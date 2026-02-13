"""
Tests for Asset Repository implementation.

Validates PostgresAssetRepository methods for Story 6-2.
"""
import pytest
from datetime import datetime
from uuid import uuid4, UUID

from app.domain.entities.asset import Asset
from app.infrastructure.repositories.asset_repository import PostgresAssetRepository


class TestPostgresAssetRepository:
    """Test PostgresAssetRepository implementation."""

    @pytest.fixture
    async def repository(self, db_session):
        """Create repository instance with test session."""
        return PostgresAssetRepository(db_session)

    @pytest.fixture
    def sample_image_asset(self):
        """Create sample image asset for testing."""
        return Asset(
            id=uuid4(),
            title="Test Image",
            content=None,
            url="https://example.com/image.png",
            asset_type="image",
            prompt="A beautiful sunset",
            width=1024,
            height=768,
            metadata=None,
            user_id=uuid4(),
            workflow_id="test-workflow-1",
            created_at=datetime.utcnow(),
        )

    @pytest.fixture
    def sample_text_asset(self):
        """Create sample text asset for testing."""
        return Asset(
            id=uuid4(),
            title="Marketing Copy",
            content="Buy our amazing product!",
            url=None,
            asset_type="text",
            prompt="Write marketing copy for a product",
            width=0,
            height=0,
            metadata=None,
            user_id=uuid4(),
            workflow_id="test-workflow-2",
            created_at=datetime.utcnow(),
        )

    @pytest.mark.asyncio
    async def test_create_asset(self, repository, sample_image_asset):
        """Test creating an asset."""
        created = await repository.create(sample_image_asset, user_id=sample_image_asset.user_id)

        assert created is not None
        assert created.title == sample_image_asset.title
        assert created.asset_type == "image"

    @pytest.mark.asyncio
    async def test_get_by_id(self, repository, sample_image_asset):
        """Test getting asset by ID."""
        created = await repository.create(sample_image_asset, user_id=sample_image_asset.user_id)

        found = await repository.get_by_id(created.db_id)

        assert found is not None
        assert found.title == sample_image_asset.title

    @pytest.mark.asyncio
    async def test_get_by_uuid(self, repository, sample_image_asset):
        """Test getting asset by UUID."""
        created = await repository.create(sample_image_asset, user_id=sample_image_asset.user_id)

        found = await repository.get_by_uuid(sample_image_asset.id)

        assert found is not None
        assert found.id == sample_image_asset.id

    @pytest.mark.asyncio
    async def test_list_assets_pagination(self, repository, sample_image_asset):
        """Test listing assets with pagination."""
        user_id = sample_image_asset.user_id

        # Create multiple assets
        for i in range(5):
            asset = Asset(
                id=uuid4(),
                title=f"Asset {i}",
                content=None,
                url=f"https://example.com/image{i}.png",
                asset_type="image",
                prompt=f"Prompt {i}",
                width=512,
                height=512,
                user_id=user_id,
                created_at=datetime.utcnow(),
            )
            await repository.create(asset, user_id=user_id)

        # Test pagination
        assets, total = await repository.list_assets(user_id, page=1, limit=3)

        assert len(assets) == 3
        assert total == 5

    @pytest.mark.asyncio
    async def test_list_assets_filter_by_type(self, repository):
        """Test filtering assets by type."""
        user_id = uuid4()

        # Create image and text assets
        image_asset = Asset(
            id=uuid4(), title="Image", asset_type="image",
            prompt="test", user_id=user_id, created_at=datetime.utcnow()
        )
        text_asset = Asset(
            id=uuid4(), title="Text", asset_type="text",
            prompt="test", user_id=user_id, created_at=datetime.utcnow()
        )

        await repository.create(image_asset, user_id=user_id)
        await repository.create(text_asset, user_id=user_id)

        # Filter by image type
        assets, total = await repository.list_assets(user_id, asset_type="image")

        assert len(assets) == 1
        assert assets[0].asset_type == "image"

    @pytest.mark.asyncio
    async def test_list_assets_search(self, repository):
        """Test searching assets by title and prompt."""
        user_id = uuid4()

        asset1 = Asset(
            id=uuid4(), title="Beautiful Sunset", asset_type="image",
            prompt="A gorgeous sunset over mountains", user_id=user_id,
            width=512, height=512, created_at=datetime.utcnow()
        )
        asset2 = Asset(
            id=uuid4(), title="Ocean View", asset_type="image",
            prompt="Calm ocean waves", user_id=user_id,
            width=512, height=512, created_at=datetime.utcnow()
        )

        await repository.create(asset1, user_id=user_id)
        await repository.create(asset2, user_id=user_id)

        # Search for "sunset"
        assets, total = await repository.list_assets(user_id, search_query="sunset")

        assert len(assets) == 1
        assert "sunset" in assets[0].title.lower()

    @pytest.mark.asyncio
    async def test_update_title(self, repository, sample_image_asset):
        """Test updating asset title."""
        created = await repository.create(sample_image_asset, user_id=sample_image_asset.user_id)

        updated = await repository.update_title(created.db_id, "New Title")

        assert updated is not None
        assert updated.title == "New Title"

    @pytest.mark.asyncio
    async def test_delete_asset(self, repository, sample_image_asset):
        """Test deleting an asset."""
        created = await repository.create(sample_image_asset, user_id=sample_image_asset.user_id)
        asset_id = created.db_id

        result = await repository.delete(asset_id)

        assert result is True

        # Verify deleted
        found = await repository.get_by_id(asset_id)
        assert found is None

    @pytest.mark.asyncio
    async def test_text_asset_with_null_url(self, repository, sample_text_asset):
        """Test creating text asset with null URL."""
        created = await repository.create(sample_text_asset, user_id=sample_text_asset.user_id)

        assert created is not None
        assert created.asset_type == "text"
        assert created.url is None
        assert created.content == "Buy our amazing product!"
