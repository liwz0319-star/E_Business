"""
Tests for MCP Base Client.

Tests the HTTP and Stdio communication patterns for MCP protocol.
Following TDD: RED phase - write failing tests first.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import asyncio
import json

from app.infrastructure.mcp.base_client import (
    MCPBaseClient,
    MCPHttpClient,
    MCPToolCallError,
    MCPTimeoutError,
    MCPConnectionError,
)


class TestMCPBaseClient:
    """Test MCPBaseClient abstract interface."""
    
    def test_cannot_instantiate_abstract_class(self):
        """MCPBaseClient is abstract and cannot be instantiated directly."""
        with pytest.raises(TypeError):
            MCPBaseClient()
    
    def test_subclass_must_implement_call_tool(self):
        """Subclasses must implement call_tool method."""
        class IncompleteClient(MCPBaseClient):
            pass
        
        with pytest.raises(TypeError):
            IncompleteClient()


class TestMCPHttpClient:
    """Test MCP HTTP client implementation."""
    
    @pytest.fixture
    def client(self):
        """Create HTTP client instance."""
        return MCPHttpClient(
            server_url="http://localhost:3000",
            timeout=60,
        )
    
    @pytest.mark.asyncio
    async def test_format_mcp_request(self, client):
        """Test MCP request formatting according to protocol spec."""
        request = client.format_mcp_request(
            tool_name="generate_image",
            arguments={
                "prompt": "test prompt",
                "width": 512,
                "height": 512,
            }
        )
        
        assert request["jsonrpc"] == "2.0"
        assert "id" in request
        assert request["method"] == "tools/call"
        assert request["params"]["name"] == "generate_image"
        assert request["params"]["arguments"]["prompt"] == "test prompt"
        assert request["params"]["arguments"]["width"] == 512
        assert request["params"]["arguments"]["height"] == 512
    
    @pytest.mark.asyncio
    async def test_parse_mcp_response_success(self, client):
        """Test parsing successful MCP response."""
        response = {
            "jsonrpc": "2.0",
            "id": "test-id",
            "result": {
                "content": [
                    {
                        "type": "image",
                        "data": "http://example.com/image.png",
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
        }
        
        result = client.parse_mcp_response(response)
        
        assert result["content"][0]["data"] == "http://example.com/image.png"
        assert result["metadata"]["width"] == 512
    
    @pytest.mark.asyncio
    async def test_parse_mcp_response_error(self, client):
        """Test parsing MCP error response."""
        response = {
            "jsonrpc": "2.0",
            "id": "test-id",
            "error": {
                "code": -32602,
                "message": "Tool not found",
                "data": {"tool_name": "unknown_tool"}
            }
        }
        
        with pytest.raises(MCPToolCallError) as exc_info:
            client.parse_mcp_response(response)
        
        assert "Tool not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_call_tool_success(self, client):
        """Test successful tool call via HTTP."""
        mock_response = {
            "jsonrpc": "2.0",
            "id": "test-id",
            "result": {
                "content": [
                    {
                        "type": "image",
                        "data": "http://example.com/image.png",
                        "mimeType": "image/png"
                    }
                ],
                "metadata": {}
            }
        }
        
        with patch.object(client, '_send_http_request', new_callable=AsyncMock) as mock_send:
            mock_send.return_value = mock_response
            
            result = await client.call_tool(
                "generate_image",
                {"prompt": "test", "width": 512, "height": 512}
            )
            
            assert result["content"][0]["data"] == "http://example.com/image.png"
            mock_send.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_call_tool_timeout(self, client):
        """Test timeout handling."""
        with patch.object(client, '_send_http_request', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = asyncio.TimeoutError()
            
            with pytest.raises(MCPTimeoutError):
                await client.call_tool(
                    "generate_image",
                    {"prompt": "test"}
                )
    
    @pytest.mark.asyncio
    async def test_call_tool_connection_error(self, client):
        """Test connection error handling."""
        with patch.object(client, '_send_http_request', new_callable=AsyncMock) as mock_send:
            mock_send.side_effect = ConnectionError("Cannot connect to server")
            
            with pytest.raises(MCPConnectionError):
                await client.call_tool(
                    "generate_image",
                    {"prompt": "test"}
                )
    
    @pytest.mark.asyncio
    async def test_context_manager_http_client(self, client):
        """Test async context manager for session management."""
        async with client as c:
            assert c._session is not None
        
        # After exit, session should be closed
        assert client._session is None or client._session.closed


class TestMCPExceptions:
    """Test custom MCP exceptions."""
    
    def test_mcp_tool_call_error(self):
        """Test MCPToolCallError with details."""
        error = MCPToolCallError(
            message="Tool not found",
            code=-32602,
            tool_name="unknown_tool"
        )
        
        assert str(error) == "Tool not found"
        assert error.code == -32602
        assert error.tool_name == "unknown_tool"
    
    def test_mcp_timeout_error(self):
        """Test MCPTimeoutError."""
        error = MCPTimeoutError("Request timed out after 60 seconds")
        
        assert "60 seconds" in str(error)
    
    def test_mcp_connection_error(self):
        """Test MCPConnectionError."""
        error = MCPConnectionError("Cannot connect to MCP server")
        
        assert "Cannot connect" in str(error)
