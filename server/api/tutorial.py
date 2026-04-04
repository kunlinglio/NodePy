
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.lib.AuthUtils import get_optional_user
from server.models.database import TutorialReviewRecord, UserRecord, get_async_session

router = APIRouter()

"""
API router for tutorial-related endpoints.
"""

router.post(
    "/review/{tutorial_id}",
    status_code=200,
    responses={
        200: {"description": "Review tutorial successfully"},
        500: {"description": "Internal server error"},
    },
)
async def review_tutorial(
    tutorial_id: int,
    review: Literal["like", "dislike"],
    db_client: AsyncSession = Depends(get_async_session),
    user_record: UserRecord = Depends(get_optional_user),
) -> None:
    user_id = int(user_record.id) if user_record else None # type: ignore
    try:
        # check if the user has already reviewed this tutorial
        existing_review = await db_client.execute(
            select(TutorialReviewRecord).where(
                TutorialReviewRecord.tutorial_id == tutorial_id,
                TutorialReviewRecord.user_id == user_id,
            )
        )
        existing_review = existing_review.scalars().first()

        if existing_review:
            # update the existing review
            existing_review.review = review # type: ignore
            await db_client.commit()
        else:
            # create a new review
            new_review = TutorialReviewRecord(
                tutorial_id=tutorial_id,
                user_id=user_id,
                review=review,
            )
            db_client.add(new_review)
            await db_client.commit()
    except Exception as e:
        logger.error(f"Error occurred while review tutorial: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


router.get(
    "/review/{tutorial_id}",
    status_code=200,
    responses={
        200: {"description": "Get tutorial reviews successfully"},
        500: {"description": "Internal server error"},
    },
)
async def get_tutorial_reviews(
    tutorial_id: int,
    db_client: AsyncSession = Depends(get_async_session),
) -> tuple[int, int]:
    """Returns (like_count, dislike_count) for the given tutorial_id"""
    try:
        like = await db_client.execute(
            select(func.count()).where(
                TutorialReviewRecord.tutorial_id == tutorial_id,
                TutorialReviewRecord.review == "like",
            )
        )
        like_count = like.scalar() or 0
        dislike = await db_client.execute(
            select(func.count()).where(
                TutorialReviewRecord.tutorial_id == tutorial_id,
                TutorialReviewRecord.review == "dislike",
            )
        )
        dislike_count = dislike.scalar() or 0
        return like_count, dislike_count
    except Exception as e:
        logger.error(f"Error occurred while review tutorial: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
