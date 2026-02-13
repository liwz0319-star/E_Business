"""
Asset Service.

Application service for Asset Gallery business logic.
Handles DTO transformation and repository coordination.
"""
import math
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from app.application.dtos.asset_dtos import GalleryAssetDTO, AssetListResponseDTO
from app.domain.entities.asset import Asset
from app.domain.interfaces.asset_repository import IAssetRepository


class AssetService:
    """
    Application service for asset gallery operations.

    Coordinates repository access and transforms domain entities
    to frontend-compatible DTOs.
    """

    def __init__(self, repository: IAssetRepository):
        """
        Initialize service with repository.

        Args:
            repository: Asset repository implementation
        """
        self._repository = repository

    async def get_gallery_assets(
        self,
        user_id: UUID,
        asset_type: Optional[str] = None,
        search_query: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> AssetListResponseDTO:
        """
        Get paginated list of assets for gallery display.

        Args:
            user_id: User's UUID
            asset_type: Filter by type ('image', 'video', 'text')
            search_query: Search term for title/prompt
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            AssetListResponseDTO with items and pagination metadata
        """
        assets, total = await self._repository.list_assets(
            user_id=user_id,
            asset_type=asset_type,
            search_query=search_query,
            page=page,
            limit=limit,
        )

        # Transform entities to DTOs
        items = [self._entity_to_dto(asset) for asset in assets]

        # Calculate pagination metadata
        pages = math.ceil(total / limit) if total > 0 else 1

        return AssetListResponseDTO(
            items=items,
            total=total,
            page=page,
            limit=limit,
            pages=pages,
        )

    async def get_asset_by_id(self, asset_id: int) -> Optional[GalleryAssetDTO]:
        """
        Get a single asset by database ID.

        Args:
            asset_id: Database integer ID

        Returns:
            GalleryAssetDTO if found, None otherwise
        """
        asset = await self._repository.get_by_id(asset_id)
        if asset is None:
            return None
        return self._entity_to_dto(asset)

    async def get_asset_by_uuid(self, asset_uuid: UUID) -> Optional[GalleryAssetDTO]:
        """
        Get a single asset by UUID.

        Args:
            asset_uuid: Asset UUID

        Returns:
            GalleryAssetDTO if found, None otherwise
        """
        asset = await self._repository.get_by_uuid(asset_uuid)
        if asset is None:
            return None
        return self._entity_to_dto(asset)

    async def get_asset_by_uuid_for_user(
        self, asset_uuid: UUID, user_id: UUID
    ) -> Optional[GalleryAssetDTO]:
        """
        Get a single asset by UUID with user ownership check.

        Enforces user isolation to prevent IDOR attacks.

        Args:
            asset_uuid: Asset UUID
            user_id: User's UUID (must match asset owner)

        Returns:
            GalleryAssetDTO if found AND belongs to user, None otherwise
        """
        asset = await self._repository.get_by_uuid_for_user(asset_uuid, user_id)
        if asset is None:
            return None
        return self._entity_to_dto(asset)

    async def update_asset_title(self, asset_id: int, title: str) -> Optional[GalleryAssetDTO]:
        """
        Update an asset's title.

        Args:
            asset_id: Database integer ID
            title: New title value

        Returns:
            Updated GalleryAssetDTO if found, None otherwise
        """
        asset = await self._repository.update_title(asset_id, title)
        if asset is None:
            return None
        return self._entity_to_dto(asset)

    async def delete_asset(self, asset_id: int) -> bool:
        """
        Delete an asset.

        Args:
            asset_id: Database integer ID

        Returns:
            True if deleted, False if not found
        """
        return await self._repository.delete(asset_id)

    def _entity_to_dto(self, asset: Asset) -> GalleryAssetDTO:
        """
        Transform Asset entity to GalleryAssetDTO.

        Handles all field mappings including derived fields.

        Args:
            asset: Asset domain entity

        Returns:
            GalleryAssetDTO with frontend-compatible fields
        """
        return GalleryAssetDTO(
            id=str(asset.id),
            title=asset.display_title,  # Uses fallback logic
            type=asset.category,
            tag=asset.tag,
            meta=asset.meta_string,
            url=asset.url,
            content=asset.content,
            is_vertical=asset.is_vertical,
            is_text=asset.is_text,
            duration=asset.duration,
            created_at=asset.created_at,
        )
