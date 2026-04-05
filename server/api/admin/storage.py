from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from minio import Minio
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.config import (
    EXAMPLE_USER_USERNAME,
    GUEST_USER_USERNAME,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_URL,
)
from server.lib.AuthUtils import get_admin_user
from server.lib.FileManager import FileManager
from server.models.database import (
    FileRecord,
    UserRecord,
    get_async_session,
)

router = APIRouter()

class StorageStats(BaseModel):
    total_storage_bytes: int
    guest_storage_bytes: int
    example_storage_bytes: int

class FileInfo(BaseModel):
    id: int
    filename: str
    format: str
    user_id: int
    project_id: Optional[int]
    file_size: int
    last_modify_time: datetime
    is_deleted: bool


@router.get(
    "/overview",
    status_code=200,
    responses={
        200: {"description": "Storage stats retrieved successfully"},
        404: {"description": "User not found"},
        403: {"description": "Access denied"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"},
    },
)
async def get_overview(
    admin: UserRecord = Depends(get_admin_user), db_client: AsyncSession = Depends(get_async_session)
) -> StorageStats:
    """Get storage stats of whole server."""
    try:
        # get total usage
        total_storage = (
            await db_client.scalar(select(func.sum(FileRecord.file_size)).where(~FileRecord.is_deleted)) or 0
        )
        # get example user usage
        example_user = await db_client.execute(select(UserRecord).where(UserRecord.username == EXAMPLE_USER_USERNAME))
        example_user = example_user.scalars().first()
        if example_user is None:
            raise HTTPException(status_code=404, detail="Example user not found")
        example_user_id = int(example_user.id)  # type: ignore
        example_user_storage = (
            await db_client.scalar(select(func.sum(FileRecord.file_size)).where(FileRecord.user_id == example_user_id))
            or 0
        )
        # get guest user usage
        guest_user = await db_client.execute(select(UserRecord).where(UserRecord.username == GUEST_USER_USERNAME))
        guest_user = guest_user.scalars().first()
        if guest_user is None:
            raise HTTPException(status_code=404, detail="Guest user not found")
        guest_user_id = int(guest_user.id)  # type: ignore
        guest_user_storage = (
            await db_client.scalar(select(func.sum(FileRecord.file_size)).where(FileRecord.user_id == guest_user_id))
            or 0
        )
        return StorageStats(
            total_storage_bytes=total_storage,
            guest_storage_bytes=guest_user_storage,
            example_storage_bytes=example_user_storage,
        )
    except Exception as e:
        logger.exception(f"Error getting top storage users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/user/{user_id}")
async def get_user_storage(
    user_id: int,
    admin: UserRecord = Depends(get_admin_user),
    db_client: AsyncSession = Depends(get_async_session),
):
    """Return a user's storage quota and usage details."""
    try:
        user = await db_client.get(UserRecord, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        fm = FileManager(async_db_session=db_client)
        used = await fm._cal_user_occupy_async(user_id)
        total = int(user.file_total_space)  # type: ignore
        return {
            "user_id": user_id,
            "username": user.username,
            "used_bytes": used,
            "total_bytes": total,
            "used_percentage": (used / total * 100) if total > 0 else 0,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting user storage: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/files", status_code=200)
async def list_files(
    filename: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    admin: UserRecord = Depends(get_admin_user),
    db_client: AsyncSession = Depends(get_async_session),
) -> List[FileInfo]:
    """List files, supports filename search."""
    try:
        stmt = (
            select(FileRecord)
            .where(FileRecord.is_deleted.is_(False))
            .order_by(FileRecord.last_modify_time.desc())
            .limit(limit)
            .offset(offset)
        )
        if filename:
            stmt = (
                select(FileRecord)
                .where(FileRecord.is_deleted.is_(False), FileRecord.filename.contains(filename))
                .order_by(FileRecord.last_modify_time.desc())
                .limit(limit)
                .offset(offset)
            )
        result = await db_client.execute(stmt)
        files = result.scalars().all()
        return [
            FileInfo(
                id=f.id, # type: ignore
                filename=f.filename, # type: ignore
                format=f.format, # type: ignore
                user_id=f.user_id, # type: ignore
                project_id=f.project_id, # type: ignore 
                file_size=f.file_size, # type: ignore
                last_modify_time=f.last_modify_time, # type: ignore
                is_deleted=f.is_deleted, # type: ignore
            )
            for f in files
        ]
    except Exception as e:
        logger.exception(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/files/num", status_code=200)
async def list_files_num(
    filename: Optional[str] = None,
    admin: UserRecord = Depends(get_admin_user),
    db_client: AsyncSession = Depends(get_async_session),
) -> int:
    """Return the number of files, supports filename search."""
    try:
        stmt = select(func.count()).where(FileRecord.is_deleted.is_(False))
        if filename:
            stmt = stmt.where(FileRecord.filename.contains(filename))
        result = await db_client.execute(stmt)
        return result.scalar() or 0
    except Exception as e:
        logger.exception(f"Error listing files: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/files/{file_id}/preview")
async def preview_file(
    file_id: int,
    admin: UserRecord = Depends(get_admin_user),
    db_client: AsyncSession = Depends(get_async_session),
):
    """Return a presigned URL to preview a file stored in MinIO."""
    try:
        file = await db_client.get(FileRecord, file_id)
        if not file or file.is_deleted: # type: ignore
            raise HTTPException(status_code=404, detail="File not found")
        m = Minio(
            endpoint=MINIO_URL,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False,
        )
        url = m.presigned_get_object("nodepy-files", file.file_key, expires=timedelta(minutes=15)) # type: ignore
        return {"url": url}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error generating file preview URL: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/files/{file_id}")
async def delete_file(
    file_id: int,
    admin: UserRecord = Depends(get_admin_user),
    db_client: AsyncSession = Depends(get_async_session),
):
    """Soft-delete a file record and attempt to remove from MinIO."""
    try:
        file = await db_client.get(FileRecord, file_id)
        if not file:
            raise HTTPException(status_code=404, detail="File not found")
        file.is_deleted = True  # type: ignore
        await db_client.commit()
        try:
            m = Minio(endpoint=MINIO_URL, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
            m.remove_object("nodepy-files", file.file_key) # type: ignore
        except Exception:
            # ignore MinIO deletion errors; DB is authoritative
            pass
        return {"message": "File deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting file: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
