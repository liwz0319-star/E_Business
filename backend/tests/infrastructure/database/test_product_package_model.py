import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.database.models import Base, ProductPackageModel

@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_product_package_minimal(db_session):
    """测试:创建最小产品包记录"""
    package = ProductPackageModel(
        workflow_id="test-wf-001",
        status="pending",
        stage="analysis",
        user_id="test-user"
    )
    db_session.add(package)
    db_session.commit()
    db_session.refresh(package)

    assert package.id is not None
    assert package.workflow_id == "test-wf-001"
    assert package.status == "pending"
    assert package.stage == "analysis"
    assert package.created_at is not None

def test_product_package_status_transitions(db_session):
    """测试:状态机转换 (pending -> running -> completed)"""
    package = ProductPackageModel(
        workflow_id="test-wf-002",
        status="pending",
        stage="analysis",
        user_id="test-user"
    )
    db_session.add(package)
    db_session.commit()

    # pending -> running
    package.status = "running"
    db_session.commit()
    db_session.refresh(package)
    assert package.status == "running"

    # running -> completed
    package.status = "completed"
    db_session.commit()
    db_session.refresh(package)
    assert package.status == "completed"

def test_product_package_with_analysis_data(db_session):
    """测试:保存产品分析结果"""
    package = ProductPackageModel(
        workflow_id="test-wf-003",
        status="running",
        stage="copywriting",
        user_id="test-user",
        analysis_data={
            "product_category": "electronics",
            "target_audience": "young professionals",
            "key_selling_points": ["portable", "high capacity"]
        }
    )
    db_session.add(package)
    db_session.commit()
    db_session.refresh(package)

    assert package.analysis_data["product_category"] == "electronics"
    assert len(package.analysis_data["key_selling_points"]) == 2

def test_product_package_artifacts_tracking(db_session):
    """测试:跟踪生成的工件 (文案/图片/视频)"""
    package = ProductPackageModel(
        workflow_id="test-wf-004",
        status="running",
        stage="image_generation",
        user_id="test-user"
    )
    db_session.add(package)
    db_session.commit()

    # 添加文案工件
    package.artifacts = {
        "copywriting": ["cp-001", "cp-002"],
        "images": ["img-001", "img-002", "img-003"],
        "video": None  # 尚未生成
    }
    db_session.commit()
    db_session.refresh(package)

    assert len(package.artifacts["copywriting"]) == 2
    assert len(package.artifacts["images"]) == 3
    assert package.artifacts["video"] is None
