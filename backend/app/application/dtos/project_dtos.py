"""项目管理相关 DTOs

使用 Pydantic v2 实现 camelCase JSON 别名。
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class ProjectListRequest(BaseModel):
    """项目列表请求参数"""

    page: int = Field(default=1, ge=1, description="页码")
    limit: int = Field(default=20, ge=1, le=100, description="每页条目数")
    sort_by: str = Field(default="created_at", description="排序字段")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$", description="排序方向")
    status: Optional[str] = Field(default=None, description="状态过滤")
    search: Optional[str] = Field(default=None, description="搜索关键词")


class ProjectListItem(BaseModel):
    """项目列表项 (用于列表视图)"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: UUID
    name: str
    workflow_id: str
    status: str
    stage: str
    thumbnail_url: Optional[str] = None
    created_at: datetime


class ProjectResponse(BaseModel):
    """完整项目响应"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: UUID
    name: str
    workflow_id: str
    user_id: UUID
    status: str
    stage: str
    input_data: Optional[dict] = None
    analysis_data: Optional[dict] = None
    artifacts: dict = Field(default_factory=dict)
    thumbnail_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class ProjectListResponse(BaseModel):
    """分页项目列表响应"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    items: List[ProjectListItem]
    total: int
    page: int
    limit: int
    pages: int


class ProjectUpdateRequest(BaseModel):
    """项目更新请求"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    name: str = Field(..., min_length=1, max_length=255, description="新项目名称")


class ProjectDuplicateResponse(BaseModel):
    """项目复制响应"""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: UUID
    name: str
    workflow_id: str
    status: str
    created_at: datetime


def get_thumbnail_url(artifacts: Optional[dict]) -> Optional[str]:
    """从 artifacts 中提取缩略图 URL"""
    if not artifacts:
        return None

    images = artifacts.get("images", [])
    if not images or not isinstance(images, list) or len(images) == 0:
        return None

    first_image = images[0]
    if isinstance(first_image, dict):
        return first_image.get("url")
    elif isinstance(first_image, str):
        return first_image

    return None


def entity_to_list_item(entity, thumbnail_url: Optional[str] = None) -> ProjectListItem:
    """将实体转换为列表项"""
    return ProjectListItem(
        id=entity.id,
        name=entity.name,
        workflow_id=entity.workflow_id,
        status=entity.status,
        stage=entity.stage,
        thumbnail_url=thumbnail_url or get_thumbnail_url(entity.artifacts),
        created_at=entity.created_at,
    )


def entity_to_response(entity) -> ProjectResponse:
    """将实体转换为完整响应"""
    return ProjectResponse(
        id=entity.id,
        name=entity.name,
        workflow_id=entity.workflow_id,
        user_id=entity.user_id,
        status=entity.status,
        stage=entity.stage,
        input_data=entity.input_data,
        analysis_data=entity.analysis_data,
        artifacts=entity.artifacts,
        thumbnail_url=get_thumbnail_url(entity.artifacts),
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        completed_at=entity.completed_at,
    )


def entity_to_duplicate_response(entity) -> ProjectDuplicateResponse:
    """将实体转换为复制响应"""
    return ProjectDuplicateResponse(
        id=entity.id,
        name=entity.name,
        workflow_id=entity.workflow_id,
        status=entity.status,
        created_at=entity.created_at,
    )
