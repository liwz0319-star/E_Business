"""
MCP Base Client.

Provides base classes for MCP (Model Context Protocol) communication.
Supports both HTTP and Stdio transport mechanisms.
"""
import asyncio
import logging
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from uuid import uuid4

import aiohttp


logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================

class MCPError(Exception):
    """Base exception for MCP operations."""
    pass


class MCPToolCallError(MCPError):
    """Error during MCP tool call."""
    
    def __init__(
        self,
        message: str,
        code: Optional[int] = None,
        tool_name: Optional[str] = None,
    ):
        super().__init__(message)
        self.code = code
        self.tool_name = tool_name


class MCPTimeoutError(MCPError):
    """MCP request timed out."""
    pass


class MCPConnectionError(MCPError):
    """Failed to connect to MCP server."""
    pass


class MCPProtocolError(MCPError):
    """Invalid MCP protocol response."""
    pass


# ============================================================================
# Abstract Base Client
# ============================================================================

class MCPBaseClient(ABC):
    """Abstract base class for MCP clients.
    
    Defines the interface for MCP protocol communication.
    Subclasses implement specific transport mechanisms (HTTP, Stdio).
    """
    
    @abstractmethod
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Call an MCP tool.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments as a dictionary
            
        Returns:
            Parsed MCP result dictionary
            
        Raises:
            MCPToolCallError: If tool call fails
            MCPTimeoutError: If request times out
            MCPConnectionError: If connection fails
        """
        pass
    
    @abstractmethod
    async def __aenter__(self) -> "MCPBaseClient":
        """Enter async context manager."""
        pass
    
    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit async context manager."""
        pass


# ============================================================================
# HTTP Transport Client
# ============================================================================

class MCPHttpClient(MCPBaseClient):
    """MCP client using HTTP transport.
    
    Implements MCP JSON-RPC over HTTP for tool invocations.
    
    Example:
        async with MCPHttpClient("http://localhost:3000") as client:
            result = await client.call_tool(
                "generate_image",
                {"prompt": "a cat", "width": 512, "height": 512}
            )
    """
    
    def __init__(
        self,
        server_url: str,
        timeout: int = 60,
        headers: Optional[Dict[str, str]] = None,
    ):
        """Initialize HTTP client.
        
        Args:
            server_url: MCP server HTTP endpoint
            timeout: Request timeout in seconds
            headers: Optional HTTP headers
        """
        self.server_url = server_url.rstrip("/")
        self.timeout = timeout
        self.headers = headers or {}
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self) -> "MCPHttpClient":
        """Create HTTP session on context entry."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Close HTTP session on context exit."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None
    
    def format_mcp_request(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Format a request according to MCP JSON-RPC spec.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            MCP-compliant JSON-RPC request dictionary
        """
        return {
            "jsonrpc": "2.0",
            "id": str(uuid4()),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments,
            },
        }
    
    def parse_mcp_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse MCP JSON-RPC response.
        
        Args:
            response: Raw response dictionary
            
        Returns:
            The result portion of the response
            
        Raises:
            MCPToolCallError: If response contains an error
            MCPProtocolError: If response format is invalid
        """
        # Check for JSON-RPC error
        if "error" in response:
            error = response["error"]
            raise MCPToolCallError(
                message=error.get("message", "Unknown MCP error"),
                code=error.get("code"),
                tool_name=error.get("data", {}).get("tool_name"),
            )
        
        # Validate response structure
        if "result" not in response:
            raise MCPProtocolError("Invalid MCP response: missing 'result' field")
        
        return response["result"]
    
    async def _send_http_request(
        self,
        request: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Send HTTP POST request to MCP server.
        
        Args:
            request: MCP JSON-RPC request
            
        Returns:
            Parsed JSON response
            
        Raises:
            MCPConnectionError: If connection fails
            MCPTimeoutError: If request times out
        """
        if self._session is None:
            # Create session if not using context manager
            self._session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout),
            )
        
        try:
            async with self._session.post(
                self.server_url,
                json=request,
                headers={"Content-Type": "application/json"},
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
                
        except asyncio.TimeoutError as e:
            raise MCPTimeoutError(
                f"Request timed out after {self.timeout} seconds"
            ) from e
        except aiohttp.ClientConnectionError as e:
            raise MCPConnectionError(
                f"Failed to connect to MCP server: {e}"
            ) from e
        except aiohttp.ClientError as e:
            raise MCPConnectionError(
                f"HTTP client error: {e}"
            ) from e
    
    async def call_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Call an MCP tool via HTTP.
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Parsed MCP result dictionary
        """
        logger.debug(f"Calling MCP tool '{tool_name}' with args: {arguments}")
        
        request = self.format_mcp_request(tool_name, arguments)
        
        try:
            response = await self._send_http_request(request)
            result = self.parse_mcp_response(response)
            
            logger.debug(f"MCP tool '{tool_name}' returned successfully")
            return result
            
        except (MCPToolCallError, MCPTimeoutError, MCPConnectionError):
            raise
        except asyncio.TimeoutError as e:
            raise MCPTimeoutError(
                f"Request timed out after {self.timeout} seconds"
            ) from e
        except ConnectionError as e:
            raise MCPConnectionError(str(e)) from e
        except Exception as e:
            logger.error(f"Unexpected error calling MCP tool '{tool_name}': {e}")
            raise MCPToolCallError(
                message=f"Unexpected error: {e}",
                tool_name=tool_name,
            ) from e
