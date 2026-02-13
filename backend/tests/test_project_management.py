"""项目管理 Use Case 单元测试

测试 ListProjectsUseCase, DeleteProjectUseCase, DuplicateProjectUseCase,
UpdateProjectUseCase, GetProjectUseCase 的业务逻辑。
"""

import pytest
from datetime import datetime
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock

from fastapi import HTTPException

from app.application.use_cases.project_management import (
    ListProjectsUseCase,
    DeleteProjectUseCase,
    DuplicateProjectUseCase,
    UpdateProjectUseCase,
    GetProjectUseCase,
)
from app.application.dtos.project_dtos import (
    ProjectListRequest,
    ProjectUpdateRequest,
)
from app.domain.entities.product_package import ProductPackage
from app.domain.interfaces.project_repository import ProjectRepository


def create_mock_entity(
    project_id: UUID = None,
    user_id: UUID = None,
    name: str = "Test Project",
    workflow_id: str = None,
    status: str = "completed",
) -> ProductPackage:
    """创建测试用实体"""
    now = datetime.utcnow()
    return ProductPackage(
        id=project_id or uuid4(),
        workflow_id=workflow_id or str(uuid4()),
        name=name,
        user_id=user_id or uuid4(),
        status=status,
        stage="copywriting",
        input_data={"product_name": "Test"},
        analysis_data={"category": "electronics"},
        artifacts={"images": [{"url": "https://example.com/image.jpg"}]},
        created_at=now,
        updated_at=now,
    )


class TestListProjectsUseCase:
    """测试 ListProjectsUseCase"""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """测试成功列出项目"""
        user_id = uuid4()
        entity = create_mock_entity(user_id=user_id)

        # Mock repository
        mock_repo = MagicMock(spec=ProjectRepository)
        mock_repo.list_projects = AsyncMock(return_value=([entity], 1))

        use_case = ListProjectsUseCase(mock_repo)
        request = ProjectListRequest(page=1, limit=20)

        result = await use_case.execute(user_id, request)

        assert result.total == 1
        assert len(result.items) == 1
        assert result.page == 1
        mock_repo.list_projects.assert_called_once()

    @pytest.mark.asyncio
    async def test_execute_with_invalid_sort_field(self):
        """测试无效排序字段"""
        user_id = uuid4()
        mock_repo = MagicMock(spec=ProjectRepository)

        use_case = ListProjectsUseCase(mock_repo)
        request = ProjectListRequest(page=1, limit=20, sort_by="invalid_field")

        with pytest.raises(HTTPException) as exc:
            await use_case.execute(user_id, request)

        assert exc.value.status_code == 400
        assert "Invalid sort_by" in exc.value.detail

    @pytest.mark.asyncio
    async def test_execute_with_invalid_status(self):
        """测试无效状态过滤"""
        user_id = uuid4()
        mock_repo = MagicMock(spec=ProjectRepository)

        use_case = ListProjectsUseCase(mock_repo)
        request = ProjectListRequest(page=1, limit=20, status="invalid_status")

        with pytest.raises(HTTPException) as exc:
            await use_case.execute(user_id, request)

        assert exc.value.status_code == 400
        assert "Invalid status" in exc.value.detail

    @pytest.mark.asyncio
    async def test_execute_empty_list(self):
        """测试空列表"""
        user_id = uuid4()
        mock_repo = MagicMock(spec=ProjectRepository)
        mock_repo.list_projects = AsyncMock(return_value=([], 0))

        use_case = ListProjectsUseCase(mock_repo)
        request = ProjectListRequest(page=1, limit=20)

        result = await use_case.execute(user_id, request)

        assert result.total == 0
        assert result.items == []
        assert result.pages == 1  # 至少一页


class TestDeleteProjectUseCase:
    """测试 DeleteProjectUseCase"""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """测试成功删除项目"""
        user_id = uuid4()
        project_id = uuid4()
        entity = create_mock_entity(project_id=project_id, user_id=user_id)

        mock_repo = MagicMock(spec=ProjectRepository)
        mock_repo.get_project_by_id = AsyncMock(return_value=entity)
        mock_repo.delete_project = AsyncMock()

        use_case = DeleteProjectUseCase(mock_repo)
        await use_case.execute(project_id, user_id)

        mock_repo.get_project_by_id.assert_called_once_with(project_id)
        mock_repo.delete_project.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_execute_project_not_found(self):
        """测试项目不存在"""
        user_id = uuid4()
        project_id = uuid4()

        mock_repo = MagicMock(spec=ProjectRepository)
        mock_repo.get_project_by_id = AsyncMock(return_value=None)

        use_case = DeleteProjectUseCase(mock_repo)

        with pytest.raises(HTTPException) as exc:
            await use_case.execute(project_id, user_id)

        assert exc.value.status_code == 404
        assert "not found" in exc.value.detail.lower()

    @pytest.mark.asyncio
    async def test_execute_access_denied(self):
        """测试访问其他用户项目"""
        user_id = uuid4()
        other_user_id = uuid4()
        project_id = uuid4()
        entity = create_mock_entity(project_id=project_id, user_id=other_user_id)

        mock_repo = MagicMock(spec=ProjectRepository)
        mock_repo.get_project_by_id = AsyncMock(return_value=entity)

        use_case = DeleteProjectUseCase(mock_repo)

        with pytest.raises(HTTPException) as exc:
            await use_case.execute(project_id, user_id)

        assert exc.value.status_code == 403
        assert "access denied" in exc.value.detail.lower()


