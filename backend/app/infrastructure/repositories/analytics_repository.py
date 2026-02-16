"""
Analytics Repository Implementation.

SQLAlchemy-based implementation for analytics data aggregation.
"""
from datetime import datetime, timedelta
from typing import List, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import VideoAssetModel, ProductPackageModel


class PostgresAnalyticsRepository:
    """
    SQLAlchemy repository for analytics data aggregation.

    Provides methods for counting projects/assets and
    aggregating daily activity data.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def count_projects(self, user_id: UUID) -> int:
        """
        Count total projects for a user.

        Args:
            user_id: The user's UUID

        Returns:
            Total count of ProductPackage records
        """
        result = await self._session.execute(
            select(func.count(ProductPackageModel.id)).where(
                ProductPackageModel.user_id == user_id
            )
        )
        return result.scalar() or 0

    async def count_assets(self, user_id: UUID) -> int:
        """
        Count total assets for a user.

        Args:
            user_id: The user's UUID

        Returns:
            Total count of VideoAsset records
        """
        result = await self._session.execute(
            select(func.count(VideoAssetModel.id)).where(
                VideoAssetModel.user_id == user_id
            )
        )
        return result.scalar() or 0

    async def get_daily_activity(
        self, user_id: UUID, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get daily asset generation counts for the last N days.

        Uses both VideoAssetModel and ProductPackageModel for activity tracking.

        Args:
            user_id: The user's UUID
            days: Number of days to look back

        Returns:
            List of dicts with 'date' (YYYY-MM-DD) and 'value' (count)
        """
        start_date = datetime.utcnow().date() - timedelta(days=days)

        # Query daily asset counts
        result = await self._session.execute(
            select(
                func.date(VideoAssetModel.created_at).label("date"),
                func.count(VideoAssetModel.id).label("value")
            )
            .where(
                and_(
                    VideoAssetModel.user_id == user_id,
                    func.date(VideoAssetModel.created_at) >= start_date
                )
            )
            .group_by(func.date(VideoAssetModel.created_at))
            .order_by(func.date(VideoAssetModel.created_at))
        )

        return [
            {"date": row.date.isoformat() if hasattr(row.date, 'isoformat') else str(row.date), "value": row.value}
            for row in result.all()
        ]

    async def get_recent_assets(
        self, user_id: UUID, limit: int = 5
    ) -> List[VideoAssetModel]:
        """
        Get most recent assets for a user.

        Args:
            user_id: The user's UUID
            limit: Maximum number of assets to return

        Returns:
            List of VideoAssetModel instances
        """
        result = await self._session.execute(
            select(VideoAssetModel)
            .where(VideoAssetModel.user_id == user_id)
            .order_by(VideoAssetModel.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
