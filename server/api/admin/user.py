from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from server.lib.AuthUtils import AuthUtils, get_admin_user
from server.models.database import (
    UserRecord,
    get_async_session,
)

router = APIRouter()
class UserInfo(BaseModel):
    id: int
    username: str
    email: str
    file_total_space: int
    created_at: datetime

class ResetPasswordRequest(BaseModel):
    new_password: str

@router.get(
    "/list", status_code=200, responses={400: {"description": "Bad request"}, 401: {"description": "Unauthorized"}}
)
async def list_users(
    username: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    admin: UserRecord = Depends(get_admin_user),
    db_client: AsyncSession = Depends(get_async_session),
) -> List[UserInfo]:
    """List all registered users, supports username search."""
    try:
        stmt = select(UserRecord).order_by(UserRecord.id).limit(limit).offset(offset)
        if username:
            stmt = (
                select(UserRecord)
                .where(UserRecord.username.contains(username))
                .order_by(UserRecord.id)
                .limit(limit)
                .offset(offset)
            )
        result = await db_client.execute(stmt)
        users = result.scalars().all()
        return [
            UserInfo(
                id=u.id, # type: ignore
                username=u.username, # type: ignore
                email=u.email, # type: ignore
                file_total_space=u.file_total_space, # type: ignore
                created_at=u.created_at, # type: ignore
            )
            for u in users
        ]
    except Exception as e:
        logger.exception(f"Error listing users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get(
    "/list/num", status_code=200, responses={400: {"description": "Bad request"}, 401: {"description": "Unauthorized"}}
)
async def list_users_num(
    username: Optional[str] = None,
    admin: UserRecord = Depends(get_admin_user),
    db_client: AsyncSession = Depends(get_async_session),
) -> int:
    """Return the number of registered users, supports username search."""
    try:
        stmt = select(func.count()).select_from(UserRecord)
        if username:
            stmt = stmt.where(UserRecord.username.contains(username))
        result = await db_client.execute(stmt)
        return result.scalar() or 0
    except Exception as e:
        logger.exception(f"Error counting users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    admin: UserRecord = Depends(get_admin_user),
    db_client: AsyncSession = Depends(get_async_session),
) -> None:
    """Delete a user account."""
    try:
        user = await db_client.get(UserRecord, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # delete user (cascades via FK ondelete)
        await db_client.execute(text("DELETE FROM users WHERE id = :id"), {"id": user_id})
        await db_client.commit()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting user: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    req: ResetPasswordRequest,
    admin: UserRecord = Depends(get_admin_user),
    db_client: AsyncSession = Depends(get_async_session),
) -> None:
    """Reset a user's password to a provided new password."""
    try:
        if not AuthUtils.is_valid_password(req.new_password):
            raise HTTPException(status_code=400, detail="Password does not meet requirements")
        user = await db_client.get(UserRecord, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.hashed_password = AuthUtils.hash_password(req.new_password) # type: ignore
        await db_client.commit()
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error resetting password: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
