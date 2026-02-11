"""
Product Package DTOs

Data transfer objects for product package API.
"""

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl, model_validator


class ProductPackageOptions(BaseModel):
    """Options for product package generation."""

    copy_variants: int = Field(default=2, ge=1, le=5, description="Number of copywriting variants")
    image_variants: int = Field(default=3, ge=1, le=8, description="Number of image variants")
    video_duration_sec: int = Field(default=15, ge=6, le=60, description="Video duration in seconds")
    require_approval: bool = Field(default=True, description="Whether manual approval is required")
    force_fallback_video: bool = Field(default=False, description="Force slideshow fallback for video")


class ProductPackageRequest(BaseModel):
    """Request to generate a product package."""

    image_url: Optional[HttpUrl] = Field(default=None, description="URL of product image")
    image_asset_id: Optional[UUID] = Field(default=None, description="Existing image asset ID")
    background: str = Field(..., min_length=1, max_length=4000, description="Product background context")
    options: ProductPackageOptions = Field(default_factory=ProductPackageOptions, description="Generation options")

    @model_validator(mode='after')
    def check_image_source(self):
        """Validate that exactly one image source is provided."""
        if bool(self.image_url) == bool(self.image_asset_id):
            raise ValueError('Exactly one of image_url or image_asset_id is required')
        return self


class ProductPackageGenerateResponse(BaseModel):
    """Response for product package generation initiation."""

    package_id: UUID = Field(..., description="Package ID")
    workflow_id: str = Field(..., description="Workflow ID for tracking")
    status: str = Field(..., description="Initial status")
    stage: str = Field(..., description="Initial stage")


class ProductPackageStatusResponse(BaseModel):
    """Response for product package status query."""

    package_id: UUID = Field(..., description="Package ID")
    workflow_id: str = Field(..., description="Workflow ID")
    status: Literal["pending", "running", "approval_required", "completed", "failed", "cancelled"] = Field(
        ..., description="Current status"
    )
    stage: Literal["init", "analysis", "copywriting", "image_generation", "video_generation", "qa_review", "approval", "done"] = Field(
        ..., description="Current stage"
    )
    progress_percentage: int = Field(..., ge=0, le=100, description="Progress percentage")
    current_step: str = Field(..., description="Current step description")
    artifacts: dict = Field(default_factory=dict, description="Generated artifacts")
    error: Optional[str] = Field(default=None, description="Error message if failed")


class ArtifactDetail(BaseModel):
    """Detail of a generated artifact."""

    asset_id: str = Field(..., description="Asset ID")
    url: Optional[str] = Field(default=None, description="Asset URL")
    label: Optional[str] = Field(default=None, description="Asset label")


class CopywritingArtifact(ArtifactDetail):
    """Copywriting artifact detail."""

    channel: str = Field(..., description="Channel (product_page, social_post, ad_short)")
    content: Optional[str] = Field(default=None, description="Copywriting content")


class ImageArtifact(ArtifactDetail):
    """Image artifact detail."""

    scene: str = Field(..., description="Scene type (hero, lifestyle, detail)")


class VideoArtifact(ArtifactDetail):
    """Video artifact detail."""

    is_fallback: bool = Field(default=False, description="Whether slideshow fallback was used")
    duration: Optional[int] = Field(default=None, description="Video duration in seconds")


class ProductPackageResponse(BaseModel):
    """Response for product package detail query."""

    package_id: UUID = Field(..., description="Package ID")
    workflow_id: str = Field(..., description="Workflow ID")
    status: str = Field(..., description="Current status")
    stage: str = Field(..., description="Current stage")
    analysis: Optional[dict] = Field(default=None, description="Product analysis data")
    copywriting_versions: list[CopywritingArtifact] = Field(default_factory=list, description="Copywriting artifacts")
    images: list[ImageArtifact] = Field(default_factory=list, description="Image artifacts")
    video: Optional[VideoArtifact] = Field(default=None, description="Video artifact")
    qa_report: Optional[dict] = Field(default=None, description="QA report")


class RegenerateRequest(BaseModel):
    """Request to regenerate part or all of a package."""

    target: Literal['copywriting', 'images', 'video', 'all'] = Field(
        ..., description="What to regenerate"
    )
    reason: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Reason for regeneration"
    )


class RegenerateResponse(BaseModel):
    """Response for regeneration initiation."""

    package_id: UUID = Field(..., description="Package ID")
    workflow_id: str = Field(..., description="New workflow ID")
    target: str = Field(..., description="Regeneration target")
    status: str = Field(..., description="Status")


class ApproveRequest(BaseModel):
    """Request to approve or reject a package."""

    decision: Literal['approve', 'reject'] = Field(..., description="Approval decision")
    comment: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Approval/rejection comment"
    )


class ApproveResponse(BaseModel):
    """Response for approval decision."""

    package_id: UUID = Field(..., description="Package ID")
    decision: str = Field(..., description="Decision made")
    status: str = Field(..., description="New status")
    comment: Optional[str] = Field(default=None, description="Comment")
