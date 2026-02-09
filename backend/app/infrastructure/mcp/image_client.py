"""
Mock MCP Image Generator Client.

Temporary mock implementation for image generation via MCP.
This will be replaced with a real MCP client in Story 3.2.
"""
import asyncio
import logging
from typing import Optional
from datetime import datetime
from uuid import uuid4

from app.domain.entities.image_artifact import ImageArtifact
from app.domain.entities.image_request import ImageGenerationRequest


logger = logging.getLogger(__name__)


class MockMCPImageGenerator:
    """Mock MCP client for image generation.
    
    This is a temporary implementation that returns placeholder images.
    It will be replaced with a real MCP client that connects to an
    image generation service (like DALL-E, Stable Diffusion via MCP).
    
    Implements IImageGenerator interface.
    """
    
    # Placeholder image service URLs
    PLACEHOLDER_SERVICES = [
        "https://via.placeholder.com/{width}x{height}",
        "https://picsum.photos/{width}/{height}",
    ]
    
    def __init__(
        self,
        delay_seconds: float = 1.0,
        placeholder_service: int = 0,
    ):
        """Initialize mock generator.
        
        Args:
            delay_seconds: Simulated generation delay
            placeholder_service: Index of placeholder service to use
        """
        self.delay_seconds = delay_seconds
        self.placeholder_service = placeholder_service
        self._session_active = False
    
    async def __aenter__(self) -> "MockMCPImageGenerator":
        """Async context manager entry."""
        self._session_active = True
        logger.debug("MockMCPImageGenerator session started")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        self._session_active = False
        logger.debug("MockMCPImageGenerator session closed")
    
    async def generate(self, request: ImageGenerationRequest) -> ImageArtifact:
        """Generate a mock image.
        
        Simulates image generation with a configurable delay and returns
        a placeholder image URL.
        
        Args:
            request: Image generation request
            
        Returns:
            ImageArtifact with placeholder image URL
        """
        logger.info(f"Mock image generation started for prompt: {request.prompt[:50]}...")
        
        # Simulate generation delay
        await asyncio.sleep(self.delay_seconds)
        
        # Generate placeholder URL
        service_template = self.PLACEHOLDER_SERVICES[self.placeholder_service]
        image_url = service_template.format(
            width=request.width,
            height=request.height,
        )
        
        # Add random query param to avoid caching for picsum
        if "picsum" in image_url:
            image_url += f"?random={uuid4().hex[:8]}"
        
        artifact = ImageArtifact(
            url=image_url,
            prompt=request.prompt,
            original_prompt=request.prompt,
            provider="mock",
            width=request.width,
            height=request.height,
            created_at=datetime.utcnow(),
            id=uuid4(),
        )
        
        logger.info(f"Mock image generated: {image_url}")
        
        return artifact
    
    def parse_mcp_response(self, response: dict) -> ImageArtifact:
        """Parse MCP protocol response into ImageArtifact.
        
        This method handles the MCP response format and converts it
        to our domain entity. Currently a stub for future MCP integration.
        
        Args:
            response: Raw MCP response dictionary
            
        Returns:
            ImageArtifact parsed from response
        """
        # MCP response format (future implementation):
        # {
        #     "content": [
        #         {
        #             "type": "image",
        #             "data": "base64...",
        #             "mimeType": "image/png"
        #         }
        #     ],
        #     "metadata": {
        #         "width": 512,
        #         "height": 512,
        #         "model": "stable-diffusion-xl"
        #     }
        # }
        
        return ImageArtifact(
            url=response.get("url", ""),
            prompt=response.get("prompt", ""),
            original_prompt=response.get("original_prompt", ""),
            provider=response.get("provider", "mcp"),
            width=response.get("width", 512),
            height=response.get("height", 512),
        )
