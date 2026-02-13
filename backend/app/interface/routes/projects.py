"""项目管理 API 端点

提供项目列表、删除、复制、更新等操作。
"""

from typing import Annotated, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.infrastructure.database import get_async_session
from app.infrastructure.repositories.project_repository import SQLAlchemyProjectRepository
from app.interface.dependencies.auth import get_current_user
from app.application.dtos.project_dtos import (
    ProjectListRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
    ProjectDuplicateResponse,
)
from app.application.use_cases.project_management import (
    ListProjectsUseCase,
    DeleteProjectUseCase,
    DuplicateProjectUseCase,
    UpdateProjectUseCase,
    GetProjectUseCase,
)


router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_repository(
    session: Annotated[AsyncSession, Depends(get_async_session)]
) -> SQLAlchemyProjectRepository:
    """获取项目仓库依赖"""
    return SQLAlchemyProjectRepository(session)


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    repo: Annotated[SQLAlchemyProjectRepository, Depends(get_project_repository)],
    page: int = Query(1, ge=1, description="页码"),
    limit: int = Query(20, ge=1, le=100, description="每页条目数"),
    sort_by: str = Query("created_at", description="排序字段"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$", description="排序方向"),
    status: Optional[str] = Query(None, description="状态过滤"),
    search: Optional[str] = Query(None, description="搜索关键词"),
) -> ProjectListResponse:
    """
    获取当前用户的项目列表

    - **page**: 页码 (从 1 开始)
    - **limit**: 每页条目数 (最大 100)
    - **sort_by**: 排序字段 (created_at, name, updated_at)
    - **sort_order**: 排序方向 (asc, desc)
    - **status**: 状态过滤 (pending, running, completed, failed)
    - **search**: 在项目名称中搜索
    """
    request = ProjectListRequest(
        page=page,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order,
        status=status,
        search=search,
    )

    use_case = ListProjectsUseCase(repo)
    return await use_case.execute(current_user.id, request)


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    repo: Annotated[SQLAlchemyProjectRepository, Depends(get_project_repository)],
) -> ProjectResponse:
    """
    获取单个项目详情

    - **project_id**: 项目 UUID
    """
    use_case = GetProjectUseCase(repo)
    return await use_case.execute(project_id, current_user.id)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    repo: Annotated[SQLAlchemyProjectRepository, Depends(get_project_repository)],
) -> None:
    """
    删除项目 (硬删除)

    - **project_id**: 项目 UUID

    项目及其所有相关数据将被永久删除。
    """
    use_case = DeleteProjectUseCase(repo)
    await use_case.execute(project_id, current_user.id)


@router.post("/{project_id}/duplicate", response_model=ProjectDuplicateResponse)
async def duplicate_project(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    repo: Annotated[SQLAlchemyProjectRepository, Depends(get_project_repository)],
) -> ProjectDuplicateResponse:
    """
    复制项目

    - **project_id**: 要复制的项目 UUID

    创建一个新项目,复制原项目的 input_data 和 analysis_data。
    新项目状态为 pending,artifacts 为空。
    """
    use_case = DuplicateProjectUseCase(repo)
    return await use_case.execute(project_id, current_user.id)


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    request: ProjectUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    repo: Annotated[SQLAlchemyProjectRepository, Depends(get_project_repository)],
) -> ProjectResponse:
    """
    更新项目

    - **project_id**: 项目 UUID
    - **name**: 新项目名称
    """
    use_case = UpdateProjectUseCase(repo)
    return await use_case.execute(project_id, current_user.id, request)
