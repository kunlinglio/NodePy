import time
from typing import Literal

import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from loguru import logger
from minio import Minio
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

from server.celery import celery_app
from server.config import (
    ADMIN_USER_USERNAME,
    CACHE_REDIS_URL,
    EXAMPLE_USER_USERNAME,
    GUEST_USER_USERNAME,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_URL,
)
from server.lib.AuthUtils import AuthUtils
from server.models.database import (
    FileRecord,
    NodeOutputRecord,
    ProjectRecord,
    TrackedSymbolRecord,
    UserRecord,
    get_async_session,
)

from .auth import LoginRequest, TokenResponse

router = APIRouter()

class SystemStatsResponse(BaseModel):
    total_users: int
    total_projects: int
    total_storage_bytes: int
    total_nodes_output: int

class UserStorageStats(BaseModel):
    user_id: int
    username: str
    storage_used: int

class StorageStats(BaseModel):
    total_storage_bytes: int
    guest_storage_bytes: int
    example_storage_bytes: int
    top_users: list[UserStorageStats]

class FinancialSymbolStats(BaseModel):
    symbol: str
    type: Literal["crypto", "stock"]
    completed: bool
    oldest_data: str

class ProjectStats(BaseModel):
    total_projects: int
    explore_projects: int
    recent_updates: int # Last 24h

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

