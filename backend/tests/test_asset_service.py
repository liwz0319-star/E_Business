"""
Tests for Asset Service and DTOs.

Validates AssetService and GalleryAssetDTO for Story 6-2.
"""
import pytest
from datetime import datetime
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock

from app.application.dtos.asset_dtos import GalleryAssetDTO, AssetListResponseDTO
from app.application.services.asset_service import AssetService
from app.domain.entities.asset import Asset


class TestGalleryAssetDTO:
    """Test GalleryAssetDTO serialization and field mapping."""

    def test_dto_has_required_fields(self):
        """GalleryAssetDTO should have all frontend-required fields."""
        dto = GalleryAssetDTO(
            id=str(uuid4()),
            title="Test Asset",
            type="Product Images",
            tag="IMG",
            meta="High-res Render • 1024x1024",
            url="https://example.com/asset.png",
            content=None,
            is_vertical=False,
            is_text=False,
            duration=None,
            created_at=datetime.utcnow(),
        )

        assert dto.id is not None
        assert dto.title == "Test Asset"
        assert dto.type == "Product Images"
        assert dto.tag == "IMG"
        assert dto.is_vertical is False
        assert dto.is_text is False

    def test_dto_camel_case_alias(self):
        """GalleryAssetDTO should serialize to camelCase."""
        dto = GalleryAssetDTO(
            id=str(uuid4()),
            title="Test",
            type="Ad Videos",
            tag="VIDEO",
            meta="9:16 Vertical",
            url="https://example.com/video.mp4",
            content=None,
            is_vertical=True,
            is_text=False,
            duration="0:15",
            created_at=datetime.utcnow(),
        )

        json_dict = dto.model_dump(by_alias=True)

        assert "isVertical" in json_dict
        assert "isText" in json_dict
        assert "createdAt" in json_dict

    def test_dto_text_asset_fields(self):
        """GalleryAssetDTO should handle text asset fields."""
        dto = GalleryAssetDTO(
            id=str(uuid4()),
            title="Marketing Copy",
            type="Marketing Copy",
            tag="COPY",
            meta="Generated copy",
            url=None,
            content="Buy our amazing product!",
            is_vertical=False,
            is_text=True,
            duration=None,
            created_at=datetime.utcnow(),
        )

        assert dto.is_text is True
        assert dto.url is None
        assert dto.content == "Buy our amazing product!"


class TestAssetListResponseDTO:
    """Test AssetListResponseDTO with pagination."""

    def test_response_has_pagination_fields(self):
        """AssetListResponseDTO should have pagination fields."""
        dto = AssetListResponseDTO(
            items=[],
            total=100,
            page=1,
            limit=20,
            pages=5,
        )

        assert dto.total == 100
        assert dto.page == 1
        assert dto.limit == 20
        assert dto.pages == 5


