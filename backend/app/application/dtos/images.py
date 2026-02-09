"""
Image Generation DTOs.

Pydantic models for image generation API request/response.
"""

from typing import Optional

from pydantic import BaseModel, Field


class ImageGenerationAPIRequest(BaseModel):
    """Request model for image generation."""
    
    prompt: str = Field(
        ...,
        description="Text description of the image to generate",
        min_length=1,
        max_length=2000
    )
    width: int = Field(
        default=512,
        description="Image width in pixels",
        ge=256,
        le=2048
    )
    height: int = Field(
        default=512,
        description="Image height in pixels",
        ge=256,
        le=2048
    )
    
    model_config = {"extra": "forbid"}


class ImageGenerationAPIResponse(BaseModel):
    """Response model for image generation initiation."""
    
    workflow_id: str = Field(..., description="Unique workflow ID for tracking")
    status: str = Field(..., description="Workflow status (starting)")
    message: str = Field(..., description="Status message")


class ImageStatusResponse(BaseModel):
    """Response model for image workflow status query."""
    
    workflow_id: str = Field(..., description="Unique workflow ID")
    status: str = Field(
        ..., 
        description="Workflow status (running, completed, failed, cancelled)"
    )
    current_stage: Optional[str] = Field(
        None, 
        description="Current stage (optimize_prompt, generate_image, persist_asset, completed)"
    )
    image_url: Optional[str] = Field(
        None, 
        description="Generated image URL if completed"
    )
    optimized_prompt: Optional[str] = Field(
        None, 
        description="DeepSeek optimized prompt"
    )
    asset_id: Optional[str] = Field(
        None, 
        description="Persisted asset UUID"
    )
    error: Optional[str] = Field(
        None, 
        description="Error message if failed"
    )


class ImageCancelResponse(BaseModel):
    """Response model for image workflow cancellation."""
    
    workflow_id: str = Field(..., description="Unique workflow ID")
    cancelled: bool = Field(..., description="Whether workflow was cancelled")
    message: str = Field(..., description="Cancellation message")
