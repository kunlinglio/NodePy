import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger

from server.config import (
    ADMIN_USER_EMAIL,
    ADMIN_USER_PASSWORD,
    ADMIN_USER_USERNAME,
    EXAMPLE_USER_EMAIL,
    EXAMPLE_USER_USERNAME,
    GUEST_USER_EMAIL,
    GUEST_USER_USERNAME,
)
from server.lib.AuthUtils import AuthUtils
from server.lib.ExampleProjManager import initialize_example_projects
from server.lib.FinancialDataManager import initialize_core_symbols

# from server.lib.ApiLoggerMiddleware import ApiLoggerMiddleware
from server.models.database import DatabaseTransaction, UserRecord, init_database

from .api import router


def initialize_default_users():
    with DatabaseTransaction() as db:
        # Ensure official user exists
        user = db.query(UserRecord).filter_by(username=EXAMPLE_USER_USERNAME).first()
        if not user:
            logger.info(f"Creating official learning user: {EXAMPLE_USER_USERNAME}")
            user = UserRecord(
                username=EXAMPLE_USER_USERNAME,
                email=EXAMPLE_USER_EMAIL,
                hashed_password=None,
                file_total_space=10 * 1024 * 1024 * 1024 * 1024,  # 10 TB
            )
            db.add(user)
            db.flush()

        # Ensure Guest user exists
        guest_user = db.query(UserRecord).filter_by(username=GUEST_USER_USERNAME).first()
        if not guest_user:
            logger.info(f"Creating guest user for playground: {GUEST_USER_USERNAME}")
            guest_user = UserRecord(
                username=GUEST_USER_USERNAME,
                email=GUEST_USER_EMAIL,
                hashed_password=None,
                file_total_space=100 * 1024 * 1024 * 1024,  # 100 GB for guest pool
            )
            db.add(guest_user)
            db.flush()

        # Ensure Admin user exists
        admin_user = db.query(UserRecord).filter_by(username=ADMIN_USER_USERNAME).first()
        if not admin_user:
            logger.info(f"Creating admin user: {ADMIN_USER_USERNAME}")
            admin_user = UserRecord(
                username=ADMIN_USER_USERNAME,
                email=ADMIN_USER_EMAIL,
                hashed_password=AuthUtils.hash_password(ADMIN_USER_PASSWORD),
                file_total_space=0,
            )
            db.add(admin_user)
            db.flush()


app = FastAPI(title="NodePy API", separate_input_output_schemas=False)
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# add debug middleware
# if DEBUG:
#     app.add_middleware(ApiLoggerMiddleware)

# init database
init_database()

# init financial data for core symbols
initialize_core_symbols()

# register default users
initialize_default_users()

# init example projects for learning user
initialize_example_projects()

# Include API routes
app.include_router(router, prefix="/api")

# Static files directory
# In container: /nodepy/static (mapped from host client/dist via mount or COPY)
dist_dir = Path("/nodepy/static")
if dist_dir.exists():
    app.mount("/static", StaticFiles(directory=str(dist_dir), html=True), name="frontend")

# SPA fallback for all other routes
@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    index_path = os.path.join(dist_dir, "index.html")
    return FileResponse(index_path)
