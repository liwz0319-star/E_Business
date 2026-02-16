"""
User Settings Routes

API endpoints for User Settings & Profile feature (Story 6-3).
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.user_settings_dtos import (
    UpdateUserSettingsRequestDTO,
    UserSettingsResponseDTO,
)
from app.application.services.user_settings_service import UserSettingsService
from app.domain.entities.user import User
from app.infrastructure.database.connection import get_async_session
from app.infrastructure.repositories.user_settings_repository import PostgresUserSettingsRepository
from app.interface.dependencies.auth import get_current_user


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["User Settings"])


async def get_user_settings_service(
    session: AsyncSession = Depends(get_async_session),
) -> UserSettingsService:
    """
    Get UserSettingsService instance with dependencies.

    Args:
        session: Async database session

    Returns:
        Configured UserSettingsService instance
    """
    repository = PostgresUserSettingsRepository(session)
    return UserSettingsService(repository)


@router.get(
    "/settings",
    response_model=UserSettingsResponseDTO,
    summary="Get user settings",
    description="Returns the current user's settings including AI preferences and integration status. Creates default settings if none exist.",
)
async def get_settings(
    current_user: Annotated[User, Depends(get_current_user)],
    service: Annotated[UserSettingsService, Depends(get_user_settings_service)],
) -> UserSettingsResponseDTO:
    """
    Get user settings.

    Returns the current user's settings including:
    - AI preferences (language, tone, aspect ratio)
    - Integration status (Shopify, Amazon, TikTok)

    If the user has no existing settings record, creates one with default values.

    Requires JWT authentication.
    """
    try:
        logger.info(f"User {current_user.id} fetching settings")

        result = await service.get_settings(current_user.id)
        return result

    except Exception as e:
        logger.error(f"Failed to get settings for user {current_user.id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve settings",
        )


@router.patch(
    "/settings",
    response_model=UserSettingsResponseDTO,
    summary="Update user settings",
    description="Allows partial updates to AI preferences and/or integration status. Only updates fields that are explicitly provided.",
)
async def update_settings(
    request: UpdateUserSettingsRequestDTO,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_async_session)],
    service: Annotated[UserSettingsService, Depends(get_user_settings_service)],
) -> UserSettingsResponseDTO:
    """
    Update user settings.

    Allows partial updates to:
    - AI preferences (language, tone, aspect ratio)
    - Integration status (Shopify, Amazon, TikTok)

    Only updates fields that are explicitly provided in the request body.

    Validation:
    - language: Must be one of ['en-US', 'zh-CN', 'zh-TW', 'ja-JP', 'ko-KR']
    - tone: Must be one of ['professional', 'casual', 'playful', 'luxury', 'minimal']
    - aspect_ratio: Must be one of ['1:1', '4:3', '3:4', '16:9', '9:16']

    Requires JWT authentication.
    Returns 422 Unprocessable Entity for validation errors.
    """
    try:
        logger.info(f"User {current_user.id} updating settings")

        result = await service.update_settings(current_user.id, request)
        await session.commit()

        logger.info(f"User {current_user.id} settings updated successfully")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update settings for user {current_user.id}: {str(e)}", exc_info=True)
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update settings",
        )
