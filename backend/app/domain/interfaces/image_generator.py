"""
Image Generator Interface.

Defines the contract for image generation services.
"""
from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from app.domain.entities.image_artifact import ImageArtifact
from app.domain.entities.image_request import ImageGenerationRequest


@runtime_checkable
class IImageGenerator(Protocol):
    """Interface for image generation services.
    
    This is the domain layer contract that infrastructure implementations
    (like MCP clients) must satisfy.
    """
    
    async def generate(self, request: ImageGenerationRequest) -> ImageArtifact:
        """Generate an image from a text prompt.
        
        Args:
            request: Image generation request containing prompt and parameters
            
        Returns:
            ImageArtifact containing the generated image URL and metadata
        """
        ...

    async def __aenter__(self) -> "IImageGenerator":
        """Async context manager entry."""
        ...
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        ...
