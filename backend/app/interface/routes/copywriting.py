"""
Copywriting API routes.

Provides REST endpoints for AI-powered copywriting generation.
"""
import logging
from uuid import uuid4

from fastapi import APIRouter, HTTPException, status

from app.application.agents.copywriting_agent import CopywritingAgent
from app.application.dtos.copywriting import (
    CopywritingRequest,
    CopywritingResponse,
    WorkflowStatusResponse,
    WorkflowCancelResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/copywriting", tags=["copywriting"])


@router.post(
    "/generate",
    response_model=CopywritingResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate product marketing copy",
    description="""
    Initiates AI-powered copywriting workflow for product marketing.
    
    The workflow progresses through 4 stages:
    1. **Plan** - Analyze product and create marketing outline
    2. **Draft** - Generate initial copy based on plan
    3. **Critique** - Self-review and suggest improvements
    4. **Finalize** - Produce polished final copy
    
    Progress is streamed via Socket.io `agent:thought` events.
    Final result is emitted via `agent:result` event.
    
    Returns immediately with workflow_id for tracking.
    """,
)
async def generate_copywriting(request: CopywritingRequest) -> CopywritingResponse:
    """
    Generate marketing copy for a product.
    
    Args:
        request: Product information and features
        
    Returns:
        Workflow ID and status for tracking
    """
    try:
        workflow_id = str(uuid4())
        
        # Create agent and start workflow asynchronously
        agent = CopywritingAgent()
        await agent.run_async(
            product_name=request.product_name,
            features=request.features,
            brand_guidelines=request.brand_guidelines,
            workflow_id=workflow_id,
        )
        
        logger.info(f"Started copywriting workflow: {workflow_id}")
        
        return CopywritingResponse(
            workflow_id=workflow_id,
            status="started",
            message="Copywriting workflow initiated. Listen for agent:thought events.",
        )
        
    except Exception as e:
        logger.error(f"Failed to start copywriting workflow: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start workflow: {str(e)}"
        )


@router.get(
    "/status/{workflow_id}",
    response_model=WorkflowStatusResponse,
    summary="Get workflow status",
    description="Query the current status and stage of a copywriting workflow.",
)
async def get_workflow_status(workflow_id: str) -> WorkflowStatusResponse:
    """
    Get the current status of a workflow.
    
    Args:
        workflow_id: Workflow ID to query
        
    Returns:
        Current workflow status and stage
    """
    workflow_state = CopywritingAgent.get_workflow_status(workflow_id)
    
    if workflow_state is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found"
        )
    
    return WorkflowStatusResponse(
        workflow_id=workflow_id,
        status=workflow_state.get("status", "unknown"),
        current_stage=workflow_state.get("current_stage"),
        final_copy=workflow_state.get("state", {}).get("final_copy"),
    )


@router.delete(
    "/cancel/{workflow_id}",
    response_model=WorkflowCancelResponse,
    summary="Cancel a running workflow",
    description="Cancel a workflow that is currently running.",
)
async def cancel_workflow(workflow_id: str) -> WorkflowCancelResponse:
    """
    Cancel a running workflow.
    
    Args:
        workflow_id: Workflow ID to cancel
        
    Returns:
        Cancellation result
    """
    cancelled = CopywritingAgent.cancel_workflow(workflow_id)
    
    if not cancelled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Workflow {workflow_id} not found or already completed"
        )
    
    return WorkflowCancelResponse(
        workflow_id=workflow_id,
        cancelled=True,
        message="Workflow cancelled successfully",
    )

