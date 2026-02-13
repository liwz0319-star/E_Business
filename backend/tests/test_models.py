"""测试 ProductPackageModel 模型字段和索引"""
import pytest
from sqlalchemy import inspect, text
from app.infrastructure.database.models import ProductPackageModel, VideoAssetModel
from datetime import datetime


class TestProductPackageModelSchema:
    """验证 ProductPackageModel 架构符合故事 6-1 要求"""

    def test_model_has_name_field(self):
        """验证模型有 name 字段(nullable=False, String(255))"""
        mapper = inspect(ProductPackageModel)
        name_column = mapper.columns.get('name')

        assert name_column is not None, "ProductPackageModel 缺少 'name' 字段"
        assert name_column.type.length == 255, f"name 字段长度应该是 255, 实际是 {name_column.type.length}"
        assert not name_column.nullable, "name 字段不应该允许 NULL"

    @pytest.mark.asyncio
    async def test_model_has_created_at_index(self, db_session):
        """验证 created_at 有索引用于排序"""
        # 通过查询计划检查索引
        result = await db_session.execute(
            text("SELECT indexname FROM pg_indexes WHERE tablename = 'product_packages' AND indexname LIKE '%created_at%'")
        )
        indexes = [row[0] for row in result]

        assert any('created_at' in idx for idx in indexes), \
            "缺少 created_at 索引用于按日期排序"

    @pytest.mark.asyncio
    async def test_model_has_status_index(self, db_session):
        """验证 status 有索引用于过滤"""
        result = await db_session.execute(
            text("SELECT indexname FROM pg_indexes WHERE tablename = 'product_packages' AND indexname LIKE '%status%'")
        )
        indexes = [row[0] for row in result]

        assert any('status' in idx for idx in indexes), \
            "缺少 status 索引用于状态过滤"

    @pytest.mark.asyncio
    async def test_model_has_user_id_created_at_composite_index(self, db_session):
        """验证 (user_id, created_at) 复合索引用于用户查询"""
        result = await db_session.execute(
            text("SELECT indexname FROM pg_indexes WHERE tablename = 'product_packages' AND indexname LIKE '%user_id_created_at%'")
        )
        indexes = [row[0] for row in result]

        assert len(indexes) > 0, \
            "缺少 (user_id, created_at) 复合索引用于用户项目查询"

    def test_model_required_fields_present(self):
        """验证所有必需字段存在"""
        mapper = inspect(ProductPackageModel)
        columns = {col.name for col in mapper.columns}

        required_fields = {
            'id', 'workflow_id', 'name', 'user_id', 'status',
            'stage', 'input_data', 'analysis_data', 'artifacts',
            'created_at', 'updated_at', 'completed_at'
        }

        missing_fields = required_fields - columns
        assert not missing_fields, f"ProductPackageModel 缺少必需字段: {missing_fields}"


class TestVideoAssetModelSchema:
    """验证 VideoAssetModel 架构符合故事 6-2 要求 (Asset Gallery)"""

    def test_model_has_title_field(self):
        """VideoAssetModel 应该有 nullable title 字段"""
        mapper = inspect(VideoAssetModel)
        title_column = mapper.columns.get('title')

        assert title_column is not None, "VideoAssetModel 缺少 'title' 字段"
        assert title_column.nullable is True, "title 字段应该允许 NULL"

    def test_model_has_content_field(self):
        """VideoAssetModel 应该有 nullable content 字段用于文本资产"""
        mapper = inspect(VideoAssetModel)
        content_column = mapper.columns.get('content')

        assert content_column is not None, "VideoAssetModel 缺少 'content' 字段"
        assert content_column.nullable is True, "content 字段应该允许 NULL"

    def test_model_url_is_nullable(self):
        """VideoAssetModel url 字段应该 nullable 以支持文本资产"""
        mapper = inspect(VideoAssetModel)
        url_column = mapper.columns.get('url')

        assert url_column is not None, "VideoAssetModel 缺少 'url' 字段"
        assert url_column.nullable is True, "url 字段应该允许 NULL 以支持文本资产"

    def test_model_asset_type_is_string(self):
        """VideoAssetModel asset_type 应该是 String 类型以支持 'image', 'video', 'text'"""
        mapper = inspect(VideoAssetModel)
        asset_type_column = mapper.columns.get('asset_type')

        assert asset_type_column is not None, "VideoAssetModel 缺少 'asset_type' 字段"
        # 验证是 String 类型
        type_str = str(asset_type_column.type)
        assert "String" in type_str or "VARCHAR" in type_str, \
            f"asset_type 应该是 String 类型, 实际是 {type_str}"

    def test_model_required_fields_present(self):
        """验证所有 Gallery 所需字段存在"""
        mapper = inspect(VideoAssetModel)
        columns = {col.name for col in mapper.columns}

        required_fields = {
            'id', 'asset_uuid', 'user_id', 'workflow_id', 'asset_type',
            'url', 'prompt', 'original_prompt', 'provider',
            'width', 'height', 'metadata_json',
            'title', 'content',  # 新增字段
            'created_at', 'updated_at'
        }

        missing_fields = required_fields - columns
        assert not missing_fields, f"VideoAssetModel 缺少必需字段: {missing_fields}"
