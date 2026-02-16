"""
Analytics Service Implementation.

Business logic for generating analytics data with real + mock hybrid approach.
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from uuid import UUID

from app.application.dtos.analytics_dtos import StatItemDTO, ChartPointDTO, TopAssetDTO
from app.infrastructure.repositories.analytics_repository import PostgresAnalyticsRepository


# Asset type mapping for display - matches frontend Insights.tsx expectations
TYPE_MAP = {
    "image": "Image",
    "video": "Video",
    "text": "Copy",
}


class AnalyticsService:
    """
    Service for generating analytics/insights data.

    Uses a hybrid approach: real data from database (counts, assets)
    combined with mock business logic (views, CTR, scores).
    """

    def __init__(self, repository: PostgresAnalyticsRepository):
        """
        Initialize service with repository.

        Args:
            repository: Analytics repository for data access
        """
        self._repo = repository

    async def get_stats(self, user_id: UUID) -> List[StatItemDTO]:
        """
        Get KPI statistics for the insights dashboard.

        Combines real project/asset counts with mock metrics.

        Args:
            user_id: The user's UUID

        Returns:
            List of 4 StatItemDTO objects
        """
        # Get real counts from database
        total_projects = await self._repo.count_projects(user_id)
        total_assets = await self._repo.count_assets(user_id)

        # Calculate mock stats based on real counts
        return _calculate_mock_stats(total_projects, total_assets)

    async def get_charts(self, user_id: UUID, days: int = 30) -> List[ChartPointDTO]:
        """
        Get daily activity chart data.

        Fills missing dates with zero values for continuous chart display.

        Args:
            user_id: The user's UUID
            days: Number of days to include (default: 30)

        Returns:
            List of ChartPointDTO objects, one per day
        """
        # Get real activity data from database
        raw_data = await self._repo.get_daily_activity(user_id, days)

        # Fill missing dates
        filled_data = _fill_missing_dates(raw_data, days)

        return [ChartPointDTO(date=item["date"], value=item["value"]) for item in filled_data]

    async def get_top_assets(self, user_id: UUID, limit: int = 5) -> List[TopAssetDTO]:
        """
        Get top-performing assets with mock scores.

        Combines real asset data with mock performance scores.

        Args:
            user_id: The user's UUID
            limit: Maximum number of assets to return (max: 10)

        Returns:
            List of TopAssetDTO objects
        """
        # Cap limit at 10
        limit = min(limit, 10)

        # Get real assets from database
        assets = await self._repo.get_recent_assets(user_id, limit)

        # Convert to DTOs with mock scores
        result = []
        for asset in assets:
            asset_type = TYPE_MAP.get(asset.asset_type, "Unknown")
            score = random.randint(75, 99)  # Mock score between 75-99

            dto = TopAssetDTO(
                id=str(asset.asset_uuid),
                name=asset.title or f"{asset_type} {asset.id}",
                created=asset.created_at.isoformat(),
                platform="AI Generated",
                type=asset_type,
                score=score,
                img=asset.url if asset.asset_type == "image" else None,
            )
            result.append(dto)

        return result


def _calculate_mock_stats(total_projects: int, total_assets: int) -> List[StatItemDTO]:
    """
    Calculate mock statistics based on real counts.

    Args:
        total_projects: Real project count from database
        total_assets: Real asset count from database

    Returns:
        List of 4 StatItemDTO objects with mock values

    AC1: Uses real basis from both projects AND assets.
    """
    # Total Views: projects * base_views + assets * asset_views_multiplier
    # Formula incorporates both project and asset counts per AC1
    base_project_views = random.randint(100, 500)
    asset_view_multiplier = random.randint(10, 50)
    total_views = (total_projects * base_project_views) + (total_assets * asset_view_multiplier)

    if total_views >= 1_000_000:
        views_str = f"{total_views / 1_000_000:.1f}M"
    elif total_views >= 1_000:
        views_str = f"{total_views // 1_000}K"
    else:
        views_str = str(total_views)

    # AI Efficiency Gain: hours saved based on both projects and assets
    # Formula: projects * hours_per_project + assets * hours_per_asset
    hours_per_project = random.randint(5, 15)
    hours_per_asset = random.randint(1, 3)
    total_hours = (total_projects * hours_per_project) + (total_assets * hours_per_asset)

    return [
        StatItemDTO(
            label="Total Views",
            value=views_str,
            trend=f"+{random.randint(8, 15)}%",
            icon="visibility",
            highlight=True,
        ),
        StatItemDTO(
            label="Click-Through Rate",
            value=f"{round(random.uniform(3.0, 5.0), 1)}%",
            trend=f"+{round(random.uniform(0.2, 0.8), 1)}%",
            icon="ads_click",
        ),
        StatItemDTO(
            label="Conversion Rate",
            value=f"{round(random.uniform(1.5, 3.0), 1)}%",
            trend=f"+{round(random.uniform(0.05, 0.2), 1)}%",
            icon="shopping_cart",
        ),
        StatItemDTO(
            label="AI Efficiency Gain",
            value=f"{total_hours}hrs Saved",
            trend=f"ROI +{random.randint(150, 250)}%",
            icon="auto_awesome",
        ),
    ]


def _fill_missing_dates(data: List[Dict[str, Any]], days: int = 30) -> List[Dict[str, Any]]:
    """
    Fill missing dates with zero values for continuous chart display.

    Args:
        data: List of {date, value} dicts from database
        days: Number of days to include

    Returns:
        List of {date, value} dicts with all dates filled
    """
    today = datetime.utcnow().date()

    # Create a map from existing data
    date_map = {item["date"]: item["value"] for item in data}

    # Generate all dates for the range
    result = []
    for i in range(days - 1, -1, -1):
        date = (today - timedelta(days=i)).isoformat()
        result.append({
            "date": date,
            "value": date_map.get(date, 0)
        })

    return result
