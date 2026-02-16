"""
Analytics DTOs.

Pydantic models for Analytics/Insights API responses.
Uses camelCase aliases for frontend compatibility.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class StatItemDTO(BaseModel):
    """
    DTO for a single KPI stat item.

    Matches Insights.tsx frontend component requirements.
    Uses camelCase aliases for JSON serialization.
    """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    label: str = Field(..., description="Display label for the stat")
    value: str = Field(..., description="Formatted value string (e.g., '1.2M', '3.8%')")
    trend: str = Field(..., description="Trend indicator (e.g., '+12%', 'ROI +200%')")
    icon: str = Field(..., description="Material icon name for display")
    highlight: Optional[bool] = Field(None, description="Whether to highlight this stat")


class ChartPointDTO(BaseModel):
    """
    DTO for a single chart data point.

    Used for time-series activity chart data.
    """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    date: str = Field(..., description="Date in YYYY-MM-DD format")
    value: int = Field(..., description="Count value for this date")


class TopAssetDTO(BaseModel):
    """
    DTO for a top-performing asset.

    Combines real asset data with mocked performance score.
    """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str = Field(..., description="Asset UUID as string")
    name: str = Field(..., description="Display name (title)")
    created: str = Field(..., description="Creation timestamp ISO format")
    platform: str = Field(..., description="Platform indicator (e.g., 'AI Generated')")
    type: str = Field(..., description="Asset type display name (e.g., 'Product Image')")
    score: int = Field(..., description="Mock performance score (0-100)")
    img: Optional[str] = Field(None, description="Asset image URL if available")
