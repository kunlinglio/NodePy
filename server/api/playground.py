import asyncio
from typing import Optional, cast
from uuid import uuid4

from celery.app.task import Task as CeleryTask
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.celery import celery_app
from server.config import EXAMPLE_USER_USERNAME, GUEST_USER_USERNAME
from server.interpreter.task import execute_project_task, revoke_project_task
from server.lib.AuthUtils import get_optional_user
from server.lib.StreamQueue import Status, StreamQueue
from server.lib.utils import get_project_by_id
from server.models.database import ProjectRecord, UserRecord, get_async_session
from server.models.project import Project

"""
The api for nodes running, reporting and so on,
"""
router = APIRouter()

class TaskResponse(BaseModel):
    """Response returned when a task is submitted."""
    task_id: str

@router.get(
    "/{project_id}", 
    status_code=200,
    responses = {
        200: {"description": "Graph retrieved successfully", "model": Project},
        404: {"description": "Project not found"},
        403: {"description": "Project is not a public example"},
        500: {"description": "Internal server error"},
    }
)
async def get_playground_project(
    project_id: int,
    db_client: AsyncSession = Depends(get_async_session),
    user_record: Optional[UserRecord] = Depends(get_optional_user),
) -> Project:
    """
    Get a project for playground. Only allows projects owned by NodePy-Learning that are public.
    """
    try:
        # We don't use get_project_by_id here because we want custom permission logic
        stmt = (
            select(ProjectRecord, UserRecord.username)
            .join(UserRecord, ProjectRecord.owner_id == UserRecord.id)
            .where(ProjectRecord.id == project_id)
        )
        result = await db_client.execute(stmt)
        row = result.first()

        if row is None:
            raise HTTPException(status_code=404, detail="Project not found")

        project_rec, owner_name = row

        # Security check: Must be owned by NodePy-Learning and be public
        if owner_name != EXAMPLE_USER_USERNAME or not project_rec.show_in_explore:
            # If the user is the owner, they can still view it (though they'd usually use the main API)
            if user_record is None or project_rec.owner_id != user_record.id:
                raise HTTPException(status_code=403, detail="Only public example projects can be accessed via playground")

        # Convert to Project model (same as in utils.get_project_by_id but with our own record)
        # For simplicity, we can call get_project_by_id now that we validated permission
        project = await get_project_by_id(db_client, project_id, int(project_rec.owner_id))
        if project is None:
             raise HTTPException(status_code=404, detail="Project not found")

        return project

    except HTTPException:
        raise

@router.post(
    "/sync",
    status_code=202,
    responses={
        202: {"description": "Task accepted and running", "model": TaskResponse},
        204: {"description": "No changes to execute"},
        400: {"description": "Invalid thumbnail data"},
        403: {"description": "Project is not a public example"},
        404: {"description": "Project not found"},
        500: {"description": "Internal server error"},
    },
)
async def sync_playground_project(
    project: Project,
    db_client: AsyncSession = Depends(get_async_session),
    user_record: Optional[UserRecord] = Depends(get_optional_user),
) -> TaskResponse:
    """
    Execute a project in playground mode. Does not save changes to the database.
    """
    project_id = project.project_id
    try:
        # 1. Permission check (same as GET)
        stmt = (
            select(UserRecord.username, ProjectRecord.show_in_explore)
            .join(UserRecord, ProjectRecord.owner_id == UserRecord.id)
            .where(ProjectRecord.id == project_id)
        )
        result = await db_client.execute(stmt)
        row = result.first()

        if row is None:
            raise HTTPException(status_code=404, detail="Project not found")

        owner_name, is_public = row

        if owner_name != EXAMPLE_USER_USERNAME or is_public is not True:
            if user_record is None or str(user_record.username) != str(owner_name):
                raise HTTPException(status_code=403, detail="Only public example projects can be run in playground")

        # 2. compare the topo model to decide whether to run
        old_project = await db_client.get(ProjectRecord, project_id)
        if old_project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        new_topo = project.to_topo()
        old_topo = old_project.workflow.to_topo(project_id=project_id)
        if old_topo == new_topo:
            raise HTTPException(status_code=204, detail="No changes to execute")

        # 3. Auto-fork the project under the GUEST user with a UUID
        guest_stmt = select(UserRecord.id).where(UserRecord.username == GUEST_USER_USERNAME)
        guest_res = await db_client.execute(guest_stmt)
        exec_user_id = guest_res.scalar_one()

        # Create a new temporary project record inheriting the state from the playground
        # We'll prefix the name with 'temp-playground-' to easily identify it later.
        temp_project_name = f"temp-playground-{project.project_id}-{uuid4().hex}"
        
        # Every run is an isolated temp project
        temp_project = ProjectRecord(
            name=temp_project_name,
            owner_id=exec_user_id,
            workflow=project.workflow.model_dump(),
            ui_state=project.ui_state.model_dump(),
            show_in_explore=False,
            thumb=None
        )
        db_client.add(temp_project)
            
        await db_client.commit()
        await db_client.refresh(temp_project)
        temp_project_id = temp_project.id # type: ignore

        # 4. Run the task using the temporary project id
        celery_task = cast(CeleryTask, execute_project_task)
        task = celery_task.delay(
            project_id=temp_project_id,
            user_id=exec_user_id,
        )

        return TaskResponse(task_id=task.id)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error syncing playground project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.websocket("/status/{task_id}")
async def playground_status(task_id: str, websocket: WebSocket) -> None:
    """
    WebSocket endpoint for playground task status. (Reuses logic from project.py)
    """
    await websocket.accept()
    try:
        async with StreamQueue(task_id) as queue:
            timeout_count = 0
            while True:
                task_res = AsyncResult(task_id, app=celery_app)
                if task_res.failed():
                    await websocket.close(code=1011, reason="Task failed.")
                    break

                read_task = asyncio.create_task(queue.read_message(timeout_ms=5*1000))
                recv_task = asyncio.create_task(websocket.receive_text())
                try:
                    done, pending = await asyncio.wait(
                        {read_task, recv_task},
                        return_when=asyncio.FIRST_COMPLETED
                    )
                except Exception:
                    read_task.cancel()
                    recv_task.cancel()
                    raise
                
                for t in pending:
                    t.cancel()
                
                if websocket.client_state.name != "CONNECTED":
                    await revoke_project_task(task_id)
                    break

                if recv_task in done:
                    await revoke_project_task(task_id)
                    await websocket.close(code=4401)
                    break
                
                if read_task in done:
                    status, message = read_task.result()
                    if status == Status.TIMEOUT:
                        timeout_count += 1
                        if timeout_count >= 120: 
                            await revoke_project_task(task_id)
                            await websocket.close(code=4400)
                            break
                        continue
                    
                    timeout_count = 0
                    assert message is not None
                    await websocket.send_text(message)
                    if status.is_finished():
                        await websocket.close(code=1000)
                        break
    except Exception as e:
        await revoke_project_task(task_id)
        logger.exception(f"Websocket error {task_id}: {e}")
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
