"""
Product Package Routes

API endpoints for product package generation and management.
"""

import logging
import uuid
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.product_packages import (
    ProductPackageRequest,
    ProductPackageGenerateResponse,
    ProductPackageStatusResponse,
    ProductPackageResponse,
    RegenerateRequest,
    RegenerateResponse,
    ApproveRequest,
    ApproveResponse,
)
from app.application.orchestration.deep_orchestrator import DeepOrchestrator
from app.application.orchestration.hitl import HITLManager
from app.application.tools import ToolRegistry
from app.interface.dependencies.auth import get_current_user
from app.domain.entities.user import User
from app.infrastructure.database.connection import get_async_session
from app.infrastructure.repositories.product_package_repository import ProductPackageRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/product-packages", tags=["Product Packages"])


# Dependency injection
async def get_orchestrator(
    session: AsyncSession = Depends(get_async_session),
) -> DeepOrchestrator:
    """
    Get DeepOrchestrator instance.

    In production, this would be a singleton or managed by a container.
    """
    # TODO: Implement proper dependency injection
    # For now, create a simple instance
    from app.application.agents.copywriting_agent import CopywritingAgent
    from app.application.agents.image_agent import ImageAgent
    from app.application.tools.storage_tools import StorageTools

    tools = ToolRegistry.create_default(
        llm_client=None,  # TODO: inject
        video_asset_repository=None,  # TODO: inject
    )

    repository = ProductPackageRepository(session)

    # Register storage tools with repository
    tools.register("storage", StorageTools(repository))

    # Create agents
    copywriting_agent = CopywritingAgent()
    image_agent = ImageAgent()

    orchestrator = DeepOrchestrator(
        tools=tools,
        repository=repository,
        copywriting_agent=copywriting_agent,
        image_agent=image_agent,
    )

    return orchestrator


async def get_hitl_manager(
    session: AsyncSession = Depends(get_async_session),
) -> HITLManager:
    """Get HITLManager instance."""
    repository = ProductPackageRepository(session)
    return HITLManager(repository=repository)


@router.post("/generate", response_model=ProductPackageGenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_product_package(
    request: ProductPackageRequest,
    current_user: User = Depends(get_current_user),
    orchestrator: DeepOrchestrator = Depends(get_orchestrator),
):
    """
    Generate a new product package.

    Initiates an asynchronous workflow that:
    1. Analyzes the product image
    2. Generates copywriting (multiple variants)
    3. Generates images (multiple scenes)
    4. Generates video (with slideshow fallback)
    5. Runs QA checks
    6. Requests approval (if required)

    Returns immediately with workflow ID for tracking.
    Progress can be monitored via WebSocket events or GET /status/{workflow_id}.
    """
    try:
        logger.info(f"User {current_user.id} initiating product package generation")

        # Convert request to dict
        request_dict = {
            "image_url": str(request.image_url) if request.image_url else None,
            "image_asset_id": request.image_asset_id,
            "background": request.background,
            "options": request.options.model_dump(),
            "user_id": current_user.id,
        }

        # Start workflow (runs in background)
        result = await orchestrator.run(
            request=request_dict,
            user_id=current_user.id,
        )

        return ProductPackageGenerateResponse(**result)

    except Exception as e:
        logger.error(f"Product package generation failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start product package generation: {str(e)}",
        )


@router.get("/status/{workflow_id}", response_model=ProductPackageStatusResponse)
async def get_package_status(
    workflow_id: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get the current status of a product package workflow.

    Returns detailed status including:
    - Current stage and progress
    - Generated artifacts
    - Error messages (if any)
    """
    try:
        repository = ProductPackageRepository(session)
        package = await repository.get_by_workflow_id(workflow_id)

        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Workflow {workflow_id} not found",
            )

        # Check ownership
        if package.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        progress = package.progress or {}
        artifacts = package.artifacts or {}

        return ProductPackageStatusResponse(
            package_id=package.id,
            workflow_id=package.workflow_id,
            status=package.status,
            stage=package.stage,
            progress_percentage=progress.get("percentage", 0),
            current_step=progress.get("current_step", "unknown"),
            artifacts=artifacts,
            error=package.error_message,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get package status: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get package status: {str(e)}",
        )


@router.get("/{package_id}", response_model=ProductPackageResponse)
async def get_package_detail(
    package_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Get detailed information about a product package.

    Returns all available data including:
    - Product analysis
    - Generated copywriting versions
    - Generated images
    - Generated video
    - QA report
    """
    try:
        repository = ProductPackageRepository(session)
        package = await repository.get_by_id(package_id)

        if not package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Package {package_id} not found",
            )

        # Check ownership
        if package.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied",
            )

        # Check approval status if not completed
        if package.status == "approval_required":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Package requires approval before accessing details",
            )

        # TODO: Fetch actual artifacts from database
        # For now, return placeholder structure
        return ProductPackageResponse(
            package_id=package.id,
            workflow_id=package.workflow_id,
            status=package.status,
            stage=package.stage,
            analysis=package.analysis_data,
            copywriting_versions=[],
            images=[],
            video=None,
            qa_report=package.qa_report,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get package detail: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get package detail: {str(e)}",
        )


@router.post("/{package_id}/regenerate", response_model=RegenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def regenerate_package(
    package_id: uuid.UUID,
    request: RegenerateRequest,
    current_user: User = Depends(get_current_user),
    hitl_manager: HITLManager = Depends(get_hitl_manager),
):
    """
    Regenerate part or all of a product package.

    Allows selective regeneration of:
    - copywriting: Generate new copywriting variants
    - images: Generate new images
    - video: Generate a new video
    - all: Regenerate everything

    A new workflow is created for the regeneration.
    """
    try:
        logger.info(f"User {current_user.id} regenerating {request.target} for package {package_id}")

        result = await hitl_manager.regenerate(
            package_id=package_id,
            target=request.target,
            reason=request.reason,
        )

        return RegenerateResponse(
            package_id=package_id,
            workflow_id=result.get("workflow_id", str(uuid.uuid4())),
            target=request.target,
            status=result.get("status", "pending"),
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Regeneration failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate: {str(e)}",
        )


@router.post("/{package_id}/approve", response_model=ApproveResponse)
async def approve_package(
    package_id: uuid.UUID,
    request: ApproveRequest,
    current_user: User = Depends(get_current_user),
    hitl_manager: HITLManager = Depends(get_hitl_manager),
):
    """
    Approve or reject a product package.

    Used for HITL (Human-in-the-Loop) workflows:
    - approve: Mark package as completed
    - reject: Mark package as failed (allows regeneration)
    """
    try:
        logger.info(f"User {current_user.id} {request.decision}ing package {package_id}")

        if request.decision == "approve":
            result = await hitl_manager.approve(
                package_id=package_id,
                comment=request.comment,
            )
        else:  # reject
            result = await hitl_manager.reject(
                package_id=package_id,
                comment=request.comment,
            )

        return ApproveResponse(
            package_id=package_id,
            decision=request.decision,
            status=result["status"],
            comment=request.comment,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Approval failed: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process approval: {str(e)}",
        )
