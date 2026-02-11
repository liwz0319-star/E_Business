"""
Product Package Repository Implementation

Async SQLAlchemy-based implementation for product package data access.
"""

from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import ProductPackageModel


class ProductPackageRepository:
    """
    Async repository for ProductPackage entities.

    Handles product package data persistence using async SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session: Async SQLAlchemy session
        """
        self._session = session

    async def create(self, data: Dict[str, Any]) -> ProductPackageModel:
        """
        Create a new product package.

        Args:
            data: Dictionary containing product package fields

        Returns:
            Created ProductPackageModel instance
        """
        package = ProductPackageModel(**data)
        self._session.add(package)
        await self._session.flush()
        await self._session.refresh(package)
        return package

    async def get_by_workflow_id(self, workflow_id: str) -> Optional[ProductPackageModel]:
        """
        Retrieve a product package by workflow ID.

        Args:
            workflow_id: The workflow ID

        Returns:
            ProductPackageModel if found, None otherwise
        """
        result = await self._session.execute(
            select(ProductPackageModel).where(
                ProductPackageModel.workflow_id == workflow_id
            )
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, package_id: UUID) -> Optional[ProductPackageModel]:
        """
        Retrieve a product package by ID.

        Args:
            package_id: The package UUID

        Returns:
            ProductPackageModel if found, None otherwise
        """
        result = await self._session.execute(
            select(ProductPackageModel).where(
                ProductPackageModel.id == package_id
            )
        )
        return result.scalar_one_or_none()

    async def update_status(
        self,
        package_id: UUID,
        status: str,
        stage: Optional[str] = None,
        progress: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
    ) -> Optional[ProductPackageModel]:
        """
        Update package status and optionally stage/progress.

        Args:
            package_id: The package UUID
            status: New status value
            stage: New stage value (optional)
            progress: New progress dict (optional)
            error_message: Error message if failed (optional)

        Returns:
            Updated ProductPackageModel if found, None otherwise
        """
        result = await self._session.execute(
            select(ProductPackageModel).where(
                ProductPackageModel.id == package_id
            )
        )
        package = result.scalar_one_or_none()

        if package is None:
            return None

        package.status = status
        if stage is not None:
            package.stage = stage
        if progress is not None:
            package.progress = progress
        if error_message is not None:
            package.error_message = error_message

        # Set completed_at if transitioning to completed
        if status == "completed" and package.completed_at is None:
            from datetime import datetime, timezone
            package.completed_at = datetime.now(timezone.utc)

        await self._session.flush()
        await self._session.refresh(package)
        return package

    async def add_artifact(
        self,
        package_id: UUID,
        artifact_type: str,
        artifact_id: str
    ) -> Optional[ProductPackageModel]:
        """
        Add an artifact reference to the package.

        Args:
            package_id: The package UUID
            artifact_type: Type of artifact (e.g., 'copywriting', 'images', 'video')
            artifact_id: ID or reference to the artifact

        Returns:
            Updated ProductPackageModel if found, None otherwise
        """
        result = await self._session.execute(
            select(ProductPackageModel).where(
                ProductPackageModel.id == package_id
            )
        )
        package = result.scalar_one_or_none()

        if package is None:
            return None

        # Create new artifacts dict
        new_artifacts = dict(package.artifacts or {})
        if artifact_type not in new_artifacts:
            new_artifacts[artifact_type] = []

        # Convert to list if it's not already
        existing = list(new_artifacts[artifact_type])
        if artifact_id not in existing:
            existing.append(artifact_id)
        new_artifacts[artifact_type] = existing

        package.artifacts = new_artifacts

        await self._session.flush()
        await self._session.refresh(package)
        return package

    async def update_approval(
        self,
        package_id: UUID,
        approval_status: str,
    ) -> Optional[ProductPackageModel]:
        """
        Update package approval status.

        Args:
            package_id: The package UUID
            approval_status: New approval status ('approved' or 'rejected')

        Returns:
            Updated ProductPackageModel if found, None otherwise
        """
        result = await self._session.execute(
            select(ProductPackageModel).where(
                ProductPackageModel.id == package_id
            )
        )
        package = result.scalar_one_or_none()

        if package is None:
            return None

        package.approval_status = approval_status

        await self._session.flush()
        await self._session.refresh(package)
        return package

    async def update_qa_report(
        self,
        package_id: UUID,
        qa_report: Dict[str, Any],
    ) -> Optional[ProductPackageModel]:
        """
        Update package QA report.

        Args:
            package_id: The package UUID
            qa_report: QA report dict with score, issues, suggestions

        Returns:
            Updated ProductPackageModel if found, None otherwise
        """
        result = await self._session.execute(
            select(ProductPackageModel).where(
                ProductPackageModel.id == package_id
            )
        )
        package = result.scalar_one_or_none()

        if package is None:
            return None

        package.qa_report = qa_report

        await self._session.flush()
        await self._session.refresh(package)
        return package

    async def update_analysis_data(
        self,
        package_id: UUID,
        analysis_data: Dict[str, Any],
    ) -> Optional[ProductPackageModel]:
        """
        Update package analysis data.

        Args:
            package_id: The package UUID
            analysis_data: Analysis results dict

        Returns:
            Updated ProductPackageModel if found, None otherwise
        """
        result = await self._session.execute(
            select(ProductPackageModel).where(
                ProductPackageModel.id == package_id
            )
        )
        package = result.scalar_one_or_none()

        if package is None:
            return None

        package.analysis_data = analysis_data

        await self._session.flush()
        await self._session.refresh(package)
        return package
