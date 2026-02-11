"""
Product Package Repository Tests (Async)
"""

import pytest
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.repositories.product_package_repository import ProductPackageRepository
from app.infrastructure.database.models import ProductPackageModel


@pytest.mark.asyncio
class TestProductPackageRepository:
    """测试 ProductPackageRepository 异步操作"""

    async def test_create_package(self, async_session: AsyncSession):
        """测试创建产品包"""
        repo = ProductPackageRepository(async_session)

        data = {
            "workflow_id": str(uuid4()),
            "user_id": uuid4(),
            "status": "pending",
            "stage": "init",
            "input_data": {"test": "data"},
        }

        package = await repo.create(data)

        assert package.id is not None
        assert package.workflow_id == data["workflow_id"]
        assert package.status == "pending"
        assert package.stage == "init"

    async def test_get_by_workflow_id(self, async_session: AsyncSession):
        """测试通过 workflow_id 查询"""
        repo = ProductPackageRepository(async_session)

        workflow_id = str(uuid4())
        user_id = uuid4()

        # 创建包
        await repo.create({
            "workflow_id": workflow_id,
            "user_id": user_id,
            "status": "running",
            "stage": "analysis",
        })

        # 查询
        package = await repo.get_by_workflow_id(workflow_id)

        assert package is not None
        assert package.workflow_id == workflow_id
        assert package.user_id == user_id

    async def test_update_status(self, async_session: AsyncSession):
        """测试更新状态"""
        repo = ProductPackageRepository(async_session)

        # 创建包
        package = await repo.create({
            "workflow_id": str(uuid4()),
            "user_id": uuid4(),
            "status": "running",
            "stage": "analysis",
        })

        # 更新状态
        updated = await repo.update_status(
            package_id=package.id,
            status="completed",
            stage="done",
            progress={"percentage": 100, "current_step": "completed"},
        )

        assert updated.status == "completed"
        assert updated.stage == "done"
        assert updated.progress["percentage"] == 100
        assert updated.completed_at is not None

    async def test_add_artifact(self, async_session: AsyncSession):
        """测试添加工件引用"""
        repo = ProductPackageRepository(async_session)

        package = await repo.create({
            "workflow_id": str(uuid4()),
            "user_id": uuid4(),
            "status": "running",
            "stage": "analysis",
        })

        # 添加工件
        updated = await repo.add_artifact(
            package_id=package.id,
            artifact_type="images",
            artifact_id="img-123",
        )

        assert "images" in updated.artifacts
        assert "img-123" in updated.artifacts["images"]

    async def test_update_approval(self, async_session: AsyncSession):
        """测试更新审批状态"""
        repo = ProductPackageRepository(async_session)

        package = await repo.create({
            "workflow_id": str(uuid4()),
            "user_id": uuid4(),
            "status": "approval_required",
            "stage": "approval",
        })

        # 审批通过
        updated = await repo.update_approval(
            package_id=package.id,
            approval_status="approved",
        )

        assert updated.approval_status == "approved"

    async def test_update_qa_report(self, async_session: AsyncSession):
        """测试更新 QA 报告"""
        repo = ProductPackageRepository(async_session)

        package = await repo.create({
            "workflow_id": str(uuid4()),
            "user_id": uuid4(),
            "status": "running",
            "stage": "qa_review",
        })

        qa_report = {
            "score": 0.85,
            "passed": True,
            "issues": [],
            "suggestions": ["Consider A/B testing"],
        }

        updated = await repo.update_qa_report(
            package_id=package.id,
            qa_report=qa_report,
        )

        assert updated.qa_report == qa_report
