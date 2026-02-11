"""
Image Tools

Provides image generation and management utilities.
"""

from typing import Dict, Any, Optional
from uuid import UUID, uuid4


class ImageTools:
    """
    Image generation and asset management utilities.

    Handles image generation through providers and asset persistence.
    """

    def __init__(self, provider_factory=None, asset_repository=None):
        """
        Initialize image tools.

        Args:
            provider_factory: Factory for creating image generation providers
            asset_repository: Repository for persisting image assets
        """
        self.provider_factory = provider_factory
        self.asset_repository = asset_repository

    async def generate_image(
        self,
        prompt: str,
        width: int = 1024,
        height: int = 1024,
        provider: str = "default",
    ) -> Dict[str, Any]:
        """
        Generate an image using the specified provider.

        Args:
            prompt: Image generation prompt
            width: Image width in pixels
            height: Image height in pixels
            provider: Provider name (default, openai, stability, etc.)

        Returns:
            Dictionary with generation result:
            {
                "url": "https://...",
                "prompt": "original prompt",
                "provider": "provider_name",
                "width": 1024,
                "height": 1024,
                "metadata": {...}
            }

        Raises:
            RuntimeError: If generation fails or provider not configured
        """
        if self.provider_factory is None:
            raise RuntimeError("Image provider factory not configured")

        try:
            provider_instance = self.provider_factory.get_provider(provider)
            result = await provider_instance.generate(
                prompt=prompt,
                width=width,
                height=height,
            )
            return result
        except Exception as e:
            raise RuntimeError(f"Image generation failed: {str(e)}")

    async def create_variation(
        self,
        image_path: str,
        prompt: Optional[str] = None,
        provider: str = "default",
    ) -> Dict[str, Any]:
        """
        Create a variation of an existing image.

        Args:
            image_path: Path or URL to source image
            prompt: Optional modification prompt
            provider: Provider name

        Returns:
            Dictionary with variation result
        """
        if self.provider_factory is None:
            raise RuntimeError("Image provider factory not configured")

        try:
            provider_instance = self.provider_factory.get_provider(provider)
            result = await provider_instance.variation(
                image=image_path,
                prompt=prompt,
            )
            return result
        except Exception as e:
            raise RuntimeError(f"Image variation failed: {str(e)}")

    async def save_asset(
        self,
        artifact: Dict[str, Any],
        user_id: UUID,
        workflow_id: str,
        label: str = "generated",
    ) -> Dict[str, Any]:
        """
        Save image asset to database.

        Args:
            artifact: Image generation result
            user_id: User UUID
            workflow_id: Workflow identifier
            label: Optional label for the image

        Returns:
            Dictionary with saved asset info:
            {
                "asset_id": "uuid",
                "asset_type": "image",
                "url": "https://...",
                "label": "hero|lifestyle|detail"
            }

        Raises:
            RuntimeError: If save operation fails
        """
        if self.asset_repository is None:
            # Return mock response for development
            return {
                "asset_id": str(uuid4()),
                "asset_type": "image",
                "url": artifact.get("url", ""),
                "label": label,
            }

        try:
            # Create video asset record with asset_type='image'
            from app.infrastructure.database.models import VideoAssetModel
            from datetime import datetime, timezone

            asset = VideoAssetModel(
                user_id=user_id,
                workflow_id=workflow_id,
                asset_type="image",  # Critical: store as image type
                url=artifact.get("url", ""),
                prompt=artifact.get("prompt", ""),
                original_prompt=artifact.get("original_prompt"),
                provider=artifact.get("provider", "unknown"),
                width=artifact.get("width", 1024),
                height=artifact.get("height", 1024),
                metadata_json=artifact.get("metadata"),
            )

            saved = await self.asset_repository.create(asset)

            return {
                "asset_id": str(saved.asset_uuid),
                "asset_type": "image",
                "url": saved.url,
                "label": label,
            }
        except Exception as e:
            raise RuntimeError(f"Failed to save image asset: {str(e)}")
