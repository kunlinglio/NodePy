import datetime
import time

from loguru import logger

from server.celery import celery_app
from server.config import (
    ADMIN_USER_EMAIL,
    ADMIN_USER_PASSWORD,
    ADMIN_USER_USERNAME,
    EXAMPLE_USER_EMAIL,
    EXAMPLE_USER_USERNAME,
    GUEST_PROJECT_EXPIRED_TIME_SEC,
    GUEST_USER_EMAIL,
    GUEST_USER_USERNAME,
)
from server.lib.ProjectLock import ProjectLock
from server.models.database import DatabaseTransaction, ProjectRecord, UserRecord, get_session


def initialize_default_users():
    from server.lib.AuthUtils import AuthUtils
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

@celery_app.task(name="server.lib.default_user.cleanup_guest_temp_project")
def cleanup_guest_temp_project() -> None:
    """
    Periodic delete expired temp project of guest user.
    """
    start_time = time.perf_counter()
    db_client = next(get_session())
    try:
        guest_user_rcd = db_client.query(UserRecord).filter_by(username=GUEST_USER_USERNAME).first()
        if guest_user_rcd is None:
            logger.info("Guest user not found, skipping cleanup")
            return
        guest_user_id = int(guest_user_rcd.id) # type: ignore
        
        guest_projects = db_client.query(ProjectRecord).filter_by(owner_id=guest_user_id)
        for project in guest_projects:
            update_time = project.updated_at
            if time.time() - datetime.datetime.timestamp(update_time) > GUEST_PROJECT_EXPIRED_TIME_SEC: # type: ignore
                project_id = int(project.id) # type: ignore
                with ProjectLock(project_id = project_id, max_block_time = 5.0, identity = None, scope="all"):
                    db_client.delete(project)
                logger.info(f"Expired project deleted: {project.name}")
            else:
                logger.info(f"Project is still valid: {project.name}")
    except Exception as e:
        logger.error(f"Error occurred while cleaning up guest temp projects: {e}")
    finally:
        db_client.close()
        logger.info(f"Finished cleaning up guest temp projects in {time.perf_counter() - start_time:.2f} seconds")