class TestDuplicateProjectUseCase:
    """测试 DuplicateProjectUseCase"""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """测试成功复制项目"""
        user_id = uuid4()
        project_id = uuid4()
        entity = create_mock_entity(project_id=project_id, user_id=user_id)
        new_entity = create_mock_entity(user_id=user_id, name="Test Project (Copy)", status="pending")

        mock_repo = MagicMock(spec=ProjectRepository)
        mock_repo.get_project_by_id = AsyncMock(return_value=entity)
        mock_repo.duplicate_project = AsyncMock(return_value=new_entity)

        use_case = DuplicateProjectUseCase(mock_repo)
        result = await use_case.execute(project_id, user_id)

        assert result.name == "Test Project (Copy)"
        assert result.status == "pending"
        mock_repo.duplicate_project.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_execute_project_not_found(self):
        """测试项目不存在"""
        user_id = uuid4()
        project_id = uuid4()

        mock_repo = MagicMock(spec=ProjectRepository)
        mock_repo.get_project_by_id = AsyncMock(return_value=None)

        use_case = DuplicateProjectUseCase(mock_repo)

        with pytest.raises(HTTPException) as exc:
            await use_case.execute(project_id, user_id)

        assert exc.value.status_code == 404


class TestUpdateProjectUseCase:
    """测试 UpdateProjectUseCase"""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """测试成功更新项目"""
        user_id = uuid4()
        project_id = uuid4()
        entity = create_mock_entity(project_id=project_id, user_id=user_id)
        updated_entity = create_mock_entity(
            project_id=project_id,
            user_id=user_id,
            name="New Name"
        )

        mock_repo = MagicMock(spec=ProjectRepository)
        mock_repo.get_project_by_id = AsyncMock(return_value=entity)
        mock_repo.update_project = AsyncMock(return_value=updated_entity)

        use_case = UpdateProjectUseCase(mock_repo)
        request = ProjectUpdateRequest(name="New Name")
        result = await use_case.execute(project_id, user_id, request)

        assert result.name == "New Name"
        mock_repo.update_project.assert_called_once_with(project_id, "New Name")

    @pytest.mark.asyncio
    async def test_execute_access_denied(self):
        """测试访问其他用户项目"""
        user_id = uuid4()
        other_user_id = uuid4()
        project_id = uuid4()
        entity = create_mock_entity(project_id=project_id, user_id=other_user_id)

        mock_repo = MagicMock(spec=ProjectRepository)
        mock_repo.get_project_by_id = AsyncMock(return_value=entity)

        use_case = UpdateProjectUseCase(mock_repo)
        request = ProjectUpdateRequest(name="Hacked Name")

        with pytest.raises(HTTPException) as exc:
            await use_case.execute(project_id, user_id, request)

        assert exc.value.status_code == 403


class TestGetProjectUseCase:
    """测试 GetProjectUseCase"""

    @pytest.mark.asyncio
    async def test_execute_success(self):
        """测试成功获取项目"""
        user_id = uuid4()
        project_id = uuid4()
        entity = create_mock_entity(project_id=project_id, user_id=user_id)

        mock_repo = MagicMock(spec=ProjectRepository)
        mock_repo.get_project_by_id = AsyncMock(return_value=entity)

        use_case = GetProjectUseCase(mock_repo)
        result = await use_case.execute(project_id, user_id)

        assert result.id == project_id
        assert result.name == "Test Project"

    @pytest.mark.asyncio
    async def test_execute_project_not_found(self):
        """测试项目不存在"""
        user_id = uuid4()
        project_id = uuid4()

        mock_repo = MagicMock(spec=ProjectRepository)
        mock_repo.get_project_by_id = AsyncMock(return_value=None)

        use_case = GetProjectUseCase(mock_repo)

        with pytest.raises(HTTPException) as exc:
            await use_case.execute(project_id, user_id)

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_execute_access_denied(self):
        """测试访问其他用户项目"""
        user_id = uuid4()
        other_user_id = uuid4()
        project_id = uuid4()
        entity = create_mock_entity(project_id=project_id, user_id=other_user_id)

        mock_repo = MagicMock(spec=ProjectRepository)
        mock_repo.get_project_by_id = AsyncMock(return_value=entity)

        use_case = GetProjectUseCase(mock_repo)

        with pytest.raises(HTTPException) as exc:
            await use_case.execute(project_id, user_id)

        assert exc.value.status_code == 403
