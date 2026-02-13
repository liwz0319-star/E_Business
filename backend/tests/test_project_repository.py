"""测试 ProjectRepository 实现"""
import pytest
from uuid import uuid4, UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.project_repository import SQLAlchemyProjectRepository
from app.infrastructure.database.models import ProductPackageModel


class TestSQLAlchemyProjectRepository:
    """测试 SQLAlchemyProjectRepository 实现正确性"""

    @pytest.fixture
    async def repo(self, db_session: AsyncSession):
        """创建仓库实例"""
        return SQLAlchemyProjectRepository(db_session)

    @pytest.fixture
    async def sample_project(self, db_session: AsyncSession):
        """创建示例项目"""
        user_id = uuid4()
        project = ProductPackageModel(
            workflow_id=str(uuid4()),
            name="Test Project",
            user_id=user_id,
            status="pending",
            stage="analysis",
        )
        db_session.add(project)
        await db_session.flush()
        return project

    @pytest.mark.asyncio
    async def test_list_projects_default_params(self, repo: SQLAlchemyProjectRepository, sample_project: ProductPackageModel):
        """测试默认参数列出项目"""
        entities, total = await repo.list_projects(
            user_id=sample_project.user_id,
            page=1,
            limit=20
        )

        assert total >= 1
        assert len(entities) >= 1
        assert entities[0].name == "Test Project"

    @pytest.mark.asyncio
    async def test_list_projects_with_pagination(self, repo: SQLAlchemyProjectRepository, sample_project: ProductPackageModel, db_session: AsyncSession):
        """测试分页功能"""
        user_id = sample_project.user_id

        # 创建多个项目
        for i in range(5):
            project = ProductPackageModel(
                workflow_id=str(uuid4()),
                name=f"Project {i}",
                user_id=user_id,
                status="completed",
                stage="analysis",
            )
            db_session.add(project)
        await db_session.flush()

        # 测试分页
        entities, total = await repo.list_projects(user_id=user_id, page=1, limit=2)
        assert total >= 6
        assert len(entities) == 2

        # 第二页
        entities2, _ = await repo.list_projects(user_id=user_id, page=2, limit=2)
        assert len(entities2) == 2

    @pytest.mark.asyncio
    async def test_list_projects_with_filtering(self, repo: SQLAlchemyProjectRepository, sample_project: ProductPackageModel, db_session: AsyncSession):
        """测试状态过滤"""
        user_id = sample_project.user_id

        # 创建不同状态的项目
        for status_text in ["pending", "running", "completed"]:
            project = ProductPackageModel(
                workflow_id=str(uuid4()),
                name=f"{status_text} project",
                user_id=user_id,
                status=status_text,
                stage="analysis",
            )
            db_session.add(project)
        await db_session.flush()

        # 测试过滤
        entities, total = await repo.list_projects(user_id=user_id, status="pending")
        assert total >= 1
        assert all(e.status == "pending" for e in entities)

    @pytest.mark.asyncio
    async def test_list_projects_with_search(self, repo: SQLAlchemyProjectRepository, sample_project: ProductPackageModel, db_session: AsyncSession):
        """测试名称搜索(不区分大小写)"""
        user_id = sample_project.user_id

        project = ProductPackageModel(
            workflow_id=str(uuid4()),
            name="Searchable Project Name",
            user_id=user_id,
            status="completed",
            stage="analysis",
        )
        db_session.add(project)
        await db_session.flush()

        # 测试搜索(不区分大小写)
        entities, total = await repo.list_projects(user_id=user_id, search="searchable")
        assert total >= 1
        assert len(entities) >= 1

        entities2, _ = await repo.list_projects(user_id=user_id, search="SEARCHABLE")
        assert len(entities2) >= 1  # 大写也应该匹配

    @pytest.mark.asyncio
    async def test_list_projects_with_sorting(self, repo: SQLAlchemyProjectRepository, sample_project: ProductPackageModel, db_session: AsyncSession):
        """测试排序功能"""
        user_id = sample_project.user_id

        # 创建不同时间的项目
        for i in range(3):
            project = ProductPackageModel(
                workflow_id=str(uuid4()),
                name=f"Project {i}",
                user_id=user_id,
                status="completed",
                stage="analysis",
                created_at=datetime.utcnow()
            )
            db_session.add(project)
        await db_session.flush()

        # 测试降序排序
        entities, _ = await repo.list_projects(user_id=user_id, sort_by="created_at", sort_order="desc")
        assert len(entities) >= 3

    @pytest.mark.asyncio
    async def test_get_project_by_id(self, repo: SQLAlchemyProjectRepository, sample_project: ProductPackageModel):
        """测试通过 ID 获取项目"""
        entity = await repo.get_project_by_id(sample_project.id)

        assert entity is not None
        assert entity.id == sample_project.id
        assert entity.name == "Test Project"

    @pytest.mark.asyncio
    async def test_delete_project_hard_delete(self, repo: SQLAlchemyProjectRepository, sample_project: ProductPackageModel):
        """测试硬删除项目"""
        project_id = sample_project.id

        await repo.delete_project(project_id)

        # 验证已删除
        entity = await repo.get_project_by_id(project_id)
        assert entity is None

    @pytest.mark.asyncio
    async def test_duplicate_project_deep_copy(self, repo: SQLAlchemyProjectRepository, sample_project: ProductPackageModel):
        """测试项目复制(深度复制 input_data 和 analysis_data)"""
        # 设置 input_data 和 analysis_data
        sample_project.input_data = {"product": "test"}
        sample_project.analysis_data = {"category": "electronics"}

        new_entity = await repo.duplicate_project(sample_project.id)

        assert new_entity.id != sample_project.id
        assert new_entity.workflow_id != sample_project.workflow_id
        assert new_entity.name == f"{sample_project.name} (Copy)"
        assert new_entity.status == "pending"
        assert new_entity.stage == "analysis"
        assert new_entity.input_data == sample_project.input_data
        assert new_entity.analysis_data == sample_project.analysis_data
        assert new_entity.artifacts == {}

    @pytest.mark.asyncio
    async def test_update_project_rename(self, repo: SQLAlchemyProjectRepository, sample_project: ProductPackageModel):
        """测试项目重命名"""
        new_name = "Updated Project Name"

        updated_entity = await repo.update_project(sample_project.id, new_name)

        assert updated_entity.id == sample_project.id
        assert updated_entity.name == new_name