class TestAssetService:
    """Test AssetService business logic."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock repository."""
        repo = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_repository):
        """Create service with mock repository."""
        return AssetService(mock_repository)

    @pytest.fixture
    def sample_asset(self):
        """Create sample asset entity."""
        return Asset(
            id=uuid4(),
            db_id=1,
            title="Test Image",
            content=None,
            url="https://example.com/image.png",
            asset_type="image",
            prompt="A beautiful sunset",
            width=1024,
            height=768,
            metadata=None,
            user_id=uuid4(),
            created_at=datetime.utcnow(),
        )

    @pytest.mark.asyncio
    async def test_get_gallery_assets_returns_dtos(self, service, mock_repository, sample_asset):
        """get_gallery_assets should return list of GalleryAssetDTO."""
        user_id = uuid4()
        mock_repository.list_assets.return_value = ([sample_asset], 1)

        result = await service.get_gallery_assets(user_id=user_id)

        assert isinstance(result, AssetListResponseDTO)
        assert len(result.items) == 1
        assert isinstance(result.items[0], GalleryAssetDTO)

    @pytest.mark.asyncio
    async def test_get_gallery_assets_maps_type_correctly(self, service, mock_repository):
        """get_gallery_assets should map asset_type to frontend categories."""
        user_id = uuid4()

        # Test image type
        image_asset = Asset(
            id=uuid4(), db_id=1, title="Image", asset_type="image",
            prompt="test", width=512, height=512, user_id=user_id,
            created_at=datetime.utcnow()
        )
        mock_repository.list_assets.return_value = ([image_asset], 1)

        result = await service.get_gallery_assets(user_id=user_id)

        assert result.items[0].type == "Product Images"
        assert result.items[0].tag == "IMG"
        assert result.items[0].is_text is False

    @pytest.mark.asyncio
    async def test_get_gallery_assets_maps_video_type(self, service, mock_repository):
        """get_gallery_assets should map video type correctly."""
        user_id = uuid4()

        video_asset = Asset(
            id=uuid4(), db_id=1, title="Video", asset_type="video",
            prompt="test", width=720, height=1280, user_id=user_id,
            metadata={"duration": "0:15"},
            created_at=datetime.utcnow()
        )
        mock_repository.list_assets.return_value = ([video_asset], 1)

        result = await service.get_gallery_assets(user_id=user_id)

        assert result.items[0].type == "Ad Videos"
        assert result.items[0].tag == "VIDEO"
        assert result.items[0].is_vertical is True
        assert result.items[0].duration == "0:15"

    @pytest.mark.asyncio
    async def test_get_gallery_assets_maps_text_type(self, service, mock_repository):
        """get_gallery_assets should map text type correctly."""
        user_id = uuid4()

        text_asset = Asset(
            id=uuid4(), db_id=1, title="Copy", asset_type="text",
            prompt="test", content="Marketing copy here", width=0, height=0,
            user_id=user_id, created_at=datetime.utcnow()
        )
        mock_repository.list_assets.return_value = ([text_asset], 1)

        result = await service.get_gallery_assets(user_id=user_id)

        assert result.items[0].type == "Marketing Copy"
        assert result.items[0].tag == "COPY"
        assert result.items[0].is_text is True
        assert result.items[0].content == "Marketing copy here"

    @pytest.mark.asyncio
    async def test_get_gallery_assets_pagination(self, service, mock_repository, sample_asset):
        """get_gallery_assets should calculate pagination correctly."""
        user_id = uuid4()
        mock_repository.list_assets.return_value = ([sample_asset], 50)

        result = await service.get_gallery_assets(user_id=user_id, page=2, limit=10)

        assert result.total == 50
        assert result.page == 2
        assert result.limit == 10
        assert result.pages == 5  # 50 / 10 = 5

    @pytest.mark.asyncio
    async def test_get_gallery_assets_filters_by_type(self, service, mock_repository, sample_asset):
        """get_gallery_assets should pass type filter to repository."""
        user_id = uuid4()
        mock_repository.list_assets.return_value = ([sample_asset], 1)

        await service.get_gallery_assets(user_id=user_id, asset_type="image")

        mock_repository.list_assets.assert_called_once()
        call_args = mock_repository.list_assets.call_args
        assert call_args[1]["asset_type"] == "image"

    @pytest.mark.asyncio
    async def test_get_gallery_assets_searches(self, service, mock_repository, sample_asset):
        """get_gallery_assets should pass search query to repository."""
        user_id = uuid4()
        mock_repository.list_assets.return_value = ([sample_asset], 1)

        await service.get_gallery_assets(user_id=user_id, search_query="sunset")

        mock_repository.list_assets.assert_called_once()
        call_args = mock_repository.list_assets.call_args
        assert call_args[1]["search_query"] == "sunset"

    @pytest.mark.asyncio
    async def test_title_fallback_to_prompt(self, service, mock_repository):
        """GalleryAssetDTO should use truncated prompt when title is None."""
        user_id = uuid4()

        # Asset with no title
        asset = Asset(
            id=uuid4(), db_id=1, title=None, asset_type="image",
            prompt="This is a very long prompt that should be truncated for display purposes",
            width=512, height=512, user_id=user_id,
            created_at=datetime.utcnow()
        )
        mock_repository.list_assets.return_value = ([asset], 1)

        result = await service.get_gallery_assets(user_id=user_id)

        # Should use truncated prompt as title
        assert result.items[0].title is not None
        assert len(result.items[0].title) <= 53  # 50 chars + "..."
