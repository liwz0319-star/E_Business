"""
Integration Tests for User Settings API.

Tests cover API endpoints including authentication, validation, and response format.
"""
import asyncio
import pytest
import pytest_asyncio
from datetime import datetime
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.infrastructure.database.models import UserModel, UserSettingsModel


class TestGetSettings:
    """Tests for GET /api/v1/user/settings endpoint."""

    @pytest.mark.asyncio
    async def test_get_settings_unauthorized(self, async_client: AsyncClient):
        """Test that unauthorized request returns 401."""
        response = await async_client.get("/api/v1/user/settings")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_settings_returns_defaults(
        self,
        async_client_with_session: tuple[AsyncClient, AsyncSession],
    ):
        """Test that get settings returns default values when none exist."""
        client, session = async_client_with_session

        # Create test user
        user = UserModel(
            email=f"test-settings-api-{uuid4()}@example.com",
            hashed_password="hashed_password_123",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/api/v1/user/settings", headers=headers)

        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "aiPreferences" in data
        assert "integrations" in data
        assert "updatedAt" in data

        # Check AI preferences defaults
        assert data["aiPreferences"]["language"] == "en-US"
        assert data["aiPreferences"]["tone"] == "professional"
        assert data["aiPreferences"]["aspectRatio"] == "1:1"

        # Check integrations defaults
        assert data["integrations"]["shopify"]["connected"] is False
        assert data["integrations"]["amazon"]["connected"] is False
        assert data["integrations"]["tiktok"]["connected"] is False

    @pytest.mark.asyncio
    async def test_get_settings_returns_existing(
        self,
        async_client_with_session: tuple[AsyncClient, AsyncSession],
    ):
        """Test that get settings returns existing values."""
        client, session = async_client_with_session

        # Create test user
        user = UserModel(
            email=f"test-settings-api-{uuid4()}@example.com",
            hashed_password="hashed_password_123",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Create settings directly
        settings = UserSettingsModel(
            user_id=user.id,
            language="zh-CN",
            tone="casual",
            aspect_ratio="16:9",
        )
        session.add(settings)
        await session.commit()

        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.get("/api/v1/user/settings", headers=headers)

        assert response.status_code == 200
        data = response.json()

        assert data["aiPreferences"]["language"] == "zh-CN"
        assert data["aiPreferences"]["tone"] == "casual"
        assert data["aiPreferences"]["aspectRatio"] == "16:9"


class TestUpdateSettings:
    """Tests for PATCH /api/v1/user/settings endpoint."""

    @pytest.mark.asyncio
    async def test_update_settings_unauthorized(self, async_client: AsyncClient):
        """Test that unauthorized request returns 401."""
        response = await async_client.patch(
            "/api/v1/user/settings",
            json={"aiPreferences": {"language": "zh-CN"}},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_update_settings_ai_preferences(
        self,
        async_client_with_session: tuple[AsyncClient, AsyncSession],
    ):
        """Test updating AI preferences."""
        client, session = async_client_with_session

        # Create test user
        user = UserModel(
            email=f"test-settings-api-{uuid4()}@example.com",
            hashed_password="hashed_password_123",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.patch(
            "/api/v1/user/settings",
            headers=headers,
            json={
                "aiPreferences": {
                    "language": "zh-CN",
                    "tone": "playful",
                    "aspectRatio": "16:9",
                }
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["aiPreferences"]["language"] == "zh-CN"
        assert data["aiPreferences"]["tone"] == "playful"
        assert data["aiPreferences"]["aspectRatio"] == "16:9"

    @pytest.mark.asyncio
    async def test_update_settings_partial_update(
        self,
        async_client_with_session: tuple[AsyncClient, AsyncSession],
    ):
        """Test partial update - only language should change."""
        client, session = async_client_with_session

        # Create test user
        user = UserModel(
            email=f"test-settings-api-{uuid4()}@example.com",
            hashed_password="hashed_password_123",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        # First, set initial values
        await client.patch(
            "/api/v1/user/settings",
            headers=headers,
            json={
                "aiPreferences": {
                    "tone": "luxury",
                    "aspectRatio": "9:16",
                }
            },
        )

        # Now update only language
        response = await client.patch(
            "/api/v1/user/settings",
            headers=headers,
            json={
                "aiPreferences": {
                    "language": "ja-JP",
                }
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["aiPreferences"]["language"] == "ja-JP"
        # Other fields should remain unchanged
        assert data["aiPreferences"]["tone"] == "luxury"
        assert data["aiPreferences"]["aspectRatio"] == "9:16"

    @pytest.mark.asyncio
    async def test_update_settings_integrations(
        self,
        async_client_with_session: tuple[AsyncClient, AsyncSession],
    ):
        """Test updating integration configurations."""
        client, session = async_client_with_session

        # Create test user
        user = UserModel(
            email=f"test-settings-api-{uuid4()}@example.com",
            hashed_password="hashed_password_123",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.patch(
            "/api/v1/user/settings",
            headers=headers,
            json={
                "integrations": {
                    "shopify": {
                        "connected": True,
                        "storeName": "my-store.myshopify.com",
                    }
                }
            },
        )

        assert response.status_code == 200
        data = response.json()

        assert data["integrations"]["shopify"]["connected"] is True
        assert data["integrations"]["shopify"]["storeName"] == "my-store.myshopify.com"

    @pytest.mark.asyncio
    async def test_update_settings_empty_patch_no_op(
        self,
        async_client_with_session: tuple[AsyncClient, AsyncSession],
    ):
        """Test that empty PATCH {} returns 200 without updating updated_at."""
        client, session = async_client_with_session

        # Create test user
        user = UserModel(
            email=f"test-settings-api-{uuid4()}@example.com",
            hashed_password="hashed_password_123",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        # First, get initial settings
        initial_response = await client.get("/api/v1/user/settings", headers=headers)
        initial_updated_at = initial_response.json()["updatedAt"]

        # Small delay
        import asyncio
        await asyncio.sleep(0.05)

        # Empty PATCH
        response = await client.patch(
            "/api/v1/user/settings",
            headers=headers,
            json={},
        )

        assert response.status_code == 200
        data = response.json()

        # updated_at should NOT have changed
        assert data["updatedAt"] == initial_updated_at

    @pytest.mark.asyncio
    async def test_update_settings_integration_extension_fields_only(
        self,
        async_client_with_session: tuple[AsyncClient, AsyncSession],
    ):
        """Test updating only extension fields in integration (without connected)."""
        client, session = async_client_with_session

        # Create test user
        user = UserModel(
            email=f"test-settings-api-{uuid4()}@example.com",
            hashed_password="hashed_password_123",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        # First set connected to True
        await client.patch(
            "/api/v1/user/settings",
            headers=headers,
            json={
                "integrations": {
                    "shopify": {
                        "connected": True,
                        "storeName": "initial-store",
                    }
                }
            },
        )

        # Update only storeName (without connected field)
        response = await client.patch(
            "/api/v1/user/settings",
            headers=headers,
            json={
                "integrations": {
                    "shopify": {
                        "storeName": "updated-store",
                    }
                }
            },
        )

        assert response.status_code == 200
        data = response.json()

        # connected should remain True, storeName should be updated
        assert data["integrations"]["shopify"]["connected"] is True
        assert data["integrations"]["shopify"]["storeName"] == "updated-store"


class TestValidation:
    """Tests for input validation."""

    @pytest.mark.asyncio
    async def test_invalid_language_returns_422(
        self,
        async_client_with_session: tuple[AsyncClient, AsyncSession],
    ):
        """Test that invalid language returns 422 validation error."""
        client, session = async_client_with_session

        # Create test user
        user = UserModel(
            email=f"test-settings-api-{uuid4()}@example.com",
            hashed_password="hashed_password_123",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.patch(
            "/api/v1/user/settings",
            headers=headers,
            json={
                "aiPreferences": {
                    "language": "invalid-language",
                }
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_tone_returns_422(
        self,
        async_client_with_session: tuple[AsyncClient, AsyncSession],
    ):
        """Test that invalid tone returns 422 validation error."""
        client, session = async_client_with_session

        # Create test user
        user = UserModel(
            email=f"test-settings-api-{uuid4()}@example.com",
            hashed_password="hashed_password_123",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.patch(
            "/api/v1/user/settings",
            headers=headers,
            json={
                "aiPreferences": {
                    "tone": "invalid-tone",
                }
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_aspect_ratio_returns_422(
        self,
        async_client_with_session: tuple[AsyncClient, AsyncSession],
    ):
        """Test that invalid aspect ratio returns 422 validation error."""
        client, session = async_client_with_session

        # Create test user
        user = UserModel(
            email=f"test-settings-api-{uuid4()}@example.com",
            hashed_password="hashed_password_123",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        response = await client.patch(
            "/api/v1/user/settings",
            headers=headers,
            json={
                "aiPreferences": {
                    "aspectRatio": "invalid-ratio",
                }
            },
        )

        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_valid_languages_accepted(
        self,
        async_client_with_session: tuple[AsyncClient, AsyncSession],
    ):
        """Test that all valid languages are accepted."""
        client, session = async_client_with_session

        # Create test user
        user = UserModel(
            email=f"test-settings-api-{uuid4()}@example.com",
            hashed_password="hashed_password_123",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        valid_languages = ["en-US", "zh-CN", "zh-TW", "ja-JP", "ko-KR"]

        for lang in valid_languages:
            response = await client.patch(
                "/api/v1/user/settings",
                headers=headers,
                json={"aiPreferences": {"language": lang}},
            )
            assert response.status_code == 200, f"Language {lang} should be valid"

    @pytest.mark.asyncio
    async def test_valid_tones_accepted(
        self,
        async_client_with_session: tuple[AsyncClient, AsyncSession],
    ):
        """Test that all valid tones are accepted."""
        client, session = async_client_with_session

        # Create test user
        user = UserModel(
            email=f"test-settings-api-{uuid4()}@example.com",
            hashed_password="hashed_password_123",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        valid_tones = ["professional", "casual", "playful", "luxury", "minimal"]

        for tone in valid_tones:
            response = await client.patch(
                "/api/v1/user/settings",
                headers=headers,
                json={"aiPreferences": {"tone": tone}},
            )
            assert response.status_code == 200, f"Tone {tone} should be valid"

    @pytest.mark.asyncio
    async def test_valid_aspect_ratios_accepted(
        self,
        async_client_with_session: tuple[AsyncClient, AsyncSession],
    ):
        """Test that all valid aspect ratios are accepted."""
        client, session = async_client_with_session

        # Create test user
        user = UserModel(
            email=f"test-settings-api-{uuid4()}@example.com",
            hashed_password="hashed_password_123",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        token = create_access_token(data={"sub": str(user.id)})
        headers = {"Authorization": f"Bearer {token}"}

        valid_ratios = ["1:1", "4:3", "3:4", "16:9", "9:16"]

        for ratio in valid_ratios:
            response = await client.patch(
                "/api/v1/user/settings",
                headers=headers,
                json={"aiPreferences": {"aspectRatio": ratio}},
            )
            assert response.status_code == 200, f"Aspect ratio {ratio} should be valid"
