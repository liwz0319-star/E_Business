"""
MCP Image Generator.

Real MCP-based image generator implementation that connects to
an image generation service via MCP protocol.
"""
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from datetime import datetime
from urllib.parse import urlparse
from uuid import uuid4

from app.domain.entities.image_artifact import ImageArtifact
from app.domain.entities.image_request import ImageGenerationRequest
from app.infrastructure.mcp.base_client import (
    MCPBaseClient,
    MCPHttpClient,
    MCPToolCallError,
    MCPTimeoutError,
    MCPConnectionError,
)


logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================

class MCPImageGeneratorError(Exception):
    """Error during MCP image generation."""
    pass


class MCPInvalidURLError(MCPImageGeneratorError):
    """Invalid or blocked URL."""
    pass


# ============================================================================
# MCP Image Generator Implementation
# ============================================================================

class MCPImageGenerator:
    """MCP-based image generator.
    
    Implements IImageGenerator interface using MCP protocol
    to communicate with image generation services.
    
    Handles both URL and Base64 responses from MCP, automatically
    uploading Base64 images to MinIO when needed.
    
    Example:
        async with MCPImageGenerator(mcp_client, minio_client) as generator:
            artifact = await generator.generate(request)
    """
    
    # Default allowed URL patterns (domains)
    DEFAULT_ALLOWED_DOMAINS: Set[str] = {
        "localhost",
        "127.0.0.1",
        "minio",  # Docker service name
    }
    
    def __init__(
        self,
        mcp_client: MCPBaseClient,
        minio_client: Optional[Any] = None,
        model: str = "stable-diffusion-xl",
        tool_name: str = "generate_image",
        allowed_domains: Optional[Set[str]] = None,
    ):
        """Initialize MCP image generator.
        
        Args:
            mcp_client: MCP client for communication
            minio_client: MinIO client for Base64 upload (optional)
            model: Default model name for generation
            tool_name: MCP tool name for image generation
            allowed_domains: Set of allowed URL domains (for SSRF prevention)
        """
        self.mcp_client = mcp_client
        self.minio_client = minio_client
        self.model = model
        self.tool_name = tool_name
        self._session_active = False
        self.allowed_domains = allowed_domains or self.DEFAULT_ALLOWED_DOMAINS
    
    async def __aenter__(self) -> "MCPImageGenerator":
        """Enter async context manager."""
        await self.mcp_client.__aenter__()
        self._session_active = True
        logger.debug("MCPImageGenerator session started")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager."""
        await self.mcp_client.__aexit__(exc_type, exc_val, exc_tb)
        self._session_active = False
        logger.debug("MCPImageGenerator session closed")
    
    def _build_tool_arguments(
        self,
        request: ImageGenerationRequest,
    ) -> Dict[str, Any]:
        """Build MCP tool arguments from request.
        
        Args:
            request: Image generation request
            
        Returns:
            Dictionary of tool arguments
        """
        arguments = {
            "prompt": request.prompt,
            "width": request.width,
            "height": request.height,
            "model": self.model,
            "num_inference_steps": request.num_inference_steps,
            "guidance_scale": request.guidance_scale,
        }
        
        if request.negative_prompt:
            arguments["negative_prompt"] = request.negative_prompt
        
        if request.style:
            arguments["style"] = request.style
        
        return arguments
    
    async def _parse_mcp_image_response(
        self,
        response: Dict[str, Any],
    ) -> Tuple[str, str, Dict[str, Any]]:
        """Parse MCP image generation response.
        
        Args:
            response: MCP tool response
            
        Returns:
            Tuple of (image_data, mime_type, metadata)
            
        Raises:
            MCPImageGeneratorError: If response format is invalid
        """
        # Get content array
        content = response.get("content")
        if not content or not isinstance(content, list) or len(content) == 0:
            raise MCPImageGeneratorError(
                "Invalid MCP response: missing or empty 'content' field"
            )
        
        # Get first content item (image)
        image_content = content[0]
        image_data = image_content.get("data", "")
        mime_type = image_content.get("mimeType", "image/png")
        
        # Get metadata
        metadata = response.get("metadata", {})
        
        return image_data, mime_type, metadata
    
    def _validate_url(self, url: str) -> bool:
        """Validate URL against allowed domains to prevent SSRF.
        
        Args:
            url: URL to validate
            
        Returns:
            True if URL is valid and allowed
            
        Raises:
            MCPInvalidURLError: If URL is not allowed
        """
        try:
            parsed = urlparse(url)
            
            # Check scheme
            if parsed.scheme not in ("http", "https"):
                raise MCPInvalidURLError(
                    f"Invalid URL scheme: {parsed.scheme}. Only http/https allowed."
                )
            
            # Extract hostname
            hostname = parsed.hostname
            if not hostname:
                raise MCPInvalidURLError("URL missing hostname")
            
            # Check against allowed domains
            # Allow exact match or subdomain match
            is_allowed = any(
                hostname == domain or hostname.endswith(f".{domain}")
                for domain in self.allowed_domains
            )
            
            if not is_allowed:
                logger.warning(
                    f"URL domain '{hostname}' not in allowed list: {self.allowed_domains}"
                )
                raise MCPInvalidURLError(
                    f"URL domain '{hostname}' is not allowed. "
                    f"Allowed domains: {', '.join(self.allowed_domains)}"
                )
            
            return True
            
        except MCPInvalidURLError:
            raise
        except Exception as e:
            raise MCPInvalidURLError(f"Invalid URL format: {e}") from e
    
    async def _resolve_image_url(
        self,
        image_data: str,
        mime_type: str,
        skip_validation: bool = False,
    ) -> str:
        """Resolve image data to a URL.
        
        If image_data is already a URL, validates and returns it.
        If image_data is Base64, uploads to MinIO and returns URL.
        
        Args:
            image_data: Image URL or Base64 data
            mime_type: MIME type of the image
            skip_validation: Skip URL validation (for trusted sources)
            
        Returns:
            Accessible URL for the image
            
        Raises:
            MCPInvalidURLError: If URL validation fails
        """
        # Check if it's already a URL
        if image_data.startswith(("http://", "https://")):
            if not skip_validation:
                self._validate_url(image_data)
            return image_data
        
        # Check if it's Base64 and we have MinIO client
        if self.minio_client is not None:
            if self.minio_client.is_base64(image_data):
                logger.debug("Uploading Base64 image to MinIO")
                url = await self.minio_client.upload_base64_image(
                    image_data,
                    mime_type=mime_type,
                )
                return url
        
        # Fall back to returning the data as-is (may not be accessible)
        logger.warning(
            "Image data is not a URL and MinIO client not available, "
            "returning raw data"
        )
        return image_data
    
    async def generate(
        self,
        request: ImageGenerationRequest,
    ) -> ImageArtifact:
        """Generate an image using MCP protocol.
        
        Args:
            request: Image generation request
            
        Returns:
            ImageArtifact with generated image URL and metadata
            
        Raises:
            MCPImageGeneratorError: If generation fails
        """
        logger.info(f"Starting MCP image generation for prompt: {request.prompt[:50]}...")
        
        # Build tool arguments
        arguments = self._build_tool_arguments(request)
        
        try:
            # Call MCP tool
            response = await self.mcp_client.call_tool(
                self.tool_name,
                arguments,
            )
            
            # Parse response
            image_data, mime_type, metadata = await self._parse_mcp_image_response(response)
            
            # Resolve to URL (upload Base64 if needed)
            image_url = await self._resolve_image_url(image_data, mime_type)
            
            # Create artifact
            artifact = ImageArtifact(
                url=image_url,
                prompt=request.prompt,
                original_prompt=request.prompt,
                provider="mcp",
                width=metadata.get("width", request.width),
                height=metadata.get("height", request.height),
                created_at=datetime.utcnow(),
                id=uuid4(),
            )
            
            logger.info(f"MCP image generation complete: {image_url}")
            return artifact
            
        except MCPTimeoutError as e:
            raise MCPImageGeneratorError(
                f"Image generation timeout: {e}"
            ) from e
        except MCPConnectionError as e:
            raise MCPImageGeneratorError(
                f"MCP connection error: {e}"
            ) from e
        except MCPToolCallError as e:
            raise MCPImageGeneratorError(
                f"MCP tool call error: {e}"
            ) from e
        except MCPImageGeneratorError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during image generation: {e}")
            raise MCPImageGeneratorError(
                f"Image generation failed: {e}"
            ) from e
