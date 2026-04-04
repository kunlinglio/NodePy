from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.lib.AuthUtils import get_admin_user
from server.models.database import (
    FinancialDataRecord,
    TrackedSymbolRecord,
    UserRecord,
    get_async_session,
)

router = APIRouter()

class FinancialSymbolStats(BaseModel):
    symbol: str
    type: Literal["crypto", "stock"]
    is_history_complete: bool
    
    # Real-time stats from financial_data table
    record_count: int
    oldest_data: int | None  # Timestamp
    latest_data: int | None  # Timestamp
    
    # Derived metrics
    data_gap_ratio: float  # 0.0 means no gaps, 1.0 means no data
    is_active: bool        # True if data was updated in the last 10 minutes

@router.get(
    "/overview",
    status_code=200,
    response_model=list[FinancialSymbolStats],
)
async def get_financial_stats(
    admin: UserRecord = Depends(get_admin_user), 
    db_client: AsyncSession = Depends(get_async_session)
) -> list[FinancialSymbolStats]:
    """
    Monitor financial data health and crawler coverage by aggregating 
    actual records and comparing with tracking status.
    """
    try:
        # 1. Get real-time aggregation from financial_data
        stats_stmt = select(
            FinancialDataRecord.symbol,
            FinancialDataRecord.data_type,
            func.count(FinancialDataRecord.id).label("count"),
            func.min(FinancialDataRecord.open_time).label("min_time"),
            func.max(FinancialDataRecord.open_time).label("max_time"),
        ).group_by(FinancialDataRecord.symbol, FinancialDataRecord.data_type)
        
        stats_result = await db_client.execute(stats_stmt)
        realtime_stats = {
            (row.symbol, row.data_type): row for row in stats_result.all()
        }

        # 2. Get tracking configuration
        tracked_stmt = select(TrackedSymbolRecord)
        tracked_result = await db_client.execute(tracked_stmt)
        tracked_records = tracked_result.scalars().all()

        now = datetime.now(timezone.utc)
        financial_stats = []

        for ts in tracked_records:
            actual = realtime_stats.get((ts.symbol, ts.data_type))
            
            count = actual.count if actual else 0
            min_t = actual.min_time if actual else None
            max_t = actual.max_time if actual else None
            
            # Calculate data gap ratio
            # Expected count = (max - min).total_minutes + 1
            gap_ratio = 1.0
            is_active = False
            if min_t and max_t and count > 0: # type: ignore
                expected_minutes = (max_t - min_t).total_seconds() / 60 + 1
                gap_ratio = max(0.0, 1.0 - (count / expected_minutes))
                is_active = (now - max_t).total_seconds() < 600 

            financial_stats.append(
                FinancialSymbolStats(
                    symbol=ts.symbol, # type: ignore
                    type=ts.data_type, # type: ignore
                    is_history_complete=ts.is_history_complete, # type: ignore
                    record_count=count, # type: ignore
                    oldest_data=int(min_t.timestamp()) if min_t else None,
                    latest_data=int(max_t.timestamp()) if max_t else None,
                    data_gap_ratio=round(gap_ratio, 4),
                    is_active=is_active
                )
            )
            
        return financial_stats

    except Exception as e:
        logger.exception(f"Error getting financial stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
