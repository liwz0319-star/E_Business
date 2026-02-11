"""
Human-in-the-Loop (HITL) Support

Provides utilities for HITL workflows including approval, rejection, and regeneration.
"""

import logging
from typing import Dict, Any, Optional
from uuid import UUID

from app.application.orchestration.deep_orchestrator import DeepOrchestrator
from app.infrastructure.repositories.product_package_repository import ProductPackageRepository

logger = logging.getLogger(__name__)


class HITLManager:
    """
    Manages Human-in-the-Loop workflows.

    Handles:
    - Approval requests
    - Approval decisions
    - Rejection handling
    - Regeneration triggers
    """

    def __init__(
        self,
        repository: ProductPackageRepository,
        orchestrator: Optional[DeepOrchestrator] = None,
    ):
        """
        Initialize HITL manager.

        Args:
            repository: ProductPackageRepository instance
            orchestrator: Optional DeepOrchestrator for regeneration
        """
        self.repository = repository
        self.orchestrator = orchestrator

    async def request_approval(
        self,
        package_id: UUID,
        reason: str = "manual_approval_required",
        qa_score: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Request manual approval for a package.

        Args:
            package_id: Package UUID
            reason: Reason for approval request
            qa_score: QA score (if applicable)

        Returns:
            Updated package data
        """
        logger.info(f"Requesting approval for package {package_id}: {reason}")

        package = await self.repository.get_by_id(package_id)
        if not package:
            raise ValueError(f"Package {package_id} not found")

        # Update status
        updated = await self.repository.update_status(
            package_id=package_id,
            status="approval_required",
            stage="approval",
            progress={"percentage": 95, "current_step": "waiting_approval"},
        )

        return {
            "package_id": updated.id,
            "status": updated.status,
            "stage": updated.stage,
            "reason": reason,
            "qa_score": qa_score,
        }

    async def approve(
        self,
        package_id: UUID,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Approve a package.

        Args:
            package_id: Package UUID
            comment: Optional approval comment

        Returns:
            Updated package data
        """
        logger.info(f"Approving package {package_id}")

        package = await self.repository.get_by_id(package_id)
        if not package:
            raise ValueError(f"Package {package_id} not found")

        if package.status != "approval_required":
            raise ValueError(f"Package {package_id} is not awaiting approval")

        # Update approval status
        await self.repository.update_approval(package_id, "approved")

        # Mark as completed
        updated = await self.repository.update_status(
            package_id=package_id,
            status="completed",
            stage="done",
            progress={"percentage": 100, "current_step": "approved"},
        )

        logger.info(f"Package {package_id} approved and completed")

        return {
            "package_id": updated.id,
            "status": updated.status,
            "stage": updated.stage,
            "comment": comment,
        }

    async def reject(
        self,
        package_id: UUID,
        comment: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Reject a package.

        Args:
            package_id: Package UUID
            comment: Optional rejection comment

        Returns:
            Updated package data
        """
        logger.info(f"Rejecting package {package_id}")

        package = await self.repository.get_by_id(package_id)
        if not package:
            raise ValueError(f"Package {package_id} not found")

        if package.status != "approval_required":
            raise ValueError(f"Package {package_id} is not awaiting approval")

        # Update approval status
        await self.repository.update_approval(package_id, "rejected")

        # Mark as failed
        updated = await self.repository.update_status(
            package_id=package_id,
            status="failed",
            stage="approval",
            progress=package.progress,
            error_message=f"Rejected: {comment or 'No comment provided'}",
        )

        logger.info(f"Package {package_id} rejected")

        return {
            "package_id": updated.id,
            "status": updated.status,
            "stage": updated.stage,
            "comment": comment,
        }

    async def regenerate(
        self,
        package_id: UUID,
        target: str,
        reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Regenerate part or all of a package.

        Args:
            package_id: Package UUID
            target: What to regenerate ('copywriting', 'images', 'video', 'all')
            reason: Optional reason for regeneration

        Returns:
            New workflow data
        """
        logger.info(f"Regenerating {target} for package {package_id}")

        if not self.orchestrator:
            raise RuntimeError("Orchestrator not configured for regeneration")

        package = await self.repository.get_by_id(package_id)
        if not package:
            raise ValueError(f"Package {package_id} not found")

        # Get original request
        input_data = package.input_data or {}

        # Trigger new workflow
        # Note: This is a simplified version - in production you'd want to:
        # 1. Clone the package
        # 2. Only regenerate specified parts
        # 3. Merge results with existing assets

        logger.warning(f"Full regeneration triggered for {target} - consider partial regeneration in production")

        # For now, return a mock response
        return {
            "package_id": package_id,
            "target": target,
            "status": "regeneration_initiated",
            "reason": reason,
        }
