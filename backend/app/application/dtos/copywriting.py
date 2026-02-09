"""
Copywriting DTOs.

Pydantic models for copywriting API request/response.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


def _to_camel(field_name: str) -> str:
    """Convert snake_case field names to camelCase aliases."""
    parts = field_name.split("_")
    return parts[0] + "".join(word.capitalize() for word in parts[1:])


class CopywritingRequest(BaseModel):
    """Request model for copywriting generation."""
    
    product_name: str = Field(
        ...,
        description="Name of the product",
        max_length=200
    )
    features: list[str] = Field(
        ...,
        description="Product features",
        min_length=1
    )
    brand_guidelines: Optional[str] = Field(
        None,
        description="Brand guidelines",
        max_length=1000
    )
    
    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
        extra="forbid",
    )


class CopywritingResponse(BaseModel):
    """Response model for copywriting generation."""
    
    workflow_id: str = Field(..., description="Unique workflow ID")
    status: str = Field(..., description="Workflow status")
    message: str = Field(..., description="Status message")

    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
    )


class WorkflowStatusResponse(BaseModel):
    """Response model for workflow status query."""
    
    workflow_id: str = Field(..., description="Unique workflow ID")
    status: str = Field(..., description="Workflow status (running, completed, failed, cancelled)")
    current_stage: Optional[str] = Field(None, description="Current stage (plan, draft, critique, finalize, completed)")
    final_copy: Optional[str] = Field(None, description="Final copy if workflow completed")
    error: Optional[str] = Field(None, description="Error message if failed")

    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
    )


class WorkflowCancelResponse(BaseModel):
    """Response model for workflow cancellation."""
    
    workflow_id: str = Field(..., description="Unique workflow ID")
    cancelled: bool = Field(..., description="Whether workflow was cancelled")
    message: str = Field(..., description="Cancellation message")

    model_config = ConfigDict(
        alias_generator=_to_camel,
        populate_by_name=True,
    )

