"""
MCP Infrastructure Module.

Contains MCP (Model Context Protocol) client implementations.
"""

from .image_client import MockMCPImageGenerator
from .base_client import (
    MCPBaseClient,
    MCPHttpClient,
    MCPError,
    MCPToolCallError,
    MCPTimeoutError,
    MCPConnectionError,
    MCPProtocolError,
)
from .mcp_image_generator import (
    MCPImageGenerator,
    MCPImageGeneratorError,
    MCPInvalidURLError,
)

__all__ = [
    # Mock client (for testing)
    "MockMCPImageGenerator",
    # Real MCP clients
    "MCPBaseClient",
    "MCPHttpClient",
    "MCPImageGenerator",
    # Exceptions
    "MCPError",
    "MCPToolCallError",
    "MCPTimeoutError",
    "MCPConnectionError",
    "MCPProtocolError",
    "MCPImageGeneratorError",
    "MCPInvalidURLError",
]

