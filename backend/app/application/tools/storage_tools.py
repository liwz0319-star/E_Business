"""
Storage Tools

Provides product package storage and state management utilities.
"""

from typing import Dict, Any, Optional
from uuid import UUID


class StorageTools:
    """
    Product package storage and state management.

    Wraps ProductPackageRepository for high-level operations.
    """

    def __init__(self, repository):
        """
        Initialize storage tools.

        Args:
            repository: ProductPackageRepository instance
        """
        self.repository = repository

    async def create_package(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new product package.

        Args:
            data: Package creation data:
            {
                "workflow_id": "uuid-string",
                "user_id": UUID,
                "input_data": {...},
                "status": "running",
                "stage": "analysis"
            }

        Returns:
            Created package data:
            {
                "package_id": UUID,
                "workflow_id": "uuid-string",
                "status": "running",
                "stage": "analysis"
            }

        Raises:
            RuntimeError: If creation fails
        """
        try:
            package = await self.repository.create(data)
            return {
                "package_id": package.id,
                "workflow_id": package.workflow_id,
                "status": package.status,
                "stage": package.stage,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to create package: {str(e)}")

    async def update_package_status(
        self,
        package_id: UUID,
        status: str,
        stage: str,
        progress: Dict[str, Any],
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Update package status, stage, and progress.

        Args:
            package_id: Package UUID
            status: New status
            stage: New stage
            progress: Progress dict (percentage, current_step)
            error_message: Error message if failed

        Returns:
            Updated package data

        Raises:
            RuntimeError: If update fails or package not found
        """
        try:
            package = await self.repository.update_status(
                package_id=package_id,
                status=status,
                stage=stage,
                progress=progress,
                error_message=error_message,
            )

            if package is None:
                raise RuntimeError(f"Package {package_id} not found")

            return {
                "package_id": package.id,
                "workflow_id": package.workflow_id,
                "status": package.status,
                "stage": package.stage,
                "progress": package.progress,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to update package status: {str(e)}")

    async def link_asset(
        self,
        package_id: UUID,
        artifact_type: str,
        artifact_id: str,
    ) -> Dict[str, Any]:
        """
        Link an artifact to a package.

        Args:
            package_id: Package UUID
            artifact_type: Artifact type (copywriting, images, video)
            artifact_id: Artifact ID or reference

        Returns:
            Updated package data

        Raises:
            RuntimeError: If link fails or package not found
        """
        try:
            package = await self.repository.add_artifact(
                package_id=package_id,
                artifact_type=artifact_type,
                artifact_id=artifact_id,
            )

            if package is None:
                raise RuntimeError(f"Package {package_id} not found")

            return {
                "package_id": package.id,
                "artifacts": package.artifacts,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to link artifact: {str(e)}")

    async def update_analysis(
        self,
        package_id: UUID,
        analysis_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update package analysis data.

        Args:
            package_id: Package UUID
            analysis_data: Analysis results

        Returns:
            Updated package data

        Raises:
            RuntimeError: If update fails or package not found
        """
        try:
            package = await self.repository.update_analysis_data(
                package_id=package_id,
                analysis_data=analysis_data,
            )

            if package is None:
                raise RuntimeError(f"Package {package_id} not found")

            return {
                "package_id": package.id,
                "analysis_data": package.analysis_data,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to update analysis: {str(e)}")

    async def update_qa_report(
        self,
        package_id: UUID,
        qa_report: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Update package QA report.

        Args:
            package_id: Package UUID
            qa_report: QA report dict

        Returns:
            Updated package data

        Raises:
            RuntimeError: If update fails or package not found
        """
        try:
            package = await self.repository.update_qa_report(
                package_id=package_id,
                qa_report=qa_report,
            )

            if package is None:
                raise RuntimeError(f"Package {package_id} not found")

            return {
                "package_id": package.id,
                "qa_report": package.qa_report,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to update QA report: {str(e)}")

    async def update_approval(
        self,
        package_id: UUID,
        approval_status: str,
    ) -> Dict[str, Any]:
        """
        Update package approval status.

        Args:
            package_id: Package UUID
            approval_status: New approval status (approved/rejected)

        Returns:
            Updated package data

        Raises:
            RuntimeError: If update fails or package not found
        """
        try:
            package = await self.repository.update_approval(
                package_id=package_id,
                approval_status=approval_status,
            )

            if package is None:
                raise RuntimeError(f"Package {package_id} not found")

            return {
                "package_id": package.id,
                "approval_status": package.approval_status,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to update approval: {str(e)}")
