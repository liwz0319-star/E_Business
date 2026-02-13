"""
Asset Repository Interface.

Abstract interface defining the contract for asset persistence operations.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from app.domain.entities.asset import Asset


class IAssetRepository(ABC):
    """
    Abstract interface for asset repository operations.

    Defines the contract for persisting and retrieving assets
    in the Asset Gallery feature.
    """

    @abstractmethod
    async def list_assets(
        self,
        user_id: UUID,
        asset_type: Optional[str] = None,
        search_query: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[List[Asset], int]:
        """
        List assets with filtering, search, and pagination.

        Args:
            user_id: The user's UUID
            asset_type: Filter by type ('image', 'video', 'text') or None for all
            search_query: Search term for title and prompt fields
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (list of assets, total count)
        """
        pass

    @abstractmethod
    async def get_by_id(self, asset_id: int) -> Optional[Asset]:
        """
        Get an asset by its database ID.

        Args:
            asset_id: The asset's integer ID

        Returns:
            Asset if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_uuid(self, asset_uuid: UUID) -> Optional[Asset]:
        """
        Get an asset by its UUID.

        Args:
            asset_uuid: The asset's UUID

        Returns:
            Asset if found, None otherwise
        """
        pass

    @abstractmethod
    async def get_by_uuid_for_user(
        self, asset_uuid: UUID, user_id: UUID
    ) -> Optional[Asset]:
        """
        Get an asset by UUID with user ownership constraint.

        This method enforces user isolation to prevent IDOR attacks.

        Args:
            asset_uuid: The asset's UUID
            user_id: The user's UUID (must match asset owner)

        Returns:
            Asset if found AND belongs to user, None otherwise
        """
        pass

    @abstractmethod
    async def update_title(self, asset_id: int, title: str) -> Optional[Asset]:
        """
        Update an asset's title.

        Args:
            asset_id: The asset's integer ID
            title: New title value

        Returns:
            Updated Asset if found, None otherwise
        """
        pass

    @abstractmethod
    async def delete(self, asset_id: int) -> bool:
        """
        Delete an asset.

        Args:
            asset_id: The asset's integer ID

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def create(
        self,
        asset: Asset,
        user_id: Optional[UUID] = None,
    ) -> Asset:
        """
        Create a new asset.

        Args:
            asset: Asset entity to persist
            user_id: Optional user who created the asset

        Returns:
            Created Asset with database ID
        """
        pass
