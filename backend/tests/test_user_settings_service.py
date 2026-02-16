"""
Tests for UserSettingsService.

Tests cover service layer operations including DTO transformation and validation.
"""
import pytest
from datetime import datetime
from uuid import uuid4, UUID
from unittest.mock import AsyncMock, MagicMock

from app.application.dtos.user_settings_dtos import (
    UpdateUserSettingsRequestDTO,
    UpdateAIPreferencesDTO,
    UpdateIntegrationsDTO,
    IntegrationConfigDTO,
)
from app.application.services.user_settings_service import UserSettingsService
from app.domain.entities.user_settings import UserSettings


@pytest.fixture
def mock_repository():
    """Create mock repository for service tests."""
    return AsyncMock()


@pytest.fixture
def service(mock_repository):
    """Create service instance with mock repository."""
    return UserSettingsService(mock_repository)


@pytest.fixture
def sample_settings() -> UserSettings:
    """Create sample UserSettings entity for tests."""
    return UserSettings(
        id=uuid4(),
        user_id=uuid4(),
        language="en-US",
        tone="professional",
        aspect_ratio="1:1",
        shopify_config={"connected": False},
        amazon_config={"connected": False},
        tiktok_config={"connected": False},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


class TestUserSettingsServiceGet:
    """Tests for get_settings operation."""

    @pytest.mark.asyncio
    async def test_get_settings_returns_dto(
        self,
        service: UserSettingsService,
        mock_repository,
        sample_settings: UserSettings,
    ):
        """Test that get_settings returns properly formatted DTO."""
        mock_repository.get_or_create.return_value = sample_settings

        result = await service.get_settings(sample_settings.user_id)

        assert result is not None
        assert result.ai_preferences.language == "en-US"
        assert result.ai_preferences.tone == "professional"
        assert result.ai_preferences.aspect_ratio == "1:1"
        assert result.integrations.shopify.connected is False
        assert result.integrations.amazon.connected is False
        assert result.integrations.tiktok.connected is False

    @pytest.mark.asyncio
    async def test_get_settings_calls_repository(
        self,
        service: UserSettingsService,
        mock_repository,
        sample_settings: UserSettings,
    ):
        """Test that get_settings calls repository correctly."""
        mock_repository.get_or_create.return_value = sample_settings

        await service.get_settings(sample_settings.user_id)

        mock_repository.get_or_create.assert_called_once_with(sample_settings.user_id)


class TestUserSettingsServiceUpdate:
    """Tests for update_settings operation."""

    @pytest.mark.asyncio
    async def test_update_settings_ai_preferences(
        self,
        service: UserSettingsService,
        mock_repository,
        sample_settings: UserSettings,
    ):
        """Test updating AI preferences."""
        # Setup
        updated_settings = UserSettings(
            id=sample_settings.id,
            user_id=sample_settings.user_id,
            language="zh-CN",
            tone="casual",
            aspect_ratio="16:9",
            shopify_config=sample_settings.shopify_config,
            amazon_config=sample_settings.amazon_config,
            tiktok_config=sample_settings.tiktok_config,
            created_at=sample_settings.created_at,
            updated_at=datetime.utcnow(),
        )
        mock_repository.update.return_value = updated_settings

        # Execute
        request = UpdateUserSettingsRequestDTO(
            ai_preferences=UpdateAIPreferencesDTO(
                language="zh-CN",
                tone="casual",
                aspect_ratio="16:9",
            )
        )
        result = await service.update_settings(sample_settings.user_id, request)

        # Verify
        assert result.ai_preferences.language == "zh-CN"
        assert result.ai_preferences.tone == "casual"
        assert result.ai_preferences.aspect_ratio == "16:9"

        # Verify repository was called with correct updates
        mock_repository.update.assert_called_once()
        call_args = mock_repository.update.call_args
        assert call_args[0][0] == sample_settings.user_id
        assert "ai_preferences" in call_args[0][1]

    @pytest.mark.asyncio
    async def test_update_settings_integrations(
        self,
        service: UserSettingsService,
        mock_repository,
        sample_settings: UserSettings,
    ):
        """Test updating integrations."""
        # Setup
        updated_settings = UserSettings(
            id=sample_settings.id,
            user_id=sample_settings.user_id,
            language=sample_settings.language,
            tone=sample_settings.tone,
            aspect_ratio=sample_settings.aspect_ratio,
            shopify_config={"connected": True, "storeName": "my-store"},
            amazon_config=sample_settings.amazon_config,
            tiktok_config=sample_settings.tiktok_config,
            created_at=sample_settings.created_at,
            updated_at=datetime.utcnow(),
        )
        mock_repository.update.return_value = updated_settings

        # Execute
        request = UpdateUserSettingsRequestDTO(
            integrations=UpdateIntegrationsDTO(
                shopify=IntegrationConfigDTO(connected=True, storeName="my-store")
            )
        )
        result = await service.update_settings(sample_settings.user_id, request)

        # Verify
        assert result.integrations.shopify.connected is True

    @pytest.mark.asyncio
    async def test_update_settings_partial_update(
        self,
        service: UserSettingsService,
        mock_repository,
        sample_settings: UserSettings,
    ):
        """Test that only provided fields are updated."""
        # Setup
        mock_repository.update.return_value = sample_settings

        # Execute - only update language
        request = UpdateUserSettingsRequestDTO(
            ai_preferences=UpdateAIPreferencesDTO(language="ja-JP")
        )
        await service.update_settings(sample_settings.user_id, request)

        # Verify - only language should be in updates
        call_args = mock_repository.update.call_args
        updates = call_args[0][1]
        assert updates["ai_preferences"]["language"] == "ja-JP"
        assert "tone" not in updates["ai_preferences"]
        assert "aspect_ratio" not in updates["ai_preferences"]

    @pytest.mark.asyncio
    async def test_update_settings_empty_patch_no_op(
        self,
        service: UserSettingsService,
        mock_repository,
        sample_settings: UserSettings,
    ):
        """Test that empty PATCH {} does not trigger repository update."""
        # Setup
        mock_repository.get_or_create.return_value = sample_settings

        # Execute - empty request
        request = UpdateUserSettingsRequestDTO()
        result = await service.update_settings(sample_settings.user_id, request)

        # Verify - update should NOT be called, only get_or_create
        mock_repository.get_or_create.assert_called_once_with(sample_settings.user_id)
        mock_repository.update.assert_not_called()

        # Verify response is still valid
        assert result is not None
        assert result.ai_preferences.language == sample_settings.language

    @pytest.mark.asyncio
    async def test_update_settings_empty_nested_objects_no_op(
        self,
        service: UserSettingsService,
        mock_repository,
        sample_settings: UserSettings,
    ):
        """Test that PATCH with empty nested objects {} does not trigger update."""
        # Setup
        mock_repository.get_or_create.return_value = sample_settings

        # Execute - request with empty nested objects
        request = UpdateUserSettingsRequestDTO(
            ai_preferences=UpdateAIPreferencesDTO(),
            integrations=UpdateIntegrationsDTO(),
        )
        result = await service.update_settings(sample_settings.user_id, request)

        # Verify - update should NOT be called
        mock_repository.get_or_create.assert_called_once_with(sample_settings.user_id)
        mock_repository.update.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_settings_integration_extension_fields_only(
        self,
        service: UserSettingsService,
        mock_repository,
        sample_settings: UserSettings,
    ):
        """Test updating only extension fields in integration (without connected)."""
        # Setup
        updated_settings = UserSettings(
            id=sample_settings.id,
            user_id=sample_settings.user_id,
            language=sample_settings.language,
            tone=sample_settings.tone,
            aspect_ratio=sample_settings.aspect_ratio,
            shopify_config={"connected": True, "storeName": "new-store"},
            amazon_config=sample_settings.amazon_config,
            tiktok_config=sample_settings.tiktok_config,
            created_at=sample_settings.created_at,
            updated_at=datetime.utcnow(),
        )
        mock_repository.update.return_value = updated_settings

        # Execute - update only storeName, connected is None
        request = UpdateUserSettingsRequestDTO(
            integrations=UpdateIntegrationsDTO(
                shopify=IntegrationConfigDTO(storeName="new-store")
            )
        )
        result = await service.update_settings(sample_settings.user_id, request)

        # Verify repository was called
        mock_repository.update.assert_called_once()
        call_args = mock_repository.update.call_args
        updates = call_args[0][1]

        # Verify shopify update contains only storeName (connected excluded due to None)
        assert "shopify" in updates["integrations"]
        assert updates["integrations"]["shopify"]["storeName"] == "new-store"
        # connected should not be in updates (excluded_none=True)


class TestUserSettingsServiceEntityToDTO:
    """Tests for entity to DTO transformation."""

    def test_entity_to_dto_ai_preferences(
        self,
        service: UserSettingsService,
        sample_settings: UserSettings,
    ):
        """Test AI preferences DTO transformation."""
        result = service._entity_to_dto(sample_settings)

        assert result.ai_preferences.language == sample_settings.language
        assert result.ai_preferences.tone == sample_settings.tone
        assert result.ai_preferences.aspect_ratio == sample_settings.aspect_ratio

    def test_entity_to_dto_integrations(
        self,
        service: UserSettingsService,
        sample_settings: UserSettings,
    ):
        """Test integrations DTO transformation."""
        result = service._entity_to_dto(sample_settings)

        assert result.integrations.shopify.connected == sample_settings.shopify_config["connected"]
        assert result.integrations.amazon.connected == sample_settings.amazon_config["connected"]
        assert result.integrations.tiktok.connected == sample_settings.tiktok_config["connected"]

    def test_entity_to_dto_with_extra_integration_fields(
        self,
        service: UserSettingsService,
    ):
        """Test DTO transformation with extra integration fields."""
        settings = UserSettings(
            id=uuid4(),
            user_id=uuid4(),
            language="en-US",
            tone="professional",
            aspect_ratio="1:1",
            shopify_config={"connected": True, "storeName": "my-store.myshopify.com"},
            amazon_config={"connected": True, "region": "US", "sellerId": "12345"},
            tiktok_config={"connected": False},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        result = service._entity_to_dto(settings)

        assert result.integrations.shopify.model_dump(by_alias=True).get("storeName") == "my-store.myshopify.com"
        assert result.integrations.amazon.model_dump(by_alias=True).get("region") == "US"
