"""
Deep Orchestrator

Main orchestrator for product package generation workflow.
Coordinates all sub-agents and manages workflow state.
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from uuid import UUID

from app.application.agents.product_analysis_agent import ProductAnalysisAgent
from app.application.agents.subagents import CopywritingSubagent, ImageSubagent
from app.application.agents.video_generation_agent import VideoGenerationAgent
from app.application.agents.qa_agent import QAAgent
from app.application.tools import ToolRegistry
from app.infrastructure.repositories.product_package_repository import ProductPackageRepository
from app.interface.ws.socket_manager import socket_manager

logger = logging.getLogger(__name__)


class DeepOrchestrator:
    """
    Main orchestrator for product package generation.

    Workflow:
    1. Create workspace and package record
    2. Run product analysis
    3. Generate copywriting
    4. Generate images
    5. Generate video (with slideshow fallback)
    6. Run QA checks
    7. Request approval if required
    8. Finalize and complete

    State Machine:
    - pending/init -> running/analysis
    - running/analysis -> running/copywriting
    - running/copywriting -> running/image_generation
    - running/image_generation -> running/video_generation
    - running/video_generation -> running/qa_review
    - running/qa_review -> approval_required/approval OR completed/done
    """

    # Stage definitions
    STAGES = {
        "init": 0,
        "analysis": 10,
        "copywriting": 25,
        "image_generation": 45,
        "video_generation": 65,
        "qa_review": 85,
        "approval": 95,
        "done": 100,
    }

    def __init__(
        self,
        tools: ToolRegistry,
        repository: ProductPackageRepository,
        copywriting_agent=None,
        image_agent=None,
    ):
        """
        Initialize DeepOrchestrator.

        Args:
            tools: ToolRegistry instance
            repository: ProductPackageRepository instance
            copywriting_agent: Existing CopywritingAgent (for subagent wrapper)
            image_agent: Existing ImageAgent (for subagent wrapper)
        """
        self.tools = tools
        self.repository = repository

        # Initialize sub-agents
        self.analysis_agent = ProductAnalysisAgent(tools)
        self.copywriting_subagent = CopywritingSubagent(copywriting_agent, tools) if copywriting_agent else None
        self.image_subagent = ImageSubagent(image_agent, tools) if image_agent else None
        self.video_agent = VideoGenerationAgent(tools)
        self.qa_agent = QAAgent(tools)

        # Storage tools wrapper
        self.storage = tools.storage

    async def run(
        self,
        request: Dict[str, Any],
        user_id: UUID,
    ) -> Dict[str, Any]:
        """
        Execute the full product package generation workflow.

        Args:
            request: Product package request:
            {
                "image_url": str | None,
                "image_asset_id": UUID | None,
                "background": str,
                "options": {...}
            }
            user_id: User UUID

        Returns:
            Workflow result:
            {
                "package_id": UUID,
                "workflow_id": str,
                "status": str,
                "stage": str
            }
        """
        # Generate workflow ID
        workflow_id = str(uuid.uuid4())

        logger.info(f"Starting workflow {workflow_id} for user {user_id}")

        try:
            # Step 1: Initialize workspace and package
            package_data = await self._initialize_workflow(
                workflow_id=workflow_id,
                user_id=user_id,
                request=request,
            )
            package_id = package_data["package_id"]

            # Step 2: Product Analysis
            analysis = await self._run_analysis(
                package_id=package_id,
                workflow_id=workflow_id,
                request=request,
            )

            # Step 3: Copywriting Generation
            copy_assets = await self._run_copywriting(
                package_id=package_id,
                workflow_id=workflow_id,
                analysis=analysis,
                request=request,
            )

            # Step 4: Image Generation
            image_assets = await self._run_image_generation(
                package_id=package_id,
                workflow_id=workflow_id,
                analysis=analysis,
                request=request,
            )

            # Step 5: Video Generation
            video_asset = await self._run_video_generation(
                package_id=package_id,
                workflow_id=workflow_id,
                analysis=analysis,
                image_assets=image_assets,
                request=request,
            )

            # Step 6: QA Review
            qa_report = await self._run_qa_review(
                package_id=package_id,
                workflow_id=workflow_id,
                analysis=analysis,
                copy_assets=copy_assets,
                image_assets=image_assets,
                video_asset=video_asset,
            )

            # Step 7: Approval or Complete
            options = request.get("options", {})
            require_approval = options.get("require_approval", True)

            if require_approval:
                await self._request_approval(
                    package_id=package_id,
                    workflow_id=workflow_id,
                    qa_report=qa_report,
                )
                # Stop here - wait for manual approval
                return {
                    "package_id": package_id,
                    "workflow_id": workflow_id,
                    "status": "approval_required",
                    "stage": "approval",
                }
            else:
                await self._finalize_completed(
                    package_id=package_id,
                    workflow_id=workflow_id,
                )
                return {
                    "package_id": package_id,
                    "workflow_id": workflow_id,
                    "status": "completed",
                    "stage": "done",
                }

        except Exception as e:
            logger.error(f"Workflow {workflow_id} failed: {str(e)}", exc_info=True)
            await self._handle_failure(workflow_id, str(e))
            raise

    async def _initialize_workflow(
        self,
        workflow_id: str,
        user_id: UUID,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Initialize workspace and package record."""
        logger.info(f"[{workflow_id}] Initializing workspace")

        # Create workspace directory
        workspace = self.tools.filesystem.create_workspace(workflow_id)
        logger.info(f"[{workflow_id}] Workspace created: {workspace}")

        # Save input data
        input_data = {
            "image_url": request.get("image_url"),
            "image_asset_id": str(request.get("image_asset_id")) if request.get("image_asset_id") else None,
            "background": request.get("background"),
            "options": request.get("options"),
        }

        self.tools.filesystem.write_json(
            f"{workspace}/input/image_source.json",
            input_data,
        )

        # Create package record
        package_data = await self.storage.create_package({
            "workflow_id": workflow_id,
            "user_id": user_id,
            "status": "running",
            "stage": "init",
            "input_data": input_data,
            "progress": {"percentage": 0, "current_step": "init"},
        })

        await self._emit_progress(
            workflow_id,
            "init",
            0,
            "Workflow initialized",
        )

        return package_data

    async def _run_analysis(
        self,
        package_id: UUID,
        workflow_id: str,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run product analysis stage."""
        logger.info(f"[{workflow_id}] Running product analysis")

        await self._emit_progress(
            workflow_id,
            "analysis",
            self.STAGES["analysis"],
            "Analyzing product",
        )

        workspace = self.tools.filesystem.get_workspace_path(workflow_id)

        # Update package status
        await self.storage.update_package_status(
            package_id=package_id,
            status="running",
            stage="analysis",
            progress={"percentage": self.STAGES["analysis"], "current_step": "analysis"},
        )

        # Run analysis agent
        analysis = await self.analysis_agent.run(
            request=request,
            workspace=workspace,
        )

        # Save analysis to package
        await self.storage.update_analysis(package_id, analysis)

        logger.info(f"[{workflow_id}] Analysis complete")
        return analysis

    async def _run_copywriting(
        self,
        package_id: UUID,
        workflow_id: str,
        analysis: Dict[str, Any],
        request: Dict[str, Any],
    ) -> list[Dict[str, Any]]:
        """Run copywriting generation stage."""
        logger.info(f"[{workflow_id}] Running copywriting generation")

        await self._emit_progress(
            workflow_id,
            "copywriting",
            self.STAGES["copywriting"],
            "Generating copywriting",
        )

        workspace = self.tools.filesystem.get_workspace_path(workflow_id)

        await self.storage.update_package_status(
            package_id=package_id,
            status="running",
            stage="copywriting",
            progress={"percentage": self.STAGES["copywriting"], "current_step": "copywriting"},
        )

        # Run copywriting subagent
        copy_assets = await self.copywriting_subagent.run(
            analysis=analysis,
            request=request,
            workspace=workspace,
        )

        # Link assets to package
        for asset in copy_assets:
            await self.storage.link_asset(
                package_id=package_id,
                artifact_type="copywriting",
                artifact_id=asset["asset_id"],
            )
            await self._emit_artifact(
                workflow_id,
                "copywriting",
                asset["asset_id"],
                asset.get("path", ""),
                asset.get("channel", ""),
            )

        logger.info(f"[{workflow_id}] Copywriting complete: {len(copy_assets)} assets")
        return copy_assets

    async def _run_image_generation(
        self,
        package_id: UUID,
        workflow_id: str,
        analysis: Dict[str, Any],
        request: Dict[str, Any],
    ) -> list[Dict[str, Any]]:
        """Run image generation stage."""
        logger.info(f"[{workflow_id}] Running image generation")

        await self._emit_progress(
            workflow_id,
            "image_generation",
            self.STAGES["image_generation"],
            "Generating images",
        )

        workspace = self.tools.filesystem.get_workspace_path(workflow_id)

        await self.storage.update_package_status(
            package_id=package_id,
            status="running",
            stage="image_generation",
            progress={"percentage": self.STAGES["image_generation"], "current_step": "image_generation"},
        )

        # Run image subagent
        image_assets = await self.image_subagent.run(
            analysis=analysis,
            request=request,
            workspace=workspace,
        )

        # Link assets to package
        for asset in image_assets:
            await self.storage.link_asset(
                package_id=package_id,
                artifact_type="images",
                artifact_id=asset["asset_id"],
            )
            await self._emit_artifact(
                workflow_id,
                "image",
                asset["asset_id"],
                asset.get("url", ""),
                asset.get("label", ""),
            )

        logger.info(f"[{workflow_id}] Image generation complete: {len(image_assets)} assets")
        return image_assets

    async def _run_video_generation(
        self,
        package_id: UUID,
        workflow_id: str,
        analysis: Dict[str, Any],
        image_assets: list[Dict[str, Any]],
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run video generation stage."""
        logger.info(f"[{workflow_id}] Running video generation")

        await self._emit_progress(
            workflow_id,
            "video_generation",
            self.STAGES["video_generation"],
            "Generating video",
        )

        workspace = self.tools.filesystem.get_workspace_path(workflow_id)

        await self.storage.update_package_status(
            package_id=package_id,
            status="running",
            stage="video_generation",
            progress={"percentage": self.STAGES["video_generation"], "current_step": "video_generation"},
        )

        # Run video agent
        video_asset = await self.video_agent.run(
            analysis=analysis,
            image_assets=image_assets,
            request=request,
            workspace=workspace,
        )

        # Link asset to package
        await self.storage.link_asset(
            package_id=package_id,
            artifact_type="video",
            artifact_id=video_asset["asset_id"],
        )
        await self._emit_artifact(
            workflow_id,
            "video",
            video_asset["asset_id"],
            video_asset.get("url", ""),
            "product_video",
        )

        logger.info(f"[{workflow_id}] Video generation complete")
        return video_asset

    async def _run_qa_review(
        self,
        package_id: UUID,
        workflow_id: str,
        analysis: Dict[str, Any],
        copy_assets: list[Dict[str, Any]],
        image_assets: list[Dict[str, Any]],
        video_asset: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run QA review stage."""
        logger.info(f"[{workflow_id}] Running QA review")

        await self._emit_progress(
            workflow_id,
            "qa_review",
            self.STAGES["qa_review"],
            "Running quality checks",
        )

        workspace = self.tools.filesystem.get_workspace_path(workflow_id)

        await self.storage.update_package_status(
            package_id=package_id,
            status="running",
            stage="qa_review",
            progress={"percentage": self.STAGES["qa_review"], "current_step": "qa_review"},
        )

        # Run QA agent
        qa_report = await self.qa_agent.run(
            analysis=analysis,
            copy_assets=copy_assets,
            image_assets=image_assets,
            video_asset=video_asset,
            workspace=workspace,
        )

        # Save QA report to package
        await self.storage.update_qa_report(package_id, qa_report)

        logger.info(f"[{workflow_id}] QA review complete: score={qa_report['score']:.2f}")
        return qa_report

    async def _request_approval(
        self,
        package_id: UUID,
        workflow_id: str,
        qa_report: Dict[str, Any],
    ) -> None:
        """Request manual approval."""
        logger.info(f"[{workflow_id}] Requesting approval")

        await self.storage.update_package_status(
            package_id=package_id,
            status="approval_required",
            stage="approval",
            progress={"percentage": self.STAGES["approval"], "current_step": "waiting_approval"},
        )

        await self._emit_approval_required(
            workflow_id,
            package_id,
            qa_report.get("score", 0.0),
        )

    async def _finalize_completed(
        self,
        package_id: UUID,
        workflow_id: str,
    ) -> None:
        """Finalize package as completed."""
        logger.info(f"[{workflow_id}] Finalizing as completed")

        await self.storage.update_package_status(
            package_id=package_id,
            status="completed",
            stage="done",
            progress={"percentage": 100, "current_step": "completed"},
        )

        await self._emit_progress(
            workflow_id,
            "done",
            100,
            "Workflow completed",
        )

    async def _handle_failure(
        self,
        workflow_id: str,
        error_message: str,
    ) -> None:
        """Handle workflow failure."""
        logger.error(f"[{workflow_id}] Handling failure: {error_message}")

        # Get package by workflow_id
        package = await self.repository.get_by_workflow_id(workflow_id)
        if package:
            await self.storage.update_package_status(
                package_id=package.id,
                status="failed",
                stage=package.stage,
                progress=package.progress,
                error_message=error_message,
            )

    async def _emit_progress(
        self,
        workflow_id: str,
        stage: str,
        percentage: int,
        current_step: str,
    ) -> None:
        """Emit progress event via WebSocket."""
        try:
            await socket_manager.broadcast(
                {
                    "type": "progress",
                    "workflowId": workflow_id,
                    "data": {
                        "stage": stage,
                        "percentage": percentage,
                        "current_step": current_step,
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                namespace="/agents",
            )
        except Exception as e:
            logger.warning(f"Failed to emit progress: {str(e)}")

    async def _emit_artifact(
        self,
        workflow_id: str,
        artifact_type: str,
        artifact_id: str,
        url: str,
        label: str,
    ) -> None:
        """Emit artifact event via WebSocket."""
        try:
            await socket_manager.broadcast(
                {
                    "type": "artifact",
                    "workflowId": workflow_id,
                    "data": {
                        "artifact_type": artifact_type,
                        "artifact_id": artifact_id,
                        "url": url,
                        "label": label,
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                namespace="/agents",
            )
        except Exception as e:
            logger.warning(f"Failed to emit artifact: {str(e)}")

    async def _emit_approval_required(
        self,
        workflow_id: str,
        package_id: UUID,
        qa_score: float,
    ) -> None:
        """Emit approval required event via WebSocket."""
        try:
            await socket_manager.broadcast(
                {
                    "type": "approval_required",
                    "workflowId": workflow_id,
                    "data": {
                        "package_id": str(package_id),
                        "reason": "qa_score_below_threshold" if qa_score < 0.7 else "manual_approval_required",
                        "qa_score": qa_score,
                    },
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
                namespace="/agents",
            )
        except Exception as e:
            logger.warning(f"Failed to emit approval_required: {str(e)}")
