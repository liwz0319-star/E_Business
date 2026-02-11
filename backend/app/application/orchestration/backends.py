"""
Backend Implementations

Provides backend implementations for agent execution.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class ProviderBackend:
    """
    Base class for provider backends.
    """

    async def generate(self, **kwargs) -> Dict[str, Any]:
        """Generate content."""
        raise NotImplementedError


class MockVideoProvider(ProviderBackend):
    """
    Mock video provider for development/testing.
    """

    async def generate(
        self,
        prompt: str,
        images: list[str],
        duration: int,
    ) -> Dict[str, Any]:
        """Generate mock video."""
        import uuid

        return {
            "url": f"mock://video/{uuid.uuid4()}",
            "provider": "mock_video",
            "duration": duration,
            "prompt": prompt,
            "metadata": {
                "images_count": len(images),
            },
        }


class MockSlideshowProvider(ProviderBackend):
    """
    Mock slideshow provider for development/testing.
    """

    async def create(
        self,
        images: list[str],
        captions: list[str],
        duration: int,
        transition: str = "fade",
    ) -> Dict[str, Any]:
        """Create mock slideshow."""
        import uuid

        return {
            "url": f"mock://slideshow/{uuid.uuid4()}",
            "provider": "slideshow",
            "duration": duration,
            "images_count": len(images),
            "transition": transition,
            "metadata": {
                "images": images,
                "captions": captions,
            },
        }
