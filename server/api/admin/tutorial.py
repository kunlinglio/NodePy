from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.lib.AuthUtils import get_admin_user
from server.models.database import TutorialReviewRecord, UserRecord, get_async_session

router = APIRouter()


class TutorialReviewStats(BaseModel):
    tutorial_id: int
    likes: int
    dislikes: int
    total: int


@router.get("/reviews", response_model=List[TutorialReviewStats])
async def get_tutorial_review_stats(
    tutorial_id: Optional[int] = None,
    limit: int = 100,
    offset: int = 0,
    admin: UserRecord = Depends(get_admin_user),
    db_client: AsyncSession = Depends(get_async_session),
) -> List[TutorialReviewStats]:
    """Return like/dislike counts grouped by tutorial id."""
    try:
        likes_case = func.sum(case((TutorialReviewRecord.review == 'like', 1), else_=0)).label('likes')
        dislikes_case = func.sum(case((TutorialReviewRecord.review == 'dislike', 1), else_=0)).label('dislikes')

        stmt = select(
            TutorialReviewRecord.tutorial_id,
            likes_case,
            dislikes_case,
        ).group_by(TutorialReviewRecord.tutorial_id).order_by(TutorialReviewRecord.tutorial_id).limit(limit).offset(offset)

        if tutorial_id is not None:
            stmt = stmt.where(TutorialReviewRecord.tutorial_id == tutorial_id)

        result = await db_client.execute(stmt)
        rows = result.all()

        stats: List[TutorialReviewStats] = []
        for row in rows:
            tid = row[0]
            likes = int(row.likes or 0)
            dislikes = int(row.dislikes or 0)
            stats.append(TutorialReviewStats(tutorial_id=tid, likes=likes, dislikes=dislikes, total=likes + dislikes))

        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
