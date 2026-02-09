"""
Video Asset Repository Implementation

SQLAlchemy-based implementation for persisting image/video assets.
"""
import json
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.image_artifact import ImageArtifact
from app.infrastructure.database.models import VideoAssetModel


class VideoAssetRepository:
    """
    SQLAlchemy repository for video_assets table.
    
    Handles persistence of image and video assets.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session: Async SQLAlchemy session
        """
        self._session = session
    
    def _model_to_entity(self, model: VideoAssetModel) -> ImageArtifact:
        """Convert SQLAlchemy model to domain entity."""
        return ImageArtifact(
            id=model.asset_uuid,
            url=model.url,
            prompt=model.prompt,
            original_prompt=model.original_prompt or "",
            provider=model.provider,
            width=model.width,
            height=model.height,
            created_at=model.created_at,
            workflow_id=model.workflow_id,
        )
    
    def _entity_to_model(
        self,
        entity: ImageArtifact,
        user_id: Optional[UUID] = None,
        metadata: Optional[dict] = None,
    ) -> VideoAssetModel:
        """Convert domain entity to SQLAlchemy model."""
        return VideoAssetModel(
            asset_uuid=entity.id,
            user_id=user_id,
            workflow_id=entity.workflow_id,
            asset_type="image",
            url=entity.url,
            prompt=entity.prompt,
            original_prompt=entity.original_prompt,
            provider=entity.provider,
            width=entity.width,
            height=entity.height,
            metadata_json=json.dumps(metadata) if metadata else None,
            created_at=entity.created_at,
        )
    
    async def create(
        self,
        artifact: ImageArtifact,
        user_id: Optional[UUID] = None,
        metadata: Optional[dict] = None,
    ) -> ImageArtifact:
        """
        Create a new asset record in the database.
        
        Args:
            artifact: ImageArtifact entity to persist
            user_id: Optional user who created the asset
            metadata: Optional additional metadata
            
        Returns:
            Persisted ImageArtifact with database ID
        """
        model = self._entity_to_model(artifact, user_id, metadata)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        
        return self._model_to_entity(model)
    
    async def get_by_id(self, asset_id: int) -> Optional[ImageArtifact]:
        """
        Retrieve an asset by its database ID.
        
        Args:
            asset_id: The asset's integer ID
            
        Returns:
            ImageArtifact if found, None otherwise
        """
        result = await self._session.execute(
            select(VideoAssetModel).where(VideoAssetModel.id == asset_id)
        )
        model = result.scalar_one_or_none()
        
        if model is None:
            return None
        
        return self._model_to_entity(model)
    
    async def get_by_uuid(self, asset_uuid: UUID) -> Optional[ImageArtifact]:
        """
        Retrieve an asset by its UUID.
        
        Args:
            asset_uuid: The asset's UUID
            
        Returns:
            ImageArtifact if found, None otherwise
        """
        result = await self._session.execute(
            select(VideoAssetModel).where(VideoAssetModel.asset_uuid == asset_uuid)
        )
        model = result.scalar_one_or_none()
        
        if model is None:
            return None
        
        return self._model_to_entity(model)
    
    async def get_by_workflow_id(self, workflow_id: str) -> List[ImageArtifact]:
        """
        Retrieve all assets for a given workflow.
        
        Args:
            workflow_id: The workflow ID
            
        Returns:
            List of ImageArtifact entities
        """
        result = await self._session.execute(
            select(VideoAssetModel)
            .where(VideoAssetModel.workflow_id == workflow_id)
            .order_by(VideoAssetModel.created_at.desc())
        )
        models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def get_by_user_id(
        self,
        user_id: UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> List[ImageArtifact]:
        """
        Retrieve assets for a user with pagination.
        
        Args:
            user_id: The user's UUID
            limit: Maximum number of results
            offset: Number of results to skip
            
        Returns:
            List of ImageArtifact entities
        """
        result = await self._session.execute(
            select(VideoAssetModel)
            .where(VideoAssetModel.user_id == user_id)
            .order_by(VideoAssetModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()
        
        return [self._model_to_entity(model) for model in models]
    
    async def delete(self, asset_id: int) -> bool:
        """
        Delete an asset by its ID.
        
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
