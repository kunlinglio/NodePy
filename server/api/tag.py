from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.models.database import TagRecord, get_async_session
from server.models.tag import Tag

router = APIRouter()

"""
API router for tag-related endpoints.
"""

@router.get(
    "/list",
    status_code=200,
    responses={
        200: {"description": "List of tags retrieved successfully"},
        500: {"description": "Internal server error"}
    }
)
async def list_tags(db_client: AsyncSession = Depends(get_async_session)) -> list[Tag]:
    try:
        tag_records = await db_client.execute(select(TagRecord))
        return [Tag(id=tag.id, name=tag.name) for tag in tag_records.scalars()] # type: ignore
    except Exception as e:
        logger.error(f"Error occurred while fetching tags: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post(
    "/create",
    status_code=200,
    responses = {
        200: {"description": "Tag created successfully"},
        400: {"description": "Tag name duplicate"},
        500: {"description": "Internal server error"}
    }
)
async def create_tags(tag_name: str, db_client: AsyncSession = Depends(get_async_session)) -> None:
    try:
        # Check if tag already exists
        existing_tag = await db_client.execute(select(TagRecord).where(TagRecord.name == tag_name))
        if existing_tag.scalar():
            raise HTTPException(status_code=400, detail="Tag name already exists")

        # Create new tag
        new_tag = TagRecord(name=tag_name)
        db_client.add(new_tag)
        await db_client.commit()
    except Exception as e:
        logger.error(f"Error occurred while creating tag: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
