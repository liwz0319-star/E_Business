"""
User Settings Repository Implementation

SQLAlchemy-based implementation for persisting and retrieving user settings.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user_settings import UserSettings, DEFAULT_SETTINGS
from app.domain.interfaces.user_settings_repository import IUserSettingsRepository
from app.infrastructure.database.models import UserSettingsModel


class PostgresUserSettingsRepository(IUserSettingsRepository):
    """
    SQLAlchemy repository implementation for user settings.

    Handles persistence of user preferences and integration configurations
    using the UserSettingsModel table.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    def _model_to_entity(self, model: UserSettingsModel) -> UserSettings:
        """
        Convert SQLAlchemy model to domain entity.

        Args:
            model: UserSettingsModel instance

        Returns:
            UserSettings domain entity
        """
        return UserSettings(
            id=model.id,
            user_id=model.user_id,
            language=model.language,
            tone=model.tone,
            aspect_ratio=model.aspect_ratio,
            shopify_config=model.shopify_config or {"connected": False},
            amazon_config=model.amazon_config or {"connected": False},
            tiktok_config=model.tiktok_config or {"connected": False},
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def get_by_user_id(self, user_id: UUID) -> Optional[UserSettings]:
        """
        Get settings for a specific user.

        Args:
            user_id: The user's UUID

        Returns:
            UserSettings if found, None otherwise
        """
        result = await self._session.execute(
            select(UserSettingsModel).where(UserSettingsModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def get_or_create(self, user_id: UUID) -> UserSettings:
        """
        Get existing settings or create new ones with defaults.

        Implements lazy creation pattern - settings are automatically
        created on first access if they don't exist.

        Handles concurrent access by catching unique constraint violations
        and returning the existing record.

        Args:
            user_id: The user's UUID

        Returns:
            UserSettings (existing or newly created)
        """
        settings = await self.get_by_user_id(user_id)

        if settings is None:
            # Create with defaults (handles race condition)
            settings = await self._create_with_race_handling(user_id)

        return settings

    async def _create_with_race_handling(self, user_id: UUID) -> UserSettings:
        """
        Create settings with concurrent access handling.

        If a race condition occurs (unique constraint violation),
        fetches and returns the existing record instead.

        Args:
            user_id: The user's UUID

        Returns:
            UserSettings (newly created or existing from race)
        """
        model = UserSettingsModel(
            user_id=user_id,
            language=DEFAULT_SETTINGS["language"],
            tone=DEFAULT_SETTINGS["tone"],
            aspect_ratio=DEFAULT_SETTINGS["aspect_ratio"],
            shopify_config=DEFAULT_SETTINGS["shopify_config"].copy(),
            amazon_config=DEFAULT_SETTINGS["amazon_config"].copy(),
            tiktok_config=DEFAULT_SETTINGS["tiktok_config"].copy(),
        )

        self._session.add(model)

        try:
            await self._session.flush()
            await self._session.refresh(model)
            return self._model_to_entity(model)
        except IntegrityError:
            # Race condition: another request created settings first
            # Rollback the failed insert and fetch existing record
            await self._session.rollback()
            existing = await self.get_by_user_id(user_id)
            if existing is None:
                # Should never happen, but handle gracefully
                raise ValueError(f"Failed to get or create settings for user {user_id}")
            return existing

    async def create(self, user_id: UUID) -> UserSettings:
        """
        Create new settings for a user with default values.

        Note: Prefer get_or_create for most use cases.
        This method does not handle concurrent access.

        Args:
            user_id: The user's UUID

        Returns:
            Newly created UserSettings
        """
        return await self._create_with_race_handling(user_id)

    async def update(
        self,
        user_id: UUID,
        updates: Dict[str, Any],
    ) -> UserSettings:
        """
        Update user settings with partial updates.

        Only updates fields that are explicitly provided in the updates dict.
        Supports nested updates for ai_preferences and integrations.

        Args:
            user_id: The user's UUID
            updates: Dictionary of fields to update
                - ai_preferences: {language, tone, aspect_ratio}
                - integrations: {shopify, amazon, tiktok}

        Returns:
            Updated UserSettings

        Raises:
            ValueError: If settings don't exist for user
        """
        # Get existing settings (will create if not exists)
        settings = await self.get_or_create(user_id)

        # Get the model for updating
        result = await self._session.execute(
            select(UserSettingsModel).where(UserSettingsModel.user_id == user_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            raise ValueError(f"Settings not found for user {user_id}")

        # Handle nested AI preferences
        if "ai_preferences" in updates:
            prefs = updates["ai_preferences"]
            if "language" in prefs:
                model.language = prefs["language"]
            if "tone" in prefs:
                model.tone = prefs["tone"]
            if "aspect_ratio" in prefs:
                model.aspect_ratio = prefs["aspect_ratio"]

        # Handle nested integrations
        if "integrations" in updates:
            integrations = updates["integrations"]

            if "shopify" in integrations:
                model.shopify_config = {
                    **model.shopify_config,
                    **integrations["shopify"],
                }

            if "amazon" in integrations:
                model.amazon_config = {
                    **model.amazon_config,
                    **integrations["amazon"],
                }

            if "tiktok" in integrations:
                model.tiktok_config = {
                    **model.tiktok_config,
                    **integrations["tiktok"],
                }

        model.updated_at = datetime.utcnow()

        await self._session.flush()
        await self._session.refresh(model)

        return self._model_to_entity(model)
