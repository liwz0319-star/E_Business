"""
Tests for Asset API Endpoints.

Integration tests for Asset Gallery API endpoints (Story 6-2).
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from httpx import AsyncClient, ASGITransport

from app.main import fastapi_app
from app.domain.entities.user import User
from app.domain.entities.asset import Asset
from app.infrastructure.database.connection import get_async_session
from app.infrastructure.repositories.user_repository import UserRepository
from app.infrastructure.repositories.asset_repository import PostgresAssetRepository
from app.core.security import create_access_token, get_password_hash


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def auth_headers_factory():
    """Factory to create auth headers for any user ID."""
    def _create_headers(user_id) -> dict:
        token = create_access_token(data={"sub": str(user_id)})
        return {"Authorization": f"Bearer {token}"}
    return _create_headers


# ============================================================================
# Unauthenticated Tests (401 responses)
# ============================================================================

class TestAssetsAPIUnauthenticated:
    """Test Asset Gallery API endpoints without authentication."""

    @pytest.mark.asyncio
    async def test_list_assets_requires_auth(self, async_client):
        """GET /api/v1/assets should return 401 without auth."""
        response = await async_client.get("/api/v1/assets")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_asset_by_id_requires_auth(self, async_client):
        """GET /api/v1/assets/{id} should return 401 without auth."""
        test_uuid = uuid4()
        response = await async_client.get(f"/api/v1/assets/{test_uuid}")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_asset_requires_auth(self, async_client):
        """PATCH /api/v1/assets/{id} should return 401 without auth."""
        test_uuid = uuid4()
        response = await async_client.patch(
            f"/api/v1/assets/{test_uuid}",
            json={"title": "New Title"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_delete_asset_requires_auth(self, async_client):
        """DELETE /api/v1/assets/{id} should return 401 without auth."""
        test_uuid = uuid4()
        response = await async_client.delete(f"/api/v1/assets/{test_uuid}")
        assert response.status_code == 401


# ============================================================================
# Authenticated CRUD Tests
# ============================================================================

class TestAssetsAPICrud:
    """Test Asset Gallery API CRUD operations with authentication."""

    @pytest.fixture
    async def test_user(self, db_session):
        """Create a test user."""
        user_repo = UserRepository(db_session)
        user = User.create(
            email="test_assets@example.com",
            hashed_password=get_password_hash("testpassword123"),
        )
        created_user = await user_repo.create(user)
        await db_session.commit()
        return created_user

    @pytest.fixture
    async def other_user(self, db_session):
        """Create another test user for IDOR tests."""
        user_repo = UserRepository(db_session)
        user = User.create(
            email="other_assets@example.com",
            hashed_password=get_password_hash("testpassword123"),
        )
        created_user = await user_repo.create(user)
        await db_session.commit()
        return created_user

    @pytest.fixture
    async def test_asset(self, db_session, test_user):
        """Create a test asset owned by test_user."""
        asset_repo = PostgresAssetRepository(db_session)
        asset = Asset(
            id=uuid4(),
            asset_type="image",
            prompt="A beautiful sunset over mountains",
            title="Sunset Image",
            url="https://example.com/sunset.png",
            width=1024,
            height=768,
            user_id=test_user.id,
        )
        created_asset = await asset_repo.create(asset, test_user.id)
        await db_session.commit()
        return created_asset

    @pytest.fixture
    async def other_user_asset(self, db_session, other_user):
        """Create a test asset owned by other_user."""
        asset_repo = PostgresAssetRepository(db_session)
        asset = Asset(
            id=uuid4(),
            asset_type="image",
            prompt="Another user's image",
            title="Other's Image",
            url="https://example.com/other.png",
            width=800,
            height=600,
            user_id=other_user.id,
        )
        created_asset = await asset_repo.create(asset, other_user.id)
        await db_session.commit()
        return created_asset

    # --- LIST tests ---

    @pytest.mark.asyncio
    async def test_list_assets_success(
        self, async_client_with_session, test_user, test_asset, auth_headers_factory
    ):
        """GET /api/v1/assets should return user's assets."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        response = await client.get("/api/v1/assets", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_assets_empty(
        self, async_client_with_session, test_user, auth_headers_factory
    ):
        """GET /api/v1/assets should return empty list for user with no assets."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        response = await client.get("/api/v1/assets", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_assets_only_returns_own_assets(
        self, async_client_with_session, test_user, test_asset,
        other_user, other_user_asset, auth_headers_factory
    ):
        """GET /api/v1/assets should only return assets owned by current user."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        response = await client.get("/api/v1/assets", headers=headers)

        assert response.status_code == 200
        data = response.json()
        # Should only see own assets, not other_user's
        asset_ids = [item["id"] for item in data["items"]]
        assert str(test_asset.id) in asset_ids
        assert str(other_user_asset.id) not in asset_ids

    # --- GET by ID tests ---

    @pytest.mark.asyncio
    async def test_get_asset_by_id_success(
        self, async_client_with_session, test_user, test_asset, auth_headers_factory
    ):
        """GET /api/v1/assets/{id} should return the asset."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        response = await client.get(
            f"/api/v1/assets/{test_asset.id}", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_asset.id)
        assert data["title"] == test_asset.title

    @pytest.mark.asyncio
    async def test_get_asset_by_id_not_found(
        self, async_client_with_session, test_user, auth_headers_factory
    ):
        """GET /api/v1/assets/{id} should return 404 for non-existent asset."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)
        fake_uuid = uuid4()

        response = await client.get(
            f"/api/v1/assets/{fake_uuid}", headers=headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_asset_by_id_idor_prevented(
        self, async_client_with_session, test_user, other_user_asset, auth_headers_factory
    ):
        """GET /api/v1/assets/{id} should return 404 for other user's asset (IDOR fix)."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        response = await client.get(
            f"/api/v1/assets/{other_user_asset.id}", headers=headers
        )

        # Should return 404, not 200 or 403 (to avoid information disclosure)
        assert response.status_code == 404

    # --- UPDATE tests ---

    @pytest.mark.asyncio
    async def test_update_asset_success(
        self, async_client_with_session, test_user, test_asset, auth_headers_factory
    ):
        """PATCH /api/v1/assets/{id} should update asset title."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        response = await client.patch(
            f"/api/v1/assets/{test_asset.id}",
            json={"title": "Updated Title"},
            headers=headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"

    @pytest.mark.asyncio
    async def test_update_asset_not_found(
        self, async_client_with_session, test_user, auth_headers_factory
    ):
        """PATCH /api/v1/assets/{id} should return 404 for non-existent asset."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)
        fake_uuid = uuid4()

        response = await client.patch(
            f"/api/v1/assets/{fake_uuid}",
            json={"title": "New Title"},
            headers=headers,
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_asset_forbidden(
        self, async_client_with_session, test_user, other_user_asset, auth_headers_factory
    ):
        """PATCH /api/v1/assets/{id} should return 403 for other user's asset."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        response = await client.patch(
            f"/api/v1/assets/{other_user_asset.id}",
            json={"title": "Hacked Title"},
            headers=headers,
        )

        assert response.status_code == 403

    # --- DELETE tests ---

    @pytest.mark.asyncio
    async def test_delete_asset_success(
        self, async_client_with_session, test_user, auth_headers_factory
    ):
        """DELETE /api/v1/assets/{id} should delete asset and return 204."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        # Create an asset to delete
        asset_repo = PostgresAssetRepository(session)
        asset = Asset(
            id=uuid4(),
            asset_type="text",
            prompt="Asset to delete",
            title="Delete Me",
            content="This will be deleted",
            user_id=test_user.id,
        )
        created_asset = await asset_repo.create(asset, test_user.id)
        await session.commit()

        response = await client.delete(
            f"/api/v1/assets/{created_asset.id}", headers=headers
        )

        assert response.status_code == 204

        # Verify it's deleted
        response2 = await client.get(
            f"/api/v1/assets/{created_asset.id}", headers=headers
        )
        assert response2.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_asset_not_found(
        self, async_client_with_session, test_user, auth_headers_factory
    ):
        """DELETE /api/v1/assets/{id} should return 404 for non-existent asset."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)
        fake_uuid = uuid4()

        response = await client.delete(
            f"/api/v1/assets/{fake_uuid}", headers=headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_asset_forbidden(
        self, async_client_with_session, test_user, other_user_asset, auth_headers_factory
    ):
        """DELETE /api/v1/assets/{id} should return 403 for other user's asset."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        response = await client.delete(
            f"/api/v1/assets/{other_user_asset.id}", headers=headers
        )

        assert response.status_code == 403


# ============================================================================
# Filtering and Pagination Tests
# ============================================================================

class TestAssetsAPIFiltering:
    """Test Asset Gallery API filtering and pagination."""

    @pytest.fixture
    async def test_user(self, db_session):
        """Create a test user."""
        user_repo = UserRepository(db_session)
        user = User.create(
            email="filter_test@example.com",
            hashed_password=get_password_hash("testpassword123"),
        )
        created_user = await user_repo.create(user)
        await db_session.commit()
        return created_user

    @pytest.fixture
    async def mixed_assets(self, db_session, test_user):
        """Create a mix of asset types for filtering tests."""
        asset_repo = PostgresAssetRepository(db_session)
        assets = []

        # Create image assets
        for i in range(3):
            asset = Asset(
                id=uuid4(),
                asset_type="image",
                prompt=f"Image prompt {i}",
                title=f"Image {i}",
                url=f"https://example.com/image{i}.png",
                width=1024,
                height=768,
                user_id=test_user.id,
            )
            assets.append(await asset_repo.create(asset, test_user.id))

        # Create video assets
        for i in range(2):
            asset = Asset(
                id=uuid4(),
                asset_type="video",
                prompt=f"Video prompt {i}",
                title=f"Video {i}",
                url=f"https://example.com/video{i}.mp4",
                width=720,
                height=1280,
                user_id=test_user.id,
            )
            assets.append(await asset_repo.create(asset, test_user.id))

        # Create text assets
        for i in range(2):
            asset = Asset(
                id=uuid4(),
                asset_type="text",
                prompt=f"Text prompt {i}",
                title=f"Marketing Copy {i}",
                content=f"Generated marketing content {i}",
                user_id=test_user.id,
            )
            assets.append(await asset_repo.create(asset, test_user.id))

        await db_session.commit()
        return assets

    @pytest.mark.asyncio
    async def test_filter_by_image_type(
        self, async_client_with_session, test_user, mixed_assets, auth_headers_factory
    ):
        """GET /api/v1/assets?type=image should return only images."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        response = await client.get(
            "/api/v1/assets?type=image", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        for item in data["items"]:
            assert item["tag"] == "IMG"

    @pytest.mark.asyncio
    async def test_filter_by_video_type(
        self, async_client_with_session, test_user, mixed_assets, auth_headers_factory
    ):
        """GET /api/v1/assets?type=video should return only videos."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        response = await client.get(
            "/api/v1/assets?type=video", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert item["tag"] == "VIDEO"

    @pytest.mark.asyncio
    async def test_filter_by_text_type(
        self, async_client_with_session, test_user, mixed_assets, auth_headers_factory
    ):
        """GET /api/v1/assets?type=text should return only text assets."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        response = await client.get(
            "/api/v1/assets?type=text", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for item in data["items"]:
            assert item["tag"] == "COPY"

    @pytest.mark.asyncio
    async def test_search_by_title(
        self, async_client_with_session, test_user, mixed_assets, auth_headers_factory
    ):
        """GET /api/v1/assets?q=Marketing should find text assets."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        response = await client.get(
            "/api/v1/assets?q=Marketing", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 2  # At least the 2 text assets

    @pytest.mark.asyncio
    async def test_search_by_prompt(
        self, async_client_with_session, test_user, mixed_assets, auth_headers_factory
    ):
        """GET /api/v1/assets?q=prompt should find all assets."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        response = await client.get(
            "/api/v1/assets?q=prompt", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 7  # All assets have "prompt" in their prompt

    @pytest.mark.asyncio
    async def test_pagination(
        self, async_client_with_session, test_user, mixed_assets, auth_headers_factory
    ):
        """GET /api/v1/assets with page/limit should paginate correctly."""
        client, session = async_client_with_session
        headers = auth_headers_factory(test_user.id)

        # Get first page
        response = await client.get(
            "/api/v1/assets?page=1&limit=3", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 3
        assert data["page"] == 1
        assert data["limit"] == 3
        assert data["pages"] == 3  # 7 items / 3 per page = 3 pages

        # Get second page
        response2 = await client.get(
            "/api/v1/assets?page=2&limit=3", headers=headers
        )

        assert response2.status_code == 200
        data2 = response2.json()
        assert len(data2["items"]) == 3
        assert data2["page"] == 2


# ============================================================================
# Response Format Tests
# ============================================================================

class TestAssetResponseFormat:
    """Test Asset API response format matches frontend expectations."""

    @pytest.mark.asyncio
    async def test_asset_dto_camel_case_serialization(self, db_session):
        """GalleryAssetDTO should serialize to camelCase."""
        from app.application.dtos.asset_dtos import GalleryAssetDTO

        dto = GalleryAssetDTO(
            id=str(uuid4()),
            title="Test Asset",
            type="Product Images",
            tag="IMG",
            meta="High-res Render • 1024x1024",
            url="https://example.com/asset.png",
            content=None,
            is_vertical=True,
            is_text=False,
            duration="0:15",
            created_at=datetime.utcnow(),
        )

        json_dict = dto.model_dump(by_alias=True)

        # Check camelCase fields
        assert "isVertical" in json_dict
        assert "isText" in json_dict
        assert "createdAt" in json_dict
        assert "is_vertical" not in json_dict  # snake_case should not appear
