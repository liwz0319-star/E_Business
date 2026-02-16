"""
User Settings Repository Interface

Abstract interface defining the contract for user settings persistence operations.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from uuid import UUID

from app.domain.entities.user_settings import UserSettings


class IUserSettingsRepository(ABC):
    """
    Abstract interface for user settings repository operations.

    Defines the contract for persisting and retrieving user settings
    in the User Settings & Profile feature.
    """

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> Optional[UserSettings]:
        """
        Get settings for a specific user.

        Args:
            user_id: The user's UUID

        Returns:
            UserSettings if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_or_create(self, user_id: UUID) -> UserSettings:
        """
        Get existing settings or create new ones with defaults.

        This implements the lazy creation pattern - settings are
        automatically created on first access if they don't exist.

        Args:
            user_id: The user's UUID

        Returns:
            UserSettings (existing or newly created)
        """
        pass

    @abstractmethod
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

        Returns:
            Updated UserSettings

        Raises:
            ValueError: If settings don't exist for user
        """
        pass

    @abstractmethod
    async def create(self, user_id: UUID) -> UserSettings:
        """
        Create new settings for a user with default values.

        Args:
            user_id: The user's UUID

        Returns:
            Newly created UserSettings
        """
        pass
