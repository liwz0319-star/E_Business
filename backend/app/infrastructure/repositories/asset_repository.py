"""
Asset Repository Implementation.

SQLAlchemy-based implementation for persisting and retrieving assets.
"""
import json
from datetime import datetime
from typing import List, Optional, Tuple
from uuid import UUID

from sqlalchemy import select, or_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.asset import Asset
from app.domain.interfaces.asset_repository import IAssetRepository
from app.infrastructure.database.models import VideoAssetModel


class PostgresAssetRepository(IAssetRepository):
    """
    SQLAlchemy repository implementation for assets.

    Handles persistence of image, video, and text assets
    using the VideoAssetModel table.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    def _model_to_entity(self, model: VideoAssetModel) -> Asset:
        """Convert SQLAlchemy model to domain entity."""
        metadata = None
        if model.metadata_json:
            try:
                metadata = json.loads(model.metadata_json) if isinstance(model.metadata_json, str) else model.metadata_json
            except (json.JSONDecodeError, TypeError):
                metadata = None

        return Asset(
            db_id=model.id,  # Database integer ID
            id=model.asset_uuid,
            title=model.title,
            content=model.content,
            url=model.url,
            asset_type=model.asset_type,
            prompt=model.prompt,
            original_prompt=model.original_prompt,
            provider=model.provider,
            width=model.width,
            height=model.height,
            metadata=metadata,
            user_id=model.user_id,
            workflow_id=model.workflow_id,
            created_at=model.created_at,
        )

    def _entity_to_model(
        self,
        entity: Asset,
        user_id: Optional[UUID] = None,
    ) -> VideoAssetModel:
        """Convert domain entity to SQLAlchemy model."""
        metadata_json = None
        if entity.metadata:
            metadata_json = json.dumps(entity.metadata)

        return VideoAssetModel(
            asset_uuid=entity.id,
            user_id=user_id or entity.user_id,
            workflow_id=entity.workflow_id,
            asset_type=entity.asset_type,
            title=entity.title,
            content=entity.content,
            url=entity.url,
            prompt=entity.prompt,
            original_prompt=entity.original_prompt,
            provider=entity.provider,
            width=entity.width,
            height=entity.height,
            metadata_json=metadata_json,
            created_at=entity.created_at,
        )

    async def create(
        self,
        asset: Asset,
        user_id: Optional[UUID] = None,
    ) -> Asset:
        """
        Create a new asset record in the database.

        Args:
            asset: Asset entity to persist
            user_id: Optional user who created the asset

        Returns:
            Persisted Asset with database ID
        """
        model = self._entity_to_model(asset, user_id)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)

        return self._model_to_entity(model)

    async def get_by_id(self, asset_id: int) -> Optional[Asset]:
        """
        Retrieve an asset by its database ID.

        Args:
            asset_id: The asset's integer ID

        Returns:
            Asset if found, None otherwise
        """
        result = await self._session.execute(
            select(VideoAssetModel).where(VideoAssetModel.id == asset_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def get_by_uuid(self, asset_uuid: UUID) -> Optional[Asset]:
        """
        Retrieve an asset by its UUID.

        Args:
            asset_uuid: The asset's UUID

        Returns:
            Asset if found, None otherwise
        """
        result = await self._session.execute(
            select(VideoAssetModel).where(VideoAssetModel.asset_uuid == asset_uuid)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def get_by_uuid_for_user(
        self, asset_uuid: UUID, user_id: UUID
    ) -> Optional[Asset]:
        """
        Retrieve an asset by UUID with user ownership constraint.

        This method enforces user isolation to prevent IDOR attacks.

        Args:
            asset_uuid: The asset's UUID
            user_id: The user's UUID (must match asset owner)

        Returns:
            Asset if found AND belongs to user, None otherwise
        """
        result = await self._session.execute(
            select(VideoAssetModel).where(
                VideoAssetModel.asset_uuid == asset_uuid,
                VideoAssetModel.user_id == user_id,
            )
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._model_to_entity(model)

    async def list_assets(
        self,
        user_id: UUID,
        asset_type: Optional[str] = None,
        search_query: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Asset], int]:
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
        # Build base query
        query = select(VideoAssetModel).where(VideoAssetModel.user_id == user_id)

        # Apply asset type filter
        if asset_type:
            query = query.where(VideoAssetModel.asset_type == asset_type)

        # Apply search filter (case-insensitive)
        if search_query:
            search_pattern = f"%{search_query}%"
            query = query.where(
                or_(
                    VideoAssetModel.title.ilike(search_pattern),
                    VideoAssetModel.prompt.ilike(search_pattern),
                )
            )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(VideoAssetModel.created_at.desc())
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        # Execute query
        result = await self._session.execute(query)
        models = result.scalars().all()

        assets = [self._model_to_entity(model) for model in models]
        return assets, total

    async def update_title(self, asset_id: int, title: str) -> Optional[Asset]:
        """
        Update an asset's title.

        Args:
            asset_id: The asset's integer ID
            title: New title value

        Returns:
            Updated Asset if found, None otherwise
        """
        result = await self._session.execute(
            select(VideoAssetModel).where(VideoAssetModel.id == asset_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return None

        model.title = title
        model.updated_at = datetime.utcnow()
        await self._session.flush()
        await self._session.refresh(model)

        return self._model_to_entity(model)

    async def delete(self, asset_id: int) -> bool:
        """
        Delete an asset.

        Args:
            asset_id: The asset's integer ID

        Returns:
            True if deleted, False if not found
        """
        result = await self._session.execute(
            select(VideoAssetModel).where(VideoAssetModel.id == asset_id)
        )
        model = result.scalar_one_or_none()

        if model is None:
            return False

        await self._session.delete(model)
        await self._session.flush()

        return True
