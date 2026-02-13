"""
Asset Gallery Routes

API endpoints for Asset Gallery management (Story 6-2).
"""
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.asset_dtos import (
    GalleryAssetDTO,
    AssetListResponseDTO,
    AssetUpdateRequest,
)
from app.application.services.asset_service import AssetService
from app.interface.dependencies.auth import get_current_user
from app.domain.entities.user import User
from app.infrastructure.database.connection import get_async_session
from app.infrastructure.repositories.asset_repository import PostgresAssetRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/assets", tags=["Assets"])


async def get_asset_service(
    session: AsyncSession = Depends(get_async_session),
) -> AssetService:
    """Get AssetService instance with dependencies."""
    repository = PostgresAssetRepository(session)
    return AssetService(repository)


@router.get("", response_model=AssetListResponseDTO)
async def list_assets(
    type: Optional[str] = Query(
        None,
        description="Filter by asset type: image, video, text",
        pattern="^(image|video|text)$",
    ),
    q: Optional[str] = Query(
        None,
        description="Search query for title and prompt fields",
        max_length=100,
    ),
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """
    List assets with filtering, search, and pagination.

    Returns a paginated list of assets ordered by created_at DESC.

    Query Parameters:
    - type: Filter by asset type ('image', 'video', 'text')
    - q: Search term for title and prompt fields
    - page: Page number (default: 1)
    - limit: Items per page (default: 20, max: 100)
    """
    try:
        logger.info(f"User {current_user.id} listing assets (type={type}, q={q}, page={page})")

        result = await service.get_gallery_assets(
            user_id=current_user.id,
            asset_type=type,
            search_query=q,
            page=page,
            limit=limit,
        )

        return result

    except Exception as e:
        logger.error(f"Failed to list assets: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list assets",
        )


@router.get("/{asset_id}", response_model=GalleryAssetDTO)
async def get_asset(
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    service: AssetService = Depends(get_asset_service),
):
    """
    Get a single asset by UUID.

    Returns full details of a specific asset owned by the current user.
    Returns 404 if not found or not owned by user.
    """
    try:
        logger.info(f"User {current_user.id} getting asset {asset_id}")

        # Use user-scoped query to prevent IDOR
        result = await service.get_asset_by_uuid_for_user(asset_id, current_user.id)

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset {asset_id} not found",
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get asset: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve asset",
        )


@router.patch("/{asset_id}", response_model=GalleryAssetDTO)
async def update_asset(
    asset_id: UUID,
    request: AssetUpdateRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    service: AssetService = Depends(get_asset_service),
):
    """
    Update an asset's title.

    Only the title field can be updated.
    Returns 404 if asset not found.
    """
    try:
        logger.info(f"User {current_user.id} updating asset {asset_id}")

        # First verify asset exists and belongs to user
        repository = PostgresAssetRepository(session)
        asset = await repository.get_by_uuid(asset_id)

        if asset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset {asset_id} not found",
            )

        if asset.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Update title
        result = await service.update_asset_title(asset.db_id, request.title)

        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset {asset_id} not found",
            )

        await session.commit()
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update asset: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update asset",
        )


@router.delete("/{asset_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_asset(
    asset_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
    service: AssetService = Depends(get_asset_service),
):
    """
    Delete an asset.

    Permanently removes the asset from the database.
    Returns 204 No Content on success.
    Returns 404 if asset not found.
    """
    try:
        logger.info(f"User {current_user.id} deleting asset {asset_id}")

        # First verify asset exists and belongs to user
        repository = PostgresAssetRepository(session)
        asset = await repository.get_by_uuid(asset_id)

        if asset is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset {asset_id} not found",
            )

        if asset.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Delete asset
        deleted = await service.delete_asset(asset.db_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Asset {asset_id} not found",
            )

        await session.commit()
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete asset: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete asset",
        )
