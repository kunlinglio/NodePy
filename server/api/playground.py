import asyncio
from typing import Optional, cast
from uuid import uuid4

from celery.app.task import Task as CeleryTask
from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException, Response, WebSocket
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.celery import celery_app
from server.config import EXAMPLE_USER_USERNAME, GUEST_USER_USERNAME
from server.interpreter.task import execute_project_task, revoke_project_task
from server.lib.AuthUtils import get_optional_user
from server.lib.ProjectLock import ProjectLock
from server.lib.StreamQueue import Status, StreamQueue
from server.lib.utils import get_project_by_id, set_project_record
from server.models.database import ProjectRecord, UserRecord, get_async_session
from server.models.exception import ProjectLockError, ProjLockIdentityError
from server.models.project import Project

from .project import TaskResponse

"""
The api for nodes running, reporting and so on,
"""
router = APIRouter()

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
    Forks the project under the GUEST user automatically.
    """
    try:
        # 1. Permission check
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
        is_example = owner_name == EXAMPLE_USER_USERNAME and project_rec.show_in_explore

        if not is_example:
            raise HTTPException(status_code=403, detail="Only public example projects can be accessed via playground")

        # 2. Convert to Project model
        project = await get_project_by_id(db_client, project_id, int(project_rec.owner_id))
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        # 3. Auto-fork the project under the GUEST user if it's an example (and not already the owner viewing it)

        guest_stmt = select(UserRecord.id).where(UserRecord.username == GUEST_USER_USERNAME)
        guest_res = await db_client.execute(guest_stmt)
        guest_user_id = guest_res.scalar_one()

        # Create a new temporary project record
        temp_project_name = f"temp-playground-{project.project_id}-{uuid4().hex}"
        temp_project = ProjectRecord(
            name=temp_project_name,
            owner_id=guest_user_id,
            workflow=project.workflow.model_dump(),
            ui_state=project.ui_state.model_dump(),
            show_in_explore=False,
            thumb=None
        )
        db_client.add(temp_project)
            
        await db_client.commit()
        await db_client.refresh(temp_project)
        
        # Return the forked project with the new temp_project_id
        fork_project_id = cast(int, temp_project.id)
        forked_project = await get_project_by_id(db_client, fork_project_id, guest_user_id)
        if forked_project is None:
            raise HTTPException(status_code=500, detail="Failed to retrieve forked project")
        return forked_project

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting playground project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

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
    response: Response,
    db_client: AsyncSession = Depends(get_async_session),
    user_record: Optional[UserRecord] = Depends(get_optional_user),
) -> TaskResponse:
    """
    Execute a project in playground mode.
    The project should already be a forked temporary project (owned by GUEST or the current user).
    Changes are saved to the temporary project before execution.
    """
    project_id = project.project_id
    try:
        async with ProjectLock(project_id=project.project_id, max_block_time=5.0, identity=None, scope="all") as lock:   
            # 1. Access Check: Must be the owner to sync/run (playground forked projects are owned by GUEST or user)
            stmt = (
                select(ProjectRecord.owner_id, UserRecord.username)
                .join(UserRecord, ProjectRecord.owner_id == UserRecord.id)
                .where(ProjectRecord.id == project_id)
            )
            result = await db_client.execute(stmt)
            row = result.first()

            if row is None:
                raise HTTPException(status_code=404, detail="Project not found")

            owner_id, owner_name = row

            if owner_name != GUEST_USER_USERNAME:
                    raise HTTPException(status_code=403, detail="Only guest-owned temporary projects can be run without login")

            # 2. Compare the topo model to decide whether to run
            old_project = await get_project_by_id(db_client, project_id, user_id=None)
            if old_project is None:
                raise HTTPException(status_code=404, detail="Project not found")

            new_topo = project.to_topo()
            old_topo = old_project.workflow.to_topo(project_id=project_id)

            # 3. Always save the current state to the temporary project
            await set_project_record(db_client, project, int(owner_id))
            await db_client.commit()

            if old_topo == new_topo:
                raise HTTPException(status_code=204, detail="No changes to execute")

            # 4. Run the task
            celery_task = cast(CeleryTask, execute_project_task)
            task = celery_task.delay(
                project_id=project_id,
                user_id=int(owner_id),
            )
            response.status_code = 202  # Accepted
            await lock.appoint_transfer_async(task.id)
            await db_client.commit()
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
                # 1. Check if task fail
                task_res = AsyncResult(task_id, app=celery_app)
                if task_res.failed():
                    # Because all exceptions are handled and reported via StreamQueue,
                    # this failed should happen very rarely.
                    if isinstance(task_res.result, Exception):
                        try:
                            raise task_res.result
                        except ProjectLockError as e:
                            logger.exception(f"Project lock error for task {task_id}: {e}")
                            await websocket.close(
                                code=4409,
                                reason=f"Project is locked, and waiting time out. This may be caused by running one project multiple times concurrently. Details: {str(e)}",
                            )
                            break  # 4409 for conflict
                        except ProjLockIdentityError as e:
                            logger.exception(f"Project lock identity error for task {task_id}: {e}")
                            await websocket.close(code=4409, reason=f"Project lock identity error: {str(e)}")
                            break
                        except Exception as e:
                            logger.exception(f"Task {task_id} failed with exception: {e}")
                            await websocket.close(code=1011, reason=f"Task failed with exception: {str(e)}")
                            break
                    else:
                        await websocket.close(code=1011, reason="Task failed.")
                        break

                # 2. await messages from both queue and websocket
                # Create tasks for both queue and websocket
                read_task = asyncio.create_task(queue.read_message(timeout_ms=5 * 1000))
                recv_task = asyncio.create_task(websocket.receive_text())

                try:
                    done, pending = await asyncio.wait({read_task, recv_task}, return_when=asyncio.FIRST_COMPLETED)
                except Exception as e:
                    read_task.cancel()
                    recv_task.cancel()
                    raise e

                # Cancel all pending tasks
                for task in pending:
                    task.cancel()

                # 3. check if websocket is disconnected
                if websocket.client_state.name != "CONNECTED":
                    await revoke_project_task(task_id)
                    break

                # 4. check if the websocket received a message from client
                if recv_task in done:
                    try:
                        message = recv_task.result()
                        # Client sent a message (usually means disconnect)
                        if message is not None:
                            await revoke_project_task(task_id)
                            await websocket.close(code=4401, reason="Client closed the connection.")
                            break
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        raise e

                # 5. check if received a message from the task
                if read_task in done:
                    try:
                        status, message = read_task.result()

                        if status == Status.TIMEOUT:
                            timeout_count += 1
                            if timeout_count >= 12 * 10:  # 10 minutes timeout for one node
                                await revoke_project_task(task_id)
                                # avoid dead loop for user provided workflow
                                await websocket.close(code=4400, reason="Task timed out.")
                                break
                            else:
                                continue
                        else:
                            # Reset timeout counter on successful message
                            timeout_count = 0

                        assert message is not None
                        await websocket.send_text(message)

                        if status.is_finished():
                            await websocket.close(code=1000, reason="Task finished.")
                            break
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        raise e
    except Exception as e:
        await revoke_project_task(task_id)
        logger.exception(f"Error processing websocket for task {task_id}: {e}")
        try:
            await websocket.close(code=1011, reason=f"Internal server error: {str(e)}")
        except Exception:
            pass
