from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from server.lib.AuthUtils import get_admin_user
from server.models.database import (
    ProjectRecord,
    UserRecord,
    get_async_session,
)

router = APIRouter()

class ProjectInfo(BaseModel):
    id: int
    name: str
    owner_id: int
    owner_username: Optional[str]
    show_in_explore: bool
    created_at: datetime
    updated_at: datetime

@router.get("/overview", status_code=200)
async def list_projects(
    owner_username: Optional[str] = None,
    project_name: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    admin: UserRecord = Depends(get_admin_user),
    db_client: AsyncSession = Depends(get_async_session),
) -> List[ProjectInfo]:
    """List projects, supports owner username and project name filters."""
    try:
        stmt = select(ProjectRecord, UserRecord.username).join(UserRecord, ProjectRecord.owner_id == UserRecord.id)
        if owner_username:
            stmt = stmt.where(UserRecord.username.contains(owner_username))
        if project_name:
            stmt = stmt.where(ProjectRecord.name.contains(project_name))
        stmt = stmt.order_by(ProjectRecord.updated_at.desc()).limit(limit).offset(offset)
        result = await db_client.execute(stmt)
        rows = result.all()
        projects: List[ProjectInfo] = []
        for proj, owner_username in rows:
            projects.append(
                ProjectInfo(
                    id=proj.id,
                    name=proj.name,
                    owner_id=proj.owner_id,
                    owner_username=owner_username,
                    show_in_explore=proj.show_in_explore,
                    created_at=proj.created_at,
                    updated_at=proj.updated_at,
                )
            )
        return projects
    except Exception as e:
        logger.exception(f"Error listing projects: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/overview/num", status_code=200)
async def list_projects_num(
    owner_username: Optional[str] = None,
    project_name: Optional[str] = None,
    admin: UserRecord = Depends(get_admin_user),
    db_client: AsyncSession = Depends(get_async_session),
) -> int:
    """List projects, supports owner username and project name filters."""
    try:
        stmt = select(func.count()).join(UserRecord, ProjectRecord.owner_id == UserRecord.id)
        if owner_username:
            stmt = stmt.where(UserRecord.username.contains(owner_username))
        if project_name:
            stmt = stmt.where(ProjectRecord.name.contains(project_name))
        result = await db_client.execute(stmt)
        return result.scalar() or 0
    except Exception as e:
        logger.exception(f"Error listing projects: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{project_id}/set-visibility")
async def set_project_visibility(
    project_id: int,
    show: bool,
    admin: UserRecord = Depends(get_admin_user),
    db_client: AsyncSession = Depends(get_async_session),
) -> None:
    """Set project public/private (show_in_explore)."""
    try:
        project = await db_client.get(ProjectRecord, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        project.show_in_explore = show  # type: ignore
        await db_client.commit()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error setting project visibility: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    admin: UserRecord = Depends(get_admin_user),
    db_client: AsyncSession = Depends(get_async_session),
) -> None:
    """Delete a project."""
    try:
        project = await db_client.get(ProjectRecord, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        await db_client.execute(text("DELETE FROM projects WHERE id = :id"), {"id": project_id})
        await db_client.commit()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting project: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
