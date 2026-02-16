"""
Tests for UserSettingsModel database model.

Tests cover model creation, field validation, and database constraints.
"""
import pytest
import pytest_asyncio
from datetime import datetime
from uuid import uuid4, UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import UserSettingsModel, UserModel


class TestUserSettingsModel:
    """Tests for UserSettingsModel database operations."""

    @pytest.mark.asyncio
    async def test_create_user_settings_with_defaults(
        self, async_session: AsyncSession, test_user: UserModel
    ):
        """Test creating user settings with default values."""
        settings = UserSettingsModel(user_id=test_user.id)
        async_session.add(settings)
        await async_session.commit()
        await async_session.refresh(settings)

        assert settings.id is not None
        assert settings.user_id == test_user.id
        assert settings.language == "en-US"
        assert settings.tone == "professional"
        assert settings.aspect_ratio == "1:1"
        assert settings.shopify_config == {"connected": False}
        assert settings.amazon_config == {"connected": False}
        assert settings.tiktok_config == {"connected": False}
        assert settings.created_at is not None
        assert settings.updated_at is not None

    @pytest.mark.asyncio
    async def test_create_user_settings_with_custom_values(
        self, async_session: AsyncSession, test_user: UserModel
    ):
        """Test creating user settings with custom values."""
        settings = UserSettingsModel(
            user_id=test_user.id,
            language="zh-CN",
            tone="casual",
            aspect_ratio="16:9",
            shopify_config={"connected": True, "storeName": "my-store.myshopify.com"},
            amazon_config={"connected": True, "region": "US"},
            tiktok_config={"connected": False},
        )
        async_session.add(settings)
        await async_session.commit()
        await async_session.refresh(settings)

        assert settings.language == "zh-CN"
        assert settings.tone == "casual"
        assert settings.aspect_ratio == "16:9"
        assert settings.shopify_config["connected"] is True
        assert settings.shopify_config["storeName"] == "my-store.myshopify.com"
        assert settings.amazon_config["connected"] is True
        assert settings.amazon_config["region"] == "US"

    @pytest.mark.asyncio
    async def test_user_settings_unique_user_constraint(
        self, async_session: AsyncSession, test_user: UserModel
    ):
        """Test that each user can only have one settings record."""
        settings1 = UserSettingsModel(user_id=test_user.id)
        async_session.add(settings1)
        await async_session.commit()

        # Attempt to create second settings for same user
        settings2 = UserSettingsModel(user_id=test_user.id)
        async_session.add(settings2)

        with pytest.raises(Exception):  # IntegrityError
            await async_session.commit()

    @pytest.mark.asyncio
    async def test_user_settings_cascade_delete(
        self, async_session: AsyncSession, test_user: UserModel
    ):
        """Test that settings are deleted when user is deleted."""
        settings = UserSettingsModel(user_id=test_user.id)
        async_session.add(settings)
        await async_session.commit()
        settings_id = settings.id

        # Delete user
        await async_session.delete(test_user)
        await async_session.commit()

        # Verify settings are also deleted
        result = await async_session.execute(
            select(UserSettingsModel).where(UserSettingsModel.id == settings_id)
        )
        deleted_settings = result.scalar_one_or_none()
        assert deleted_settings is None

    @pytest.mark.asyncio
    async def test_user_settings_updated_at_on_change(
        self, async_session: AsyncSession, test_user: UserModel
    ):
        """Test that updated_at changes when settings are modified."""
        settings = UserSettingsModel(user_id=test_user.id)
        async_session.add(settings)
        await async_session.commit()
        await async_session.refresh(settings)

        original_updated_at = settings.updated_at

        # Modify settings
        settings.language = "zh-TW"
        await async_session.commit()
        await async_session.refresh(settings)

        assert settings.updated_at >= original_updated_at


@pytest_asyncio.fixture
async def test_user(async_session: AsyncSession) -> UserModel:
    """Create a test user for settings tests."""
    user = UserModel(
        email=f"test-settings-{uuid4()}@example.com",
        hashed_password="hashed_password_123",
    )
    async_session.add(user)
    await async_session.commit()
    await async_session.refresh(user)
    return user
