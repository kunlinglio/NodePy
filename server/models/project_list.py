from typing import Literal

from pydantic import BaseModel

"""
This file contains data models for project list representation, used in project page.
"""

class ProjectListItem(BaseModel):
    project_id: int
    project_name: str
    owner: int
    created_at: int # unix timestamp in milliseconds
    updated_at: int # unix timestamp in milliseconds
    tags: list[str]
    thumb: str | None = None  # base64 encoded thumbnail image

class ProjectList(BaseModel):
    userid: int
    projects: list[ProjectListItem]

class ProjectListFilter(BaseModel):
    tags: list[str] = []
    search_keyword: str | None = None
    ordered_by: Literal["created_at", "updated_at", "project_name", "owner"] = "updated_at"
    ranging: tuple[int, int] = (0, 20)
