import time
from typing import Literal

import redis.asyncio as redis
from fastapi import APIRouter, Depends
from minio import Minio
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from server.celery import celery_app
from server.config import (
    CACHE_REDIS_URL,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_URL,
)
from server.lib.AuthUtils import get_admin_user
from server.models.database import (
    UserRecord,
    get_async_session,
)

router = APIRouter()

class PostgresMetrics(BaseModel):
    status: Literal["healthy", "unhealthy"]
    latency_ms: float | None = None
    active_connections: int
    idle_connections: int
    total_connections: int
    database_size: str | None = None
    error: str | None = None

class RedisMetrics(BaseModel):
    status: Literal["healthy", "unhealthy"]
    latency_ms: float | None = None
    used_memory_human: str | None = None
    peak_memory_human: str | None = None
    fragmentation_ratio: float | None = None
    ops_per_sec: int | None = None
    hit_rate: float | None = None
    connected_clients: int | None = None
    blocked_clients: int | None = None
    version: str | None = None
    error: str | None = None

class CeleryMetrics(BaseModel):
    status: Literal["healthy", "unhealthy"]
    latency_ms: float | None = None
    active_tasks: int
    waiting_tasks: int
    revoked_tasks: int
    worker_count: int
    worker_names: list[str]
    error: str | None = None

class MinioMetrics(BaseModel):
    status: Literal["healthy", "unhealthy"]
    latency_ms: float | None = None
    bucket_count: int
    buckets: list[str]
    error: str | None = None

class SystemHealthResponse(BaseModel):
    fastapi_latency_ms: float
    postgres: PostgresMetrics
    redis: RedisMetrics
    celery: CeleryMetrics
    minio: MinioMetrics

@router.get("/overview", response_model=SystemHealthResponse)
async def get_system_health(
    admin: UserRecord = Depends(get_admin_user), db_client: AsyncSession = Depends(get_async_session)
) -> SystemHealthResponse:
    """
    Combined health check and detailed performance stats.
    Returns comprehensive metrics for FastAPI, Postgres, Redis, MinIO, and Celery.
    """
    # 1. FastAPI (Current process)
    start_total = time.perf_counter()
    fastapi_latency = None  # will be calculated at end

    # 2. PostgreSQL
    postgres_metrics = None
    try:
        start_time = time.perf_counter()
        # Get active connections and backend status
        conn_stmt = text("""
            SELECT 
                count(*) filter (where state = 'active') as active_conn,
                count(*) filter (where state = 'idle') as idle_conn,
                count(*) as total_conn
            FROM pg_stat_activity
            WHERE datname = current_database();
        """)
        res = (await db_client.execute(conn_stmt)).first()
        latency = (time.perf_counter() - start_time) * 1000

        # Get DB size
        db_size = await db_client.scalar(text("SELECT pg_size_pretty(pg_database_size(current_database()))"))

        postgres_metrics = PostgresMetrics(
            status="healthy",
            latency_ms=latency,
            active_connections=res.active_conn if res else 0,
            idle_connections=res.idle_conn if res else 0,
            total_connections=res.total_conn if res else 0,
            database_size=db_size,
        )
    except Exception as e:
        postgres_metrics = PostgresMetrics(
            status="unhealthy", active_connections=0, idle_connections=0, total_connections=0, error=str(e)
        )

    # 3. Redis
    redis_metrics = None
    try:
        r = redis.Redis.from_url(CACHE_REDIS_URL, decode_responses=True)
        start_time = time.perf_counter()
        await r.ping()  # type: ignore
        latency = (time.perf_counter() - start_time) * 1000

        info = await r.info("all")
        keyspace_hits = int(info.get("keyspace_hits", 0))
        keyspace_misses = int(info.get("keyspace_misses", 0))
        hit_rate = (
            (keyspace_hits / (keyspace_hits + keyspace_misses) * 100) if (keyspace_hits + keyspace_misses) > 0 else 0.0
        )

        redis_metrics = RedisMetrics(
            status="healthy",
            latency_ms=latency,
            used_memory_human=info.get("used_memory_human"),
            peak_memory_human=info.get("used_memory_peak_human"),
            fragmentation_ratio=info.get("mem_fragmentation_ratio"),  # type: ignore
            ops_per_sec=info.get("instantaneous_ops_per_sec"),  # type: ignore
            hit_rate=hit_rate,
            connected_clients=info.get("connected_clients"),  # type: ignore
            blocked_clients=info.get("blocked_clients"),  # type: ignore
            version=info.get("redis_version"),  # type: ignore
        )
        await r.close()
    except Exception as e:
        redis_metrics = RedisMetrics(status="unhealthy", error=str(e))

    # 4. MinIO
    minio_metrics = None
    try:
        m = Minio(endpoint=MINIO_URL, access_key=MINIO_ACCESS_KEY, secret_key=MINIO_SECRET_KEY, secure=False)
        start_time = time.perf_counter()
        buckets = m.list_buckets()
        latency = (time.perf_counter() - start_time) * 1000

        minio_metrics = MinioMetrics(
            status="healthy", latency_ms=latency, bucket_count=len(buckets), buckets=[b.name for b in buckets]
        )
    except Exception as e:
        minio_metrics = MinioMetrics(status="unhealthy", bucket_count=0, buckets=[], error=str(e))

    # 5. Celery
    celery_metrics = None
    try:
        start_time = time.perf_counter()
        i = celery_app.control.inspect()
        active = i.active() or {}
        reserved = i.reserved() or {}
        revoked = i.revoked() or {}
        latency = (time.perf_counter() - start_time) * 1000

        total_active = sum(len(tasks) for tasks in active.values())
        total_waiting = sum(len(tasks) for tasks in reserved.values())
        total_revoked = sum(len(tasks) for tasks in revoked.values())

        celery_metrics = CeleryMetrics(
            status="healthy" if active else "unhealthy",
            latency_ms=latency,
            active_tasks=total_active,
            waiting_tasks=total_waiting,
            revoked_tasks=total_revoked,
            worker_count=len(active),
            worker_names=list(active.keys()),
        )
    except Exception as e:
        celery_metrics = CeleryMetrics(
            status="unhealthy",
            active_tasks=0,
            waiting_tasks=0,
            revoked_tasks=0,
            worker_count=0,
            worker_names=[],
            error=str(e),
        )

    # compute total elapsed time for the handler
    try:
        fastapi_latency = (time.perf_counter() - start_total) * 1000
    except Exception:
        fastapi_latency = 0.0

    return SystemHealthResponse(
        fastapi_latency_ms=fastapi_latency,
        postgres=postgres_metrics,
        redis=redis_metrics,
        minio=minio_metrics,
        celery=celery_metrics,
    )
