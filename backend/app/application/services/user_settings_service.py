"""
User Settings Service

Application service for User Settings business logic.
Handles DTO transformation and repository coordination.
"""

from typing import Dict, Any
from uuid import UUID

from app.application.dtos.user_settings_dtos import (
    UpdateUserSettingsRequestDTO,
    UserSettingsResponseDTO,
    AIPreferencesResponseDTO,
    IntegrationsResponseDTO,
    IntegrationResponseDTO,
)
from app.domain.entities.user_settings import UserSettings
from app.domain.interfaces.user_settings_repository import IUserSettingsRepository


class UserSettingsService:
    """
    Application service for user settings operations.

    Coordinates repository access and transforms domain entities
    to frontend-compatible DTOs.
    """

    def __init__(self, repository: IUserSettingsRepository):
        """
        Initialize service with repository.

        Args:
            repository: User settings repository implementation
        """
        self._repository = repository

    async def get_settings(self, user_id: UUID) -> UserSettingsResponseDTO:
        """
        Get user settings with lazy creation.

        If settings don't exist, creates them with default values.

        Args:
            user_id: User's UUID

        Returns:
            UserSettingsResponseDTO with current settings
        """
        settings = await self._repository.get_or_create(user_id)
        return self._entity_to_dto(settings)

    async def update_settings(
        self,
        user_id: UUID,
        request: UpdateUserSettingsRequestDTO,
    ) -> UserSettingsResponseDTO:
        """
        Update user settings with partial updates.

        Only updates fields that are explicitly provided in the request.

        Args:
            user_id: User's UUID
            request: Update request with optional fields

        Returns:
            UserSettingsResponseDTO with updated settings
        """
        # Convert DTO to repository update format
        updates: Dict[str, Any] = {}

        if request.ai_preferences is not None:
            updates["ai_preferences"] = {}
            if request.ai_preferences.language is not None:
                updates["ai_preferences"]["language"] = request.ai_preferences.language
            if request.ai_preferences.tone is not None:
                updates["ai_preferences"]["tone"] = request.ai_preferences.tone
            if request.ai_preferences.aspect_ratio is not None:
                updates["ai_preferences"]["aspect_ratio"] = request.ai_preferences.aspect_ratio

        if request.integrations is not None:
            updates["integrations"] = {}
            if request.integrations.shopify is not None:
                updates["integrations"]["shopify"] = request.integrations.shopify.model_dump(
                    by_alias=True,
                    exclude_none=True,
                )
            if request.integrations.amazon is not None:
                updates["integrations"]["amazon"] = request.integrations.amazon.model_dump(
                    by_alias=True,
                    exclude_none=True,
                )
            if request.integrations.tiktok is not None:
                updates["integrations"]["tiktok"] = request.integrations.tiktok.model_dump(
                    by_alias=True,
                    exclude_none=True,
                )

        # Remove empty nested dicts
        if "ai_preferences" in updates and not updates["ai_preferences"]:
            del updates["ai_preferences"]
        if "integrations" in updates and not updates["integrations"]:
            del updates["integrations"]

        # No-op: if no actual updates, return current settings without writing
        if not updates:
            settings = await self._repository.get_or_create(user_id)
            return self._entity_to_dto(settings)

        # Perform update
        settings = await self._repository.update(user_id, updates)
        return self._entity_to_dto(settings)

    def _entity_to_dto(self, settings: UserSettings) -> UserSettingsResponseDTO:
        """
        Transform UserSettings entity to UserSettingsResponseDTO.

        Handles all field mappings including camelCase conversion
        and nested object construction.

        Args:
            settings: UserSettings domain entity

        Returns:
            UserSettingsResponseDTO with frontend-compatible fields
        """
        # Build AI preferences DTO
        ai_preferences = AIPreferencesResponseDTO(
            language=settings.language,
            tone=settings.tone,
            aspect_ratio=settings.aspect_ratio,
        )

        # Build integrations DTO
        integrations = IntegrationsResponseDTO(
            shopify=IntegrationResponseDTO(**settings.shopify_config),
            amazon=IntegrationResponseDTO(**settings.amazon_config),
            tiktok=IntegrationResponseDTO(**settings.tiktok_config),
        )

        return UserSettingsResponseDTO(
            ai_preferences=ai_preferences,
            integrations=integrations,
            updated_at=settings.updated_at,
        )