async def verify_admin(
    request: Request,
    db_client: AsyncSession = Depends(get_async_session)
) -> UserRecord:
    """Helper to verify that the current user is an admin"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = auth_header.split(" ")[1]
    try:
        payload = AuthUtils.verify_token(token)
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = int(payload.get("sub")) # type: ignore
        user = await db_client.get(UserRecord, user_id)
        if user is None or user.username != ADMIN_USER_USERNAME: # type: ignore
            raise HTTPException(status_code=403, detail="Admin access required")
        return user
    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")


@router.post(
    "/login",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid username or password"},
        500: {"description": "Internal server error"},
    }
)
async def login(
    req: LoginRequest, 
    response: Response,
    db_client: AsyncSession = Depends(get_async_session)
) -> TokenResponse:
    """Login user and return JWT tokens"""
    try:
        # find user
        result = None
        if req.type == "email":
            result = await db_client.execute(
                select(UserRecord).where(UserRecord.email == req.identifier)
            )
        elif req.type == "username":  # username
            result = await db_client.execute(
                select(UserRecord).where(UserRecord.username == req.identifier)
            )
        else:
            assert False, "Unreachable"
        user = result.first()

        if user is None or not AuthUtils.verify_password(
            req.password, user[0].hashed_password
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password",
            )

        if user[0].username != ADMIN_USER_USERNAME:
            raise HTTPException(
                status_code=401,
                detail="Only admin user can login"
            )

        # generate tokens
        access_token = AuthUtils.create_access_token({"sub": user[0].id})
        refresh_token = AuthUtils.create_refresh_token({"sub": user[0].id})

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=7 * 24 * 60 * 60,
            path="/api/auth"
        )

        return TokenResponse(access_token=access_token)

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error logging in: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post(
    "/refresh",
    responses = {
        200: {"description": "Access token refreshed successfully"},
        401: {"description": "Invalid refresh token"},
        500: {"description": "Internal server error"},
    })
async def refresh_access_token(
    request: Request,
    db_client: AsyncSession = Depends(get_async_session),
) -> TokenResponse:
    """Use Refresh Token to get a new Access Token if access token expired"""
    # get Refresh Token from cookies
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )

    try:
        # verify Refresh Token
        payload = AuthUtils.verify_token(refresh_token)

        # ensure it's a refresh token
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=401, detail="Invalid token type"
            )

        user_id_str = payload.get("sub")

        # convert user_id from string to integer
        try:
            user_id = int(user_id_str) # type: ignore
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=401,
                detail="Invalid user ID in token"
            )

        # verify user still exists
        user = await db_client.get(UserRecord, user_id)
        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found",
            )
        elif user.username != ADMIN_USER_USERNAME: # type: ignore
            raise HTTPException(
                status_code=401,
                detail="Only admin user can refresh access token by this method"
            )

        # create Access Token
        new_access_token = AuthUtils.create_access_token({"sub": user_id})

        return TokenResponse(access_token=new_access_token)

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(
            status_code=401, detail="Invalid refresh token"
        )
    except Exception as e:
        logger.exception(f"Error refreshing token: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post(
    "/logout",
    responses={
        200: {"description": "Logged out successfully"}
    }
)
async def logout(response: Response) -> dict[str, str]:
    """Logout user by clearing the Refresh Token"""
    response.delete_cookie(key="refresh_token", path="/api/auth")
    return {"message": "Logged out successfully"}

@router.get(
    "/stats/overview", 
    status_code=200,
    responses={
        200: {"description": "System stats retrieved successfully"},
        500: {"description": "Internal server error"},
        401: {"description": "Unauthorized"},
        403: {"description": "Access denied"}
    }
)
async def get_system_stats(
    admin: UserRecord = Depends(verify_admin),
    db_client: AsyncSession = Depends(get_async_session)
) -> SystemStatsResponse:
    """
    Get system-wide overview statistics.
    Includes: total users, total projects, total storage, total nodes output.
    """
    try:
        total_users = await db_client.scalar(select(func.count(UserRecord.id)))
        total_projects = await db_client.scalar(select(func.count(ProjectRecord.id)))
        
        # Sum of file_size for non-deleted files
        total_storage = await db_client.scalar(
            select(func.sum(FileRecord.file_size)).where(~FileRecord.is_deleted)
        ) or 0
        
        total_nodes_output = await db_client.scalar(select(func.count(NodeOutputRecord.id)))

        return SystemStatsResponse(
            total_users=total_users, # type: ignore
            total_projects=total_projects, # type: ignore
            total_storage_bytes=total_storage, # type: ignore
            total_nodes_output=total_nodes_output # type: ignore
        )
    except Exception as e:
        logger.exception(f"Error getting system stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get(
    "/stats/storage",
    status_code=200,
    responses={
        200: {"description": "Storage stats retrieved successfully"},
        404: {"description": "User not found"},
        403: {"description": "Access denied"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_top_storage_users(
    limit: int = 10,
    admin: UserRecord = Depends(verify_admin),
    db_client: AsyncSession = Depends(get_async_session)
) -> StorageStats:
    """Get storage stats of whole server."""
    try:
        # get total usage
        total_storage = await db_client.scalar(
            select(func.sum(FileRecord.file_size)).where(~FileRecord.is_deleted)
        ) or 0
        # get example user usage
        example_user = await db_client.execute(
            select(UserRecord).where(UserRecord.username == EXAMPLE_USER_USERNAME)
        )
        example_user = example_user.scalars().first()
        if example_user is None:
            raise HTTPException(status_code=404, detail="Example user not found")
        example_user_id = int(example_user.id) # type: ignore
        example_user_storage = await db_client.scalar(
            select(func.sum(FileRecord.file_size)).where(FileRecord.user_id == example_user_id)
        ) or 0
        # get guest user usage
        guest_user = await db_client.execute(
            select(UserRecord).where(UserRecord.username == GUEST_USER_USERNAME)
        )
        guest_user = guest_user.scalars().first()
        if guest_user is None:
            raise HTTPException(status_code=404, detail="Guest user not found")
        guest_user_id = int(guest_user.id) # type: ignore
        guest_user_storage = await db_client.scalar(
            select(func.sum(FileRecord.file_size)).where(FileRecord.user_id == guest_user_id)
        ) or 0
        # get top users usage
        stmt = (
            select(
                UserRecord.id, 
                UserRecord.username, 
                func.sum(FileRecord.file_size).label("storage_used")
            )
            .join(FileRecord, UserRecord.id == FileRecord.user_id)
            .where(~FileRecord.is_deleted)
            .group_by(UserRecord.id)
            .order_by(func.sum(FileRecord.file_size).desc())
            .limit(limit)
        )
        result = await db_client.execute(stmt)
        top_users_storage = [
            UserStorageStats(user_id=row.id, username=row.username, storage_used=row.storage_used)
            for row in result
        ]
        return StorageStats(
            total_storage_bytes=total_storage,
            guest_storage_bytes=guest_user_storage,
            example_storage_bytes=example_user_storage,
            top_users=top_users_storage
        )
    except Exception as e:
        logger.exception(f"Error getting top storage users: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get(
    "/stats/financial",
    status_code=200,
    responses={
        200: {"description": "Financial stats retrieved successfully"},
        404: {"description": "User not found"},
        403: {"description": "Access denied"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_financial_stats(
    admin: UserRecord = Depends(verify_admin),
    db_client: AsyncSession = Depends(get_async_session)
) -> list[FinancialSymbolStats]:
    """Monitor financial data health and coverage."""
    try:
        stmt = select(
            TrackedSymbolRecord.symbol,
            TrackedSymbolRecord.data_type,
            TrackedSymbolRecord.is_history_complete,
            TrackedSymbolRecord.oldest_data_time
        )
        result = await db_client.execute(stmt)
        financial_stats = [
            FinancialSymbolStats(
                symbol=row.symbol,
                type=row.data_type,
                completed=row.is_history_complete,
                oldest_data=row.oldest_data_time
            )
            for row in result
        ]
        return financial_stats
    except Exception as e:
        logger.exception(f"Error getting financial stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get(
    "/stats/projects",
    status_code=200,
    responses={
        200: {"description": "Project stats retrieved successfully"},
        404: {"description": "User not found"},
        403: {"description": "Access denied"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def get_project_stats(
    admin: UserRecord = Depends(verify_admin),
    db_client: AsyncSession = Depends(get_async_session)
) -> ProjectStats:
    """Get project-specific statistics. For detailed project list, use `/projects/list` api"""
    try:
        total_projects = await db_client.scalar(select(func.count(ProjectRecord.id)))
        explore_projects = await db_client.scalar(
            select(func.count(ProjectRecord.id)).where(ProjectRecord.show_in_explore)
        )
        
        # Recent updates in last 24h
        from datetime import datetime, timedelta, timezone
        day_ago = datetime.now(timezone.utc) - timedelta(days=1)
        recent_updates = await db_client.scalar(
            select(func.count(ProjectRecord.id)).where(ProjectRecord.updated_at >= day_ago)
        )

        return ProjectStats(
            total_projects=total_projects, # type: ignore
            explore_projects=explore_projects, # type: ignore
            recent_updates=recent_updates # type: ignore
        )
    except Exception as e:
        logger.exception(f"Error getting project stats: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post(
    "/projects/{project_id}/toggle-explore",
    status_code=200,
    responses={
        200: {"description": "Project explore status toggled successfully"},
        404: {"description": "Project not found"},
        403: {"description": "Access denied"},
        401: {"description": "Unauthorized"},
        500: {"description": "Internal server error"}
    }
)
async def toggle_project_explore(
    project_id: int,
    show: bool,
    admin: UserRecord = Depends(verify_admin),
    db_client: AsyncSession = Depends(get_async_session)
):
    """Toggle whether a project is shown in the explore/case library."""
    try:
        project = await db_client.get(ProjectRecord, project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project.show_in_explore = show # type: ignore
        await db_client.commit()
        return {"message": f"Project explore status set to {show}"}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error toggling project explore: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/health", response_model=SystemHealthResponse)
async def get_system_health(
    admin: UserRecord = Depends(verify_admin),
    db_client: AsyncSession = Depends(get_async_session)
) -> SystemHealthResponse:
    """
    Combined health check and detailed performance stats.
    Returns comprehensive metrics for FastAPI, Postgres, Redis, MinIO, and Celery.
    """
    # 1. FastAPI (Current process)
    fastapi_latency = 0.0 # Base response time

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
            database_size=db_size
        )
    except Exception as e:
        postgres_metrics = PostgresMetrics(
            status="unhealthy",
            active_connections=0,
            idle_connections=0,
            total_connections=0,
            error=str(e)
        )

    # 3. Redis
    redis_metrics = None
    try:
        r = redis.Redis.from_url(CACHE_REDIS_URL, decode_responses=True)
        start_time = time.perf_counter()
        await r.ping() # type: ignore
        latency = (time.perf_counter() - start_time) * 1000
        
        info = await r.info("all")
        keyspace_hits = int(info.get("keyspace_hits", 0))
        keyspace_misses = int(info.get("keyspace_misses", 0))
        hit_rate = (keyspace_hits / (keyspace_hits + keyspace_misses) * 100) if (keyspace_hits + keyspace_misses) > 0 else 0.0

        redis_metrics = RedisMetrics(
            status="healthy",
            latency_ms=latency,
            used_memory_human=info.get("used_memory_human"),
            peak_memory_human=info.get("used_memory_peak_human"),
            fragmentation_ratio=info.get("mem_fragmentation_ratio"), # type: ignore
            ops_per_sec=info.get("instantaneous_ops_per_sec"), # type: ignore
            hit_rate=hit_rate,
            connected_clients=info.get("connected_clients"), # type: ignore
            blocked_clients=info.get("blocked_clients"), # type: ignore
            version=info.get("redis_version") # type: ignore
        )
        await r.close()
    except Exception as e:
        redis_metrics = RedisMetrics(status="unhealthy", error=str(e))

    # 4. MinIO
    minio_metrics = None
    try:
        m = Minio(
            endpoint=MINIO_URL,
            access_key=MINIO_ACCESS_KEY,
            secret_key=MINIO_SECRET_KEY,
            secure=False
        )
        start_time = time.perf_counter()
        buckets = m.list_buckets()
        latency = (time.perf_counter() - start_time) * 1000
        
        minio_metrics = MinioMetrics(
            status="healthy",
            latency_ms=latency,
            bucket_count=len(buckets),
            buckets=[b.name for b in buckets]
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
            worker_names=list(active.keys())
        )
    except Exception as e:
        celery_metrics = CeleryMetrics(
            status="unhealthy",
            active_tasks=0,
            waiting_tasks=0,
            revoked_tasks=0,
            worker_count=0,
            worker_names=[],
            error=str(e)
        )

    return SystemHealthResponse(
        fastapi_latency_ms=fastapi_latency,
        postgres=postgres_metrics,
        redis=redis_metrics,
        minio=minio_metrics,
        celery=celery_metrics
    )
