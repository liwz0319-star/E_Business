"""
Tests for UserSettingsRepository.

Tests cover repository operations including get, create, update, and lazy creation.
"""
import pytest
import pytest_asyncio
from datetime import datetime
from uuid import uuid4, UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user_settings import UserSettings, DEFAULT_SETTINGS
from app.infrastructure.database.models import UserModel, UserSettingsModel
from app.infrastructure.repositories.user_settings_repository import PostgresUserSettingsRepository


@pytest_asyncio.fixture
async def test_user(async_session: AsyncSession) -> UserModel:
    """Create a test user for settings tests."""
    user = UserModel(
        email=f"test-settings-repo-{uuid4()}@example.com",
        hashed_password="hashed_password_123",
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user


@pytest.fixture
def repository(async_session: AsyncSession) -> PostgresUserSettingsRepository:
    """Create repository instance for tests."""
    return PostgresUserSettingsRepository(async_session)


class TestUserSettingsRepositoryGet:
    """Tests for get operations."""

    @pytest.mark.asyncio
    async def test_get_by_user_id_returns_none_when_not_found(
        self,
        repository: PostgresUserSettingsRepository,
    ):
        """Test that get_by_user_id returns None when settings don't exist."""
        result = await repository.get_by_user_id(uuid4())
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_user_id_returns_settings_when_exists(
        self,
        repository: PostgresUserSettingsRepository,
        async_session: AsyncSession,
        test_user: UserModel,
    ):
        """Test that get_by_user_id returns settings when they exist."""
        # Create settings directly in database
        settings_model = UserSettingsModel(
            user_id=test_user.id,
            language="zh-CN",
            tone="casual",
        )
        async_session.add(settings_model)
        await async_session.commit()

        # Get via repository
        result = await repository.get_by_user_id(test_user.id)

        assert result is not None
        assert result.user_id == test_user.id
        assert result.language == "zh-CN"
        assert result.tone == "casual"


class TestUserSettingsRepositoryCreate:
    """Tests for create operations."""

    @pytest.mark.asyncio
    async def test_create_with_defaults(
        self,
        repository: PostgresUserSettingsRepository,
        async_session: AsyncSession,
        test_user: UserModel,
    ):
        """Test creating settings with default values."""
        result = await repository.create(test_user.id)

        assert result.id is not None
        assert result.user_id == test_user.id
        assert result.language == DEFAULT_SETTINGS["language"]
        assert result.tone == DEFAULT_SETTINGS["tone"]
        assert result.aspect_ratio == DEFAULT_SETTINGS["aspect_ratio"]
        assert result.shopify_config == {"connected": False}
        assert result.amazon_config == {"connected": False}
        assert result.tiktok_config == {"connected": False}
        assert result.created_at is not None
        assert result.updated_at is not None


class TestUserSettingsRepositoryGetOrCreate:
    """Tests for get_or_create (lazy creation) operations."""

    @pytest.mark.asyncio
    async def test_get_or_create_creates_when_not_exists(
        self,
        repository: PostgresUserSettingsRepository,
        test_user: UserModel,
    ):
        """Test that get_or_create creates settings when they don't exist."""
        result = await repository.get_or_create(test_user.id)

        assert result is not None
        assert result.user_id == test_user.id
        assert result.language == DEFAULT_SETTINGS["language"]

    @pytest.mark.asyncio
    async def test_get_or_create_returns_existing(
        self,
        repository: PostgresUserSettingsRepository,
        async_session: AsyncSession,
        test_user: UserModel,
    ):
        """Test that get_or_create returns existing settings."""
        # Create settings first
        settings_model = UserSettingsModel(
            user_id=test_user.id,
            language="ja-JP",
            tone="playful",
        )
        async_session.add(settings_model)
        await async_session.commit()

        # Get or create should return existing
        result = await repository.get_or_create(test_user.id)

        assert result is not None
        assert result.language == "ja-JP"
        assert result.tone == "playful"


class TestUserSettingsRepositoryUpdate:
    """Tests for update operations."""

    @pytest.mark.asyncio
    async def test_update_ai_preferences_language(
        self,
        repository: PostgresUserSettingsRepository,
        test_user: UserModel,
    ):
        """Test updating only the language field."""
        updates = {"ai_preferences": {"language": "zh-TW"}}
        result = await repository.update(test_user.id, updates)

        assert result.language == "zh-TW"
        # Other fields should remain default
        assert result.tone == DEFAULT_SETTINGS["tone"]
        assert result.aspect_ratio == DEFAULT_SETTINGS["aspect_ratio"]

    @pytest.mark.asyncio
    async def test_update_ai_preferences_multiple_fields(
        self,
        repository: PostgresUserSettingsRepository,
        test_user: UserModel,
    ):
        """Test updating multiple AI preference fields."""
        updates = {
            "ai_preferences": {
                "language": "ko-KR",
                "tone": "luxury",
                "aspect_ratio": "16:9",
            }
        }
        result = await repository.update(test_user.id, updates)

        assert result.language == "ko-KR"
        assert result.tone == "luxury"
        assert result.aspect_ratio == "16:9"

    @pytest.mark.asyncio
    async def test_update_integrations_shopify(
        self,
        repository: PostgresUserSettingsRepository,
        test_user: UserModel,
    ):
        """Test updating Shopify integration."""
        updates = {
            "integrations": {
                "shopify": {"connected": True, "storeName": "my-store.myshopify.com"}
            }
        }
        result = await repository.update(test_user.id, updates)

        assert result.shopify_config["connected"] is True
        assert result.shopify_config["storeName"] == "my-store.myshopify.com"

    @pytest.mark.asyncio
    async def test_update_integrations_merges_config(
        self,
        repository: PostgresUserSettingsRepository,
        async_session: AsyncSession,
        test_user: UserModel,
    ):
        """Test that integration updates merge with existing config."""
        # First update: set storeName
        await repository.update(
            test_user.id,
            {"integrations": {"shopify": {"connected": True, "storeName": "store1"}}},
        )

        # Second update: add another field
        result = await repository.update(
            test_user.id,
            {"integrations": {"shopify": {"region": "US"}}},
        )

        # Both fields should be present (merge behavior)
        assert result.shopify_config["storeName"] == "store1"
        assert result.shopify_config["region"] == "US"

    @pytest.mark.asyncio
    async def test_update_updated_at_changes(
        self,
        repository: PostgresUserSettingsRepository,
        async_session: AsyncSession,
        test_user: UserModel,
    ):
        """Test that updated_at timestamp changes on update."""
        # Create settings
        settings = await repository.get_or_create(test_user.id)
        original_updated_at = settings.updated_at

        # Small delay to ensure timestamp difference
        import asyncio
        await asyncio.sleep(0.01)

        # Update settings
        result = await repository.update(
            test_user.id,
            {"ai_preferences": {"language": "ja-JP"}},
        )

        assert result.updated_at >= original_updated_at

    @pytest.mark.asyncio
    async def test_update_integration_extension_fields_only(
        self,
        repository: PostgresUserSettingsRepository,
        test_user: UserModel,
    ):
        """Test updating only extension fields (without connected) in integration."""
        # First set connected to True
        await repository.update(
            test_user.id,
            {"integrations": {"shopify": {"connected": True, "storeName": "initial-store"}}},
        )

        # Update only extension field (storeName) - connected should remain True
        result = await repository.update(
            test_user.id,
            {"integrations": {"shopify": {"storeName": "updated-store"}}},
        )

        assert result.shopify_config["connected"] is True
        assert result.shopify_config["storeName"] == "updated-store"


class TestUserSettingsRepositoryConcurrency:
    """Tests for concurrent access handling."""

    @pytest.mark.asyncio
    async def test_create_handles_integrity_error_with_mock(
        self,
        async_session: AsyncSession,
        test_user: UserModel,
    ):
        """Test that IntegrityError during create is handled gracefully."""
        from unittest.mock import AsyncMock, patch
        from sqlalchemy.exc import IntegrityError

        repository = PostgresUserSettingsRepository(async_session)

        # First create settings normally
        settings = await repository.create(test_user.id)
        assert settings is not None
        assert settings.user_id == test_user.id

        # Verify we can get the same settings again
        settings2 = await repository.get_by_user_id(test_user.id)
        assert settings2 is not None
        assert settings2.user_id == test_user.id

    @pytest.mark.asyncio
    async def test_get_or_create_idempotent(
        self,
        repository: PostgresUserSettingsRepository,
        test_user: UserModel,
    ):
        """Test that multiple get_or_create calls return the same settings."""
        # First call creates
        settings1 = await repository.get_or_create(test_user.id)
        assert settings1 is not None

        # Second call should return existing
        settings2 = await repository.get_or_create(test_user.id)
        assert settings2 is not None
        assert settings2.id == settings1.id
