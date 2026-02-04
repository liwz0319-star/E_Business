"""
Copywriting DTOs.

Pydantic models for copywriting API request/response.
"""

from typing import Optional

from pydantic import BaseModel, Field


class CopywritingRequest(BaseModel):
    """Request model for copywriting generation."""
    
    product_name: str = Field(
        ...,
        description="Name of the product",
        max_length=200
    )
    features: list[str] = Field(
        default_factory=list,
        description="Product features",
        min_length=1
    )
    brand_guidelines: Optional[str] = Field(
        None,
        description="Brand guidelines",
        max_length=1000
    )
    
    model_config = {"extra": "forbid"}


class CopywritingResponse(BaseModel):
    """Response model for copywriting generation."""
    
    workflow_id: str = Field(..., description="Unique workflow ID")
    status: str = Field(..., description="Workflow status")
    message: str = Field(..., description="Status message")


class WorkflowStatusResponse(BaseModel):
    """Response model for workflow status query."""
    
    workflow_id: str = Field(..., description="Unique workflow ID")
    status: str = Field(..., description="Workflow status (running, completed, failed, cancelled)")
    current_stage: Optional[str] = Field(None, description="Current stage (plan, draft, critique, finalize, completed)")
    final_copy: Optional[str] = Field(None, description="Final copy if workflow completed")


class WorkflowCancelResponse(BaseModel):
    """Response model for workflow cancellation."""
    
    workflow_id: str = Field(..., description="Unique workflow ID")
    cancelled: bool = Field(..., description="Whether workflow was cancelled")
    message: str = Field(..., description="Cancellation message")

