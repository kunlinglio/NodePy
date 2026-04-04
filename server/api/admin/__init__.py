from fastapi import APIRouter

from .auth import router as auth_router
from .health import router as health_router
from .user import router as user_router
from .financial import router as financial_router
from .project import router as project_router
from .storage import router as storage_router
from .tutorial import router as tutorial_router

"""
API router for admin-related endpoints.
"""

# Create main API router
router = APIRouter()

# Include sub-routers
router.include_router(auth_router, prefix="/auth")
router.include_router(health_router, prefix="/health")
router.include_router(user_router, prefix="/users")
router.include_router(financial_router, prefix="/financial")
router.include_router(project_router, prefix="/projects")
router.include_router(storage_router, prefix="/storage")
router.include_router(tutorial_router, prefix="/tutorials")

__all__ = ["router"]
