"""
Video Tools

Provides video generation and slideshow fallback utilities.
"""

import asyncio
from typing import Dict, Any, List, Optional
from uuid import UUID, uuid4


class VideoTools:
    """
    Video generation and slideshow creation utilities.

    Implements primary video generation with automatic fallback to slideshow.
    """

    def __init__(self, video_provider=None, slideshow_provider=None, asset_repository=None):
        """
        Initialize video tools.

        Args:
            video_provider: Primary video generation provider
            slideshow_provider: Fallback slideshow provider
            asset_repository: Repository for persisting video assets
        """
        self.video_provider = video_provider
        self.slideshow_provider = slideshow_provider
        self.asset_repository = asset_repository

    async def generate_video(
        self,
        prompt: str,
        image_paths: List[str],
        duration_sec: int = 15,
        timeout_sec: int = 30,
    ) -> Dict[str, Any]:
        """
        Generate a video with automatic fallback to slideshow.

        Strategy:
        1. Try primary video generation with timeout
        2. On timeout or exception, fallback to slideshow
        3. Always returns a valid video asset

        Args:
            prompt: Video generation prompt
            image_paths: List of image paths/URLs to use
            duration_sec: Target duration in seconds
            timeout_sec: Timeout for primary generation attempt

        Returns:
            Dictionary with generation result:
            {
                "url": "https://...",
                "prompt": "original prompt",
                "provider": "video|slideshow",
                "duration": 15,
                "is_fallback": false,
                "metadata": {...}
            }
        """
        if self.video_provider is None:
            # No provider configured, use slideshow directly
            result = await self.create_slideshow(
                images=image_paths,
                captions=[prompt] if prompt else [],
                duration_sec=duration_sec,
            )
            result["is_fallback"] = True
            return result

        try:
            # Try primary video generation with timeout
            result = await asyncio.wait_for(
                self._call_video_provider(prompt, image_paths, duration_sec),
                timeout=timeout_sec,
            )
            result["is_fallback"] = False
            return result
        except (asyncio.TimeoutError, Exception) as e:
            # Fallback to slideshow on any error
            print(f"Video generation failed ({type(e).__name__}), falling back to slideshow")
            result = await self.create_slideshow(
                images=image_paths,
                captions=[prompt] if prompt else [],
                duration_sec=duration_sec,
            )
            result["is_fallback"] = True
            return result

    async def _call_video_provider(
        self,
        prompt: str,
        image_paths: List[str],
        duration_sec: int,
    ) -> Dict[str, Any]:
        """
        Internal method to call primary video provider.

        Args:
            prompt: Generation prompt
            image_paths: Source images
            duration_sec: Target duration

        Returns:
            Raw video generation result
        """
        if self.video_provider is None:
            raise RuntimeError("Video provider not configured")

        result = await self.video_provider.generate(
            prompt=prompt,
            images=image_paths,
            duration=duration_sec,
        )
        return result

    async def create_slideshow(
        self,
        images: List[str],
        captions: List[str],
        duration_sec: int = 15,
        transition: str = "fade",
    ) -> Dict[str, Any]:
        """
        Create a slideshow video from images.

        Args:
            images: List of image URLs/paths
            captions: List of captions (one per image or single caption for all)
            duration_sec: Total duration
            transition: Transition effect (fade, slide, dissolve)

        Returns:
            Dictionary with slideshow result:
            {
                "url": "https://...",
                "provider": "slideshow",
                "duration": duration_sec,
                "images_count": len(images),
                "transition": transition,
                "metadata": {...}
            }
        """
        if self.slideshow_provider is None:
            # Return mock response for development
            return {
                "url": f"mock://slideshow/{uuid4()}",
                "provider": "slideshow",
                "duration": duration_sec,
                "images_count": len(images),
                "transition": transition,
                "metadata": {
                    "images": images,
                    "captions": captions,
                },
            }

        try:
            result = await self.slideshow_provider.create(
                images=images,
                captions=captions,
                duration=duration_sec,
                transition=transition,
            )
            return result
        except Exception as e:
            raise RuntimeError(f"Slideshow creation failed: {str(e)}")

    async def save_asset(
        self,
        artifact: Dict[str, Any],
        user_id: UUID,
        workflow_id: str,
    ) -> Dict[str, Any]:
        """
        Save video asset to database.

        Args:
            artifact: Video generation result
            user_id: User UUID
            workflow_id: Workflow identifier

        Returns:
            Dictionary with saved asset info:
            {
                "asset_id": "uuid",
                "asset_type": "video",
                "url": "https://...",
                "is_fallback": bool
            }

        Raises:
            RuntimeError: If save operation fails
        """
        if self.asset_repository is None:
            # Return mock response for development
            return {
                "asset_id": str(uuid4()),
                "asset_type": "video",
                "url": artifact.get("url", ""),
                "is_fallback": artifact.get("is_fallback", False),
            }

        try:
            from app.infrastructure.database.models import VideoAssetModel
            from datetime import datetime, timezone

            asset = VideoAssetModel(
                user_id=user_id,
                workflow_id=workflow_id,
                asset_type="video",
                url=artifact.get("url", ""),
                prompt=artifact.get("prompt", ""),
                provider=artifact.get("provider", "slideshow"),
                width=artifact.get("width", 1920),
                height=artifact.get("height", 1080),
                metadata_json={
                    "duration": artifact.get("duration"),
                    "is_fallback": artifact.get("is_fallback", False),
                    **artifact.get("metadata", {}),
                },
            )

            saved = await self.asset_repository.create(asset)

            return {
                "asset_id": str(saved.asset_uuid),
                "asset_type": "video",
                "url": saved.url,
                "is_fallback": artifact.get("is_fallback", False),
            }
        except Exception as e:
            raise RuntimeError(f"Failed to save video asset: {str(e)}")
