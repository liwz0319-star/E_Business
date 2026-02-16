"""
Insights/Analytics Routes

API endpoints for Analytics/Insights (Story 6-4).
"""
import logging
from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.analytics_dtos import StatItemDTO, ChartPointDTO, TopAssetDTO
from app.application.services.analytics_service import AnalyticsService
from app.interface.dependencies.auth import get_current_user
from app.domain.entities.user import User
from app.infrastructure.database.connection import get_async_session
from app.infrastructure.repositories.analytics_repository import PostgresAnalyticsRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insights", tags=["Insights"])


async def get_analytics_service(
    session: AsyncSession = Depends(get_async_session),
) -> AnalyticsService:
    """Get AnalyticsService instance with dependencies."""
    repository = PostgresAnalyticsRepository(session)
    return AnalyticsService(repository)


@router.get("/stats", response_model=List[StatItemDTO])
async def get_stats(
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get KPI statistics for the insights dashboard.

    Returns an array of 4 KPI stat items:
    - Total Views
    - Click-Through Rate
    - Conversion Rate
    - AI Efficiency Gain

    Each item includes label, value, trend, and icon fields.
    """
    logger.info(f"User {current_user.id} requesting analytics stats")
    return await service.get_stats(current_user.id)


@router.get("/charts", response_model=List[ChartPointDTO])
async def get_charts(
    days: int = Query(
        30,
        ge=7,
        le=90,
        description="Number of days to include (default: 30, min: 7, max: 90)"
    ),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get daily activity chart data.

    Returns time-series data for the activity chart over the specified number of days.
    Missing dates are filled with zero values for continuous chart display.

    Query Parameters:
    - days: Number of days to include (default: 30, min: 7, max: 90)
    """
    logger.info(f"User {current_user.id} requesting chart data for {days} days")
    return await service.get_charts(current_user.id, days)


@router.get("/top-assets", response_model=List[TopAssetDTO])
async def get_top_assets(
    limit: int = Query(
        5,
        ge=1,
        le=10,
        description="Maximum number of assets to return (default: 5, max: 10)"
    ),
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    """
    Get top-performing assets with mock scores.

    Returns a list of recent assets with mock performance scores.
    Real asset data is combined with simulated scores for display.

    Query Parameters:
    - limit: Maximum number of assets to return (default: 5, max: 10)
    """
    logger.info(f"User {current_user.id} requesting top {limit} assets")
    return await service.get_top_assets(current_user.id, limit)
