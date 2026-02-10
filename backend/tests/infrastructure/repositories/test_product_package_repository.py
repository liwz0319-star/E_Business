import pytest
import uuid
from app.infrastructure.repositories.product_package_repository import ProductPackageRepository
from app.infrastructure.database.models import Base, ProductPackageModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="function")
def repo_and_session():
    """创建仓库和测试会话"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    repo = ProductPackageRepository(session)
    yield repo, session
    session.close()

def test_create_package(repo_and_session):
    """测试:创建新产品包"""
    repo, session = repo_and_session

    package = repo.create({
        "workflow_id": "wf-001",
        "user_id": "user-123",
        "input_data": {"image_url": "http://example.com/img.jpg", "background": "test"}
    })

    assert package.id is not None
    assert package.workflow_id == "wf-001"
    assert package.status == "pending"

def test_get_by_workflow_id(repo_and_session):
    """测试:通过 workflow_id 查询"""
    repo, session = repo_and_session

    # 创建
    repo.create({
        "workflow_id": "wf-002",
        "user_id": "user-456",
        "input_data": {"background": "test"}
    })

    # 查询
    found = repo.get_by_workflow_id("wf-002")
    assert found is not None
    assert found.workflow_id == "wf-002"

    # 不存在
    not_found = repo.get_by_workflow_id("wf-999")
    assert not_found is None

def test_update_status(repo_and_session):
    """测试:更新状态和进度"""
    repo, session = repo_and_session

    package = repo.create({
        "workflow_id": "wf-003",
        "user_id": "user-789",
        "input_data": {}
    })

    updated = repo.update_status(
        package.id,
        status="running",
        stage="copywriting",
        progress={"percentage": 25, "current_step": "generating_copywriting"}
    )

    assert updated.status == "running"
    assert updated.stage == "copywriting"
    assert updated.progress["percentage"] == 25

def test_add_artifact(repo_and_session):
    """测试:添加生成的工件"""
    repo, session = repo_and_session

    package = repo.create({
        "workflow_id": "wf-004",
        "user_id": "user-abc",
        "input_data": {}
    })

    # 添加文案
    repo.add_artifact(package.id, "copywriting", "cp-001")
    repo.add_artifact(package.id, "copywriting", "cp-002")

    updated = repo.get_by_workflow_id("wf-004")
    assert len(updated.artifacts["copywriting"]) == 2
    assert "cp-001" in updated.artifacts["copywriting"]

def test_update_status_nonexistent_package(repo_and_session):
    """测试:更新不存在的包"""
    repo, session = repo_and_session

    # 使用一个不存在的 UUID
    fake_uuid = uuid.uuid4()
    result = repo.update_status(fake_uuid, "running")
    assert result is None

def test_add_artifact_nonexistent_package(repo_and_session):
    """测试:向不存在的包添加工件"""
    repo, session = repo_and_session

    # 使用一个不存在的 UUID
    fake_uuid = uuid.uuid4()
    result = repo.add_artifact(fake_uuid, "copywriting", "cp-001")
    assert result is None
