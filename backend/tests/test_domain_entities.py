"""测试领域实体和仓库接口"""
import pytest
from datetime import datetime
from uuid import UUID


class TestProductPackageEntity:
    """验证 ProductPackage 实体存在且定义正确"""

    def test_product_package_entity_exists(self):
        """验证 ProductPackage 实体可以导入"""
        try:
            from app.domain.entities.product_package import ProductPackage
            assert ProductPackage is not None
        except ImportError as e:
            pytest.fail(f"无法导入 ProductPackage: {e}")

    def test_product_package_entity_has_required_attributes(self):
        """验证 ProductPackage 实体有必需属性"""
        from app.domain.entities.product_package import ProductPackage
        from uuid import uuid4
        from datetime import datetime

        # 创建实例验证属性
        entity = ProductPackage(
            id=uuid4(),
            workflow_id="test-wf",
            name="Test Project",
            user_id=uuid4(),
            status="pending",
            stage="analysis",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # 验证实例有必需属性
        required_attrs = {
            'id', 'workflow_id', 'name', 'user_id', 'status',
            'stage', 'input_data', 'analysis_data', 'artifacts',
            'created_at', 'updated_at', 'completed_at'
        }

        instance_attrs = set(vars(entity).keys())
        present_attrs = required_attrs & instance_attrs

        assert present_attrs == required_attrs, \
            f"ProductPackage 缺少属性: {required_attrs - present_attrs}"


class TestProjectRepositoryInterface:
    """验证 ProjectRepository 接口定义正确"""

    def test_project_repository_interface_exists(self):
        """验证 ProjectRepository 接口可以导入"""
        try:
            from app.domain.interfaces.project_repository import ProjectRepository
            assert ProjectRepository is not None
        except ImportError as e:
            pytest.fail(f"无法导入 ProjectRepository: {e}")

    def test_project_repository_has_required_methods(self):
        """验证 ProjectRepository 接口定义了必需方法"""
        from app.domain.interfaces.project_repository import ProjectRepository, ABC
        from abc import abstractmethod

        # 检查是抽象基类
        assert issubclass(ProjectRepository, ABC), \
            "ProjectRepository 应该继承自 ABC"

        # 验证必需方法存在(抽象方法)
        required_methods = {
            'list_projects', 'get_project_by_id',
            'delete_project', 'duplicate_project', 'update_project'
        }

        interface_methods = set(dir(ProjectRepository))
        present_methods = required_methods & interface_methods

        assert len(present_methods) >= len(required_methods), \
            f"ProjectRepository 缺少方法: {required_methods - present_methods}"


class TestAssetEntity:
    """验证 Asset 实体存在且定义正确 (Story 6-2)"""

    def test_asset_entity_exists(self):
        """验证 Asset 实体可以导入"""
        try:
            from app.domain.entities.asset import Asset
            assert Asset is not None
        except ImportError as e:
            pytest.fail(f"无法导入 Asset: {e}")

    def test_asset_entity_has_required_attributes(self):
        """验证 Asset 实体有必需属性"""
        from app.domain.entities.asset import Asset
        from uuid import uuid4

        # 创建实例验证属性
        entity = Asset(
            id=uuid4(),
            title="Test Asset",
            content=None,
            url="https://example.com/asset.png",
            asset_type="image",
            prompt="A test prompt",
            width=512,
            height=512,
            metadata=None,
            created_at=datetime.utcnow(),
        )

        # 验证实例有必需属性
        required_attrs = {
            'id', 'title', 'content', 'url', 'asset_type',
            'prompt', 'width', 'height', 'metadata', 'created_at'
        }

        instance_attrs = set(vars(entity).keys())
        present_attrs = required_attrs & instance_attrs

        assert present_attrs == required_attrs, \
            f"Asset 缺少属性: {required_attrs - present_attrs}"

    def test_asset_supports_text_type_with_null_url(self):
        """验证 Asset 支持 text 类型且 url 可为 None"""
        from app.domain.entities.asset import Asset
        from uuid import uuid4

        # 创建文本资产 (url 为 None)
        asset = Asset(
            id=uuid4(),
            title="Text Asset",
            content="Some marketing copy",
            url=None,
            asset_type="text",
            prompt="Write marketing copy",
            width=0,
            height=0,
            metadata=None,
            created_at=datetime.utcnow(),
        )

        assert asset.asset_type == "text"
        assert asset.url is None
        assert asset.content == "Some marketing copy"


class TestAssetRepositoryInterface:
    """验证 IAssetRepository 接口定义正确 (Story 6-2)"""

    def test_asset_repository_interface_exists(self):
        """验证 IAssetRepository 接口可以导入"""
        try:
            from app.domain.interfaces.asset_repository import IAssetRepository
            assert IAssetRepository is not None
        except ImportError as e:
            pytest.fail(f"无法导入 IAssetRepository: {e}")

    def test_asset_repository_has_required_methods(self):
        """验证 IAssetRepository 接口定义了必需方法"""
        from app.domain.interfaces.asset_repository import IAssetRepository
        from abc import ABC

        # 检查是抽象基类
        assert issubclass(IAssetRepository, ABC), \
            "IAssetRepository 应该继承自 ABC"

        # 验证必需方法存在
        required_methods = {
            'list_assets', 'get_by_id', 'get_by_uuid',
            'update_title', 'delete'
        }

        interface_methods = set(dir(IAssetRepository))
        present_methods = required_methods & interface_methods

        assert len(present_methods) >= len(required_methods), \
            f"IAssetRepository 缺少方法: {required_methods - present_methods}"
