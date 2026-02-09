"""
Tests for MCP Image Generator.

Tests the real MCP-based image generation implementation.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime
import base64

from app.infrastructure.mcp.mcp_image_generator import (
    MCPImageGenerator,
    MCPImageGeneratorError,
)
from app.infrastructure.mcp.base_client import (
    MCPHttpClient,
    MCPToolCallError,
    MCPTimeoutError,
    MCPConnectionError,
)
from app.domain.entities.image_artifact import ImageArtifact
from app.domain.entities.image_request import ImageGenerationRequest


class TestMCPImageGenerator:
    """Test MCPImageGenerator implementation."""
    
    @pytest.fixture
    def mock_mcp_client(self):
        """Create mock MCP client."""
        client = AsyncMock(spec=MCPHttpClient)
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=None)
        return client
    
    @pytest.fixture
    def mock_minio_client(self):
        """Create mock MinIO client."""
        client = MagicMock()
        client.upload_base64_image = AsyncMock(
            return_value="http://localhost:9000/e-business/images/test.png"
        )
        client.is_base64 = MagicMock(return_value=False)
        return client
    
    @pytest.fixture
    def generator(self, mock_mcp_client, mock_minio_client):
        """Create generator with mocked dependencies."""
        return MCPImageGenerator(
            mcp_client=mock_mcp_client,
            minio_client=mock_minio_client,
            model="stable-diffusion-xl",
            # Include example.com for test URLs
            allowed_domains={"localhost", "127.0.0.1", "minio", "example.com"},
        )
    
    @pytest.fixture
    def sample_request(self):
        """Create sample image generation request."""
        return ImageGenerationRequest(
            prompt="A beautiful sunset over the ocean",
            width=512,
            height=512,
        )
    
    @pytest.mark.asyncio
    async def test_generate_with_url_response(self, generator, sample_request, mock_mcp_client):
        """Test generation when MCP returns a URL directly."""
        mock_mcp_client.call_tool.return_value = {
            "content": [
                {
                    "type": "image",
                    "data": "http://example.com/generated.png",
                    "mimeType": "image/png"
                }
            ],
            "metadata": {
                "width": 512,
                "height": 512,
                "model": "stable-diffusion-xl",
                "provider": "mcp"
            }
        }
        
        result = await generator.generate(sample_request)
        
        assert isinstance(result, ImageArtifact)
        assert result.url == "http://example.com/generated.png"
        assert result.provider == "mcp"
        assert result.width == 512
        assert result.height == 512
        assert result.prompt == sample_request.prompt
    
    @pytest.mark.asyncio
    async def test_generate_with_base64_response(self, generator, sample_request, mock_mcp_client, mock_minio_client):
        """Test generation when MCP returns Base64 data."""
        # Simulate Base64 data response
        test_image_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        b64_data = base64.b64encode(test_image_data).decode()
        
        mock_mcp_client.call_tool.return_value = {
            "content": [
                {
                    "type": "image",
                    "data": b64_data,
                    "mimeType": "image/png"
                }
            ],
            "metadata": {
                "width": 512,
                "height": 512,
            }
        }
        
        # Configure Base64 detection
        mock_minio_client.is_base64.return_value = True
        
        result = await generator.generate(sample_request)
        
        assert isinstance(result, ImageArtifact)
        assert result.url == "http://localhost:9000/e-business/images/test.png"
        mock_minio_client.upload_base64_image.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_generate_formats_mcp_request_correctly(self, generator, sample_request, mock_mcp_client):
        """Test that generator formats MCP request according to spec."""
        mock_mcp_client.call_tool.return_value = {
            "content": [{"type": "image", "data": "http://example.com/img.png", "mimeType": "image/png"}],
            "metadata": {}
        }
        
        await generator.generate(sample_request)
        
        # Verify call_tool was called with correct arguments
        mock_mcp_client.call_tool.assert_called_once()
        call_args = mock_mcp_client.call_tool.call_args
        
        assert call_args[0][0] == "generate_image"  # tool_name
        arguments = call_args[0][1]
        assert arguments["prompt"] == sample_request.prompt
        assert arguments["width"] == 512
        assert arguments["height"] == 512
        assert "model" in arguments
    
    @pytest.mark.asyncio
    async def test_generate_handles_timeout(self, generator, sample_request, mock_mcp_client):
        """Test timeout handling during generation."""
        mock_mcp_client.call_tool.side_effect = MCPTimeoutError("Timed out")
        
        with pytest.raises(MCPImageGeneratorError) as exc_info:
            await generator.generate(sample_request)
        
        assert "timeout" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_generate_handles_connection_error(self, generator, sample_request, mock_mcp_client):
        """Test connection error handling."""
        mock_mcp_client.call_tool.side_effect = MCPConnectionError("Connection failed")
        
        with pytest.raises(MCPImageGeneratorError) as exc_info:
            await generator.generate(sample_request)
        
        assert "connection" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_generate_handles_tool_error(self, generator, sample_request, mock_mcp_client):
        """Test MCP tool error handling."""
        mock_mcp_client.call_tool.side_effect = MCPToolCallError(
            message="Tool not found",
            code=-32602,
            tool_name="generate_image"
        )
        
        with pytest.raises(MCPImageGeneratorError):
            await generator.generate(sample_request)
    
    @pytest.mark.asyncio
    async def test_context_manager(self, mock_mcp_client, mock_minio_client):
        """Test async context manager support."""
        generator = MCPImageGenerator(
            mcp_client=mock_mcp_client,
            minio_client=mock_minio_client,
        )
        
        async with generator as g:
            assert g is generator
        
        # MCP client should be entered and exited
        mock_mcp_client.__aenter__.assert_called_once()
        mock_mcp_client.__aexit__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_parse_mcp_image_response_url(self, generator):
        """Test parsing MCP response with URL."""
        response = {
            "content": [
                {
                    "type": "image",
                    "data": "https://example.com/image.png",
                    "mimeType": "image/png"
                }
            ],
            "metadata": {
                "width": 1024,
                "height": 768,
            }
        }
        
        image_data, mime_type, metadata = await generator._parse_mcp_image_response(response)
        
        assert image_data == "https://example.com/image.png"
        assert mime_type == "image/png"
        assert metadata["width"] == 1024
    
    @pytest.mark.asyncio
    async def test_parse_mcp_image_response_missing_content(self, generator):
        """Test parsing MCP response with missing content."""
        response = {"metadata": {}}
        
        with pytest.raises(MCPImageGeneratorError) as exc_info:
            await generator._parse_mcp_image_response(response)
        
        assert "content" in str(exc_info.value).lower()


class MCPImageGeneratorExceptions:
    """Test MCPImageGenerator exceptions."""
    
    def test_mcp_image_generator_error(self):
        """Test MCPImageGeneratorError."""
        error = MCPImageGeneratorError("Image generation failed")
        assert "Image generation failed" in str(error)


class TestMCPImageGeneratorURLValidation:
    """Test URL validation functionality."""
    
    @pytest.fixture
    def mock_mcp_client(self):
        """Create mock MCP client."""
        client = AsyncMock(spec=MCPHttpClient)
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=None)
        return client
    
    @pytest.fixture
    def mock_minio_client(self):
        """Create mock MinIO client."""
        client = MagicMock()
        client.upload_base64_image = AsyncMock(
            return_value="http://localhost:9000/e-business/images/test.png"
        )
        client.is_base64 = MagicMock(return_value=False)
        return client
    
    @pytest.fixture
    def generator(self, mock_mcp_client, mock_minio_client):
        """Create generator with mocked dependencies."""
        return MCPImageGenerator(
            mcp_client=mock_mcp_client,
            minio_client=mock_minio_client,
            model="stable-diffusion-xl",
        )
    
    def test_validate_url_allowed_localhost(self, generator):
        """Test URL validation allows localhost."""
        assert generator._validate_url("http://localhost:9000/image.png") is True
    
    def test_validate_url_allowed_127(self, generator):
        """Test URL validation allows 127.0.0.1."""
        assert generator._validate_url("http://127.0.0.1:9000/image.png") is True
    
    def test_validate_url_blocked_domain(self, generator):
        """Test URL validation blocks unknown domains."""
        from app.infrastructure.mcp.mcp_image_generator import MCPInvalidURLError
        
        with pytest.raises(MCPInvalidURLError) as exc_info:
            generator._validate_url("http://evil.com/malicious.png")
        
        assert "evil.com" in str(exc_info.value)
        assert "not allowed" in str(exc_info.value)
    
    def test_validate_url_invalid_scheme(self, generator):
        """Test URL validation blocks non-http schemes."""
        from app.infrastructure.mcp.mcp_image_generator import MCPInvalidURLError
        
        with pytest.raises(MCPInvalidURLError) as exc_info:
            generator._validate_url("file:///etc/passwd")
        
        assert "scheme" in str(exc_info.value).lower()
    
    def test_custom_allowed_domains(self, mock_mcp_client, mock_minio_client):
        """Test custom allowed domains configuration."""
        generator = MCPImageGenerator(
            mcp_client=mock_mcp_client,
            minio_client=mock_minio_client,
            allowed_domains={"example.com", "trusted.io"},
        )
        
        assert generator._validate_url("https://example.com/image.png") is True
        assert generator._validate_url("https://sub.trusted.io/image.png") is True
    
    @pytest.mark.asyncio
    async def test_resolve_image_url_validates_external(self, generator):
        """Test _resolve_image_url validates external URLs."""
        from app.infrastructure.mcp.mcp_image_generator import MCPInvalidURLError
        
        with pytest.raises(MCPInvalidURLError):
            await generator._resolve_image_url(
                "http://untrusted.com/image.png",
                "image/png"
            )
    
    @pytest.mark.asyncio
    async def test_resolve_image_url_skip_validation(self, generator):
        """Test _resolve_image_url can skip validation."""
        url = await generator._resolve_image_url(
            "http://any-domain.com/image.png",
            "image/png",
            skip_validation=True
        )
        assert url == "http://any-domain.com/image.png"

