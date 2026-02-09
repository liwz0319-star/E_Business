"""
Image Generation API Routes.

Endpoints for image generation workflow.
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status

from app.application.agents.image_agent import ImageAgent
from app.application.dtos.images import (
    ImageGenerationAPIRequest,
    ImageGenerationAPIResponse,
    ImageStatusResponse,
    ImageCancelResponse,
)


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/images", tags=["images"])

# Shared agent instance
_agent: Optional[ImageAgent] = None


def get_agent() -> ImageAgent:
    """Get or create shared ImageAgent instance."""
    global _agent
    if _agent is None:
        _agent = ImageAgent()
    return _agent


@router.post(
    "/generate",
    response_model=ImageGenerationAPIResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate Image",
    description="Start an async image generation workflow using AI"
)
async def generate_image(
    request: ImageGenerationAPIRequest,
) -> ImageGenerationAPIResponse:
    """
    Generate an image from a text description.
    
    The workflow runs asynchronously:
    1. DeepSeek optimizes the prompt
    2. MCP ImageGenerator creates the image
    3. Image metadata is persisted to database
    
    Connect to Socket.io to receive real-time updates:
    - agent:thought - AI thinking process
    - agent:tool_call - Tool invocation status
    - agent:result - Final result with image URL
    - agent:error - Error notifications
    
    Args:
        request: Image generation request with prompt and dimensions
        
    Returns:
        Workflow ID for tracking via status endpoint or Socket.io
    """
    logger.info(f"Received image generation request: {request.prompt[:50]}...")
    
    try:
        agent = get_agent()
        workflow_id = await agent.run_async(
            prompt=request.prompt,
            width=request.width,
            height=request.height,
        )
        
        logger.info(f"Started image workflow: {workflow_id}")
        
        return ImageGenerationAPIResponse(
            workflow_id=workflow_id,
            status="starting",
            message="Image generation workflow started. Connect to Socket.io for updates."
        )
        
    except Exception as e:
        logger.error(f"Failed to start image generation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start image generation: {str(e)}"
        )


@router.get(
    "/status/{workflow_id}",
    response_model=ImageStatusResponse,
    summary="Get Workflow Status",
    description="Query the current status of an image generation workflow"
)
async def get_workflow_status(workflow_id: str) -> ImageStatusResponse:
    """
    Get the current status of an image generation workflow.
    
    Args:
        workflow_id: The workflow ID returned from generate endpoint
        
    Returns:
        Current workflow status including stage and results if available
    """
    status_data = ImageAgent.get_workflow_status(workflow_id)
    
    if status_data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )
    
    state = status_data.get("state", {})
    
    return ImageStatusResponse(
        workflow_id=workflow_id,
        status=status_data.get("status", "unknown"),
        current_stage=status_data.get("current_stage"),
        image_url=state.get("image_url") if state.get("image_url") else None,
        optimized_prompt=state.get("optimized_prompt") if state.get("optimized_prompt") else None,
        asset_id=state.get("asset_id"),
        error=status_data.get("error"),
    )


@router.post(
    "/cancel/{workflow_id}",
    response_model=ImageCancelResponse,
    summary="Cancel Workflow",
    description="Cancel a running image generation workflow"
)
async def cancel_workflow(workflow_id: str) -> ImageCancelResponse:
    """
    Cancel a running image generation workflow.
    
    Args:
        workflow_id: The workflow ID to cancel
        
    Returns:
        Cancellation result
    """
    cancelled = ImageAgent.cancel_workflow(workflow_id)
    
    if cancelled:
        logger.info(f"Cancelled workflow: {workflow_id}")
        return ImageCancelResponse(
            workflow_id=workflow_id,
            cancelled=True,
            message="Workflow cancelled successfully"
        )
    else:
        return ImageCancelResponse(
            workflow_id=workflow_id,
            cancelled=False,
            message="Workflow not found or already completed"
        )
