import base64

from fastapi import APIRouter, Depends
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from server.models.database import ProjectRecord, ProjectTagRecord, TagRecord, UserRecord, get_async_session
from server.models.explore_list import ExploreList, ExploreListItem
from server.models.project_list import ProjectListFilter

"""
API router for explore-related endpoints.
"""

router = APIRouter()

@router.get(
    "/explore/projects", 
    status_code=200,
)
async def get_explore_projects(
    filter: ProjectListFilter,
    db: AsyncSession = Depends(get_async_session),
) -> ExploreList:
    """
    Get the list of projects that are marked as 'show in explore'.
    """
    # 1. filter public projects
    stmt = select(ProjectRecord).where(ProjectRecord.show_in_explore)

    # 2. filter keywords
    if filter.search_keyword:
        pattern = f"%{filter.search_keyword}%"
        stmt = stmt.where(ProjectRecord.name.ilike(pattern))

    # 3. filter tags
    if filter.tags:
        for tag_name in filter.tags:
            tag_subquery = select(ProjectTagRecord.project_id).join(TagRecord).where(TagRecord.name == tag_name)
            stmt = stmt.where(ProjectRecord.id.in_(tag_subquery))

    # 4. ordered by
    sort_attr = getattr(ProjectRecord, filter.ordered_by)
    stmt = stmt.order_by(desc(sort_attr))  # 默认降序，可根据需要调整

    # 5. ranging
    offset, limit = filter.ranging
    stmt = stmt.offset(offset).limit(limit - offset)

    # 6. query
    result = await db.execute(stmt)
    project_records = result.scalars().all()
    project_items = []
    for record in project_records:
        author_id = record.owner_id  # type: ignore
        # get author information
        author_record = await db.get(UserRecord, author_id)
        if not author_record:
            raise ValueError(f"Author with id {author_id} not found.")
        author_name = author_record.username  # type: ignore
        project_items.append(
            ExploreListItem(
                project_id=record.id,  # type: ignore
                project_name=record.name,  # type: ignore
                owner_id=record.owner_id,  # type: ignore
                owner_name=author_name,  # type: ignore
                created_at=int(record.created_at.timestamp() * 1000),  # type: ignore
                updated_at=int(record.updated_at.timestamp() * 1000),  # type: ignore
                thumb=base64.b64encode(record.thumb).decode("utf-8") if record.thumb else None,  # type: ignore
            )
        )
    return ExploreList(
        projects=project_items,
    )
