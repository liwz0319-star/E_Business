"""项目管理用例

包含项目列表、删除、复制、更新等业务逻辑。
"""

import math
from typing import Optional
from uuid import UUID

from fastapi import HTTPException

from app.domain.interfaces.project_repository import ProjectRepository
from app.application.dtos.project_dtos import (
    ProjectListRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectUpdateRequest,
    ProjectDuplicateResponse,
    ProjectListItem,
    entity_to_list_item,
    entity_to_response,
    entity_to_duplicate_response,
)


class ListProjectsUseCase:
    """列出项目用例"""

    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    async def execute(
        self,
        user_id: UUID,
        request: ProjectListRequest,
    ) -> ProjectListResponse:
        """执行列表查询"""
        # 验证排序字段
        valid_sort_fields = {"created_at", "name", "updated_at"}
        if request.sort_by not in valid_sort_fields:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid sort_by field. Must be one of: {valid_sort_fields}",
            )

        # 验证状态过滤
        valid_statuses = {"pending", "running", "completed", "failed"}
        if request.status and request.status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {valid_statuses}",
            )

        # 查询数据
        entities, total = await self.repository.list_projects(
            user_id=user_id,
            page=request.page,
            limit=request.limit,
            sort_by=request.sort_by,
            sort_order=request.sort_order,
            status=request.status,
            search=request.search,
        )

        # 转换为响应
        items = [entity_to_list_item(e) for e in entities]
        pages = math.ceil(total / request.limit) if total > 0 else 1

        return ProjectListResponse(
            items=items,
            total=total,
            page=request.page,
            limit=request.limit,
            pages=pages,
        )


class DeleteProjectUseCase:
    """删除项目用例"""

    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    async def execute(self, project_id: UUID, user_id: UUID) -> None:
        """执行删除 (验证所有权后硬删除)"""
        # 获取项目
        project = await self.repository.get_project_by_id(project_id)

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        # 验证所有权
        if project.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # 执行删除
        await self.repository.delete_project(project_id)


class DuplicateProjectUseCase:
    """复制项目用例"""

    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    async def execute(
        self,
        project_id: UUID,
        user_id: UUID,
    ) -> ProjectDuplicateResponse:
        """执行复制 (验证所有权后深度复制)"""
        # 获取项目
        project = await self.repository.get_project_by_id(project_id)

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        # 验证所有权
        if project.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # 执行复制
        new_entity = await self.repository.duplicate_project(project_id)

        return entity_to_duplicate_response(new_entity)


class UpdateProjectUseCase:
    """更新项目用例"""

    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    async def execute(
        self,
        project_id: UUID,
        user_id: UUID,
        request: ProjectUpdateRequest,
    ) -> ProjectResponse:
        """执行更新 (验证所有权后更新名称)"""
        # 获取项目
        project = await self.repository.get_project_by_id(project_id)

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        # 验证所有权
        if project.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        # 执行更新
        updated_entity = await self.repository.update_project(project_id, request.name)

        return entity_to_response(updated_entity)


class GetProjectUseCase:
    """获取单个项目用例"""

    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    async def execute(self, project_id: UUID, user_id: UUID) -> ProjectResponse:
        """执行获取 (验证所有权)"""
        project = await self.repository.get_project_by_id(project_id)

        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")

        # 验证所有权
        if project.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        return entity_to_response(project)
