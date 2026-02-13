"""
Asset Gallery DTOs.

Pydantic models for Asset Gallery API request/response.
Uses camelCase aliases for frontend compatibility.
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel


class GalleryAssetDTO(BaseModel):
    """
    DTO for a single asset in the gallery response.

    Includes all fields required by Gallery.tsx frontend component.
    Uses camelCase aliases for JSON serialization.
    """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str = Field(..., description="Asset UUID as string")
    title: Optional[str] = Field(None, description="Display title")
    type: str = Field(..., description="Frontend category: Product Images, Ad Videos, Marketing Copy")
    tag: str = Field(..., description="Short tag: IMG, VIDEO, COPY, EMAIL")
    meta: str = Field(..., description="Meta information string")
    url: Optional[str] = Field(None, description="Asset URL (null for text assets)")
    content: Optional[str] = Field(None, description="Text content for copy assets")
    is_vertical: bool = Field(..., description="Whether asset is vertically oriented")
    is_text: bool = Field(..., description="Whether this is a text asset")
    duration: Optional[str] = Field(None, description="Video duration if applicable")
    created_at: datetime = Field(..., description="Creation timestamp")


class AssetListResponseDTO(BaseModel):
    """
    DTO for paginated asset list response.

    Contains list of assets and pagination metadata.
    """
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: List[GalleryAssetDTO] = Field(..., description="List of assets")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")


class AssetQueryParams(BaseModel):
    """Query parameters for asset listing."""
    type: Optional[str] = Field(None, description="Filter by asset type: image, video, text")
    q: Optional[str] = Field(None, description="Search query for title/prompt")
    page: int = Field(1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(20, ge=1, le=100, description="Items per page")


class AssetUpdateRequest(BaseModel):
    """Request body for updating an asset."""
    title: str = Field(..., min_length=1, max_length=255, description="New title value")
