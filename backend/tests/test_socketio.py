"""
Socket.IO Integration Tests

Tests for Socket.IO connection with JWT authentication.
"""

import pytest
from datetime import datetime

from app.core.security import create_access_token
from app.interface.ws.socket_manager import SocketManager


class TestSocketManagerUnit:
    """Unit tests for SocketManager class."""
    
    def test_socket_manager_initialization(self):
        """Test that SocketManager initializes correctly."""
        manager = SocketManager()
        
        assert manager.sio is not None
        assert manager.app is not None
        assert manager._connected_users == {}
    
    def test_get_connected_count_empty(self):
        """Test connected count when no clients connected."""
        manager = SocketManager()
        
        assert manager.get_connected_count() == 0
    
    def test_get_user_id_not_found(self):
        """Test getting user ID for non-existent socket."""
        manager = SocketManager()
        
        result = manager.get_user_id("nonexistent-sid")
        assert result is None


class TestEventPayloadSchemas:
    """Tests for event payload Pydantic models."""
    
    def test_agent_thought_event(self):
        """Test AgentThoughtEvent schema."""
        from app.interface.ws.schemas import AgentThoughtEvent
        
        event = AgentThoughtEvent(
            workflow_id="test-workflow-123",
            data={"content": "Thinking about the problem..."}
        )
        
        assert event.type == "thought"
        assert event.workflow_id == "test-workflow-123"
        assert event.data["content"] == "Thinking about the problem..."
        assert isinstance(event.timestamp, datetime)
    
    def test_agent_tool_call_event(self):
        """Test AgentToolCallEvent schema."""
        from app.interface.ws.schemas import AgentToolCallEvent
        
        event = AgentToolCallEvent(
            workflow_id="test-workflow-123",
            data={
                "tool_name": "generate_image",
                "status": "in_progress",
                "message": "Generating..."
            }
        )
        
        assert event.type == "tool_call"
        assert event.data["tool_name"] == "generate_image"
    
    def test_agent_result_event(self):
        """Test AgentResultEvent schema."""
        from app.interface.ws.schemas import AgentResultEvent
        
        event = AgentResultEvent(
            workflow_id="test-workflow-123",
            data={"status": "success", "content": "Result here"}
        )
        
        assert event.type == "result"
        assert event.data["status"] == "success"
    
    def test_agent_error_event(self):
        """Test AgentErrorEvent schema."""
        from app.interface.ws.schemas import AgentErrorEvent
        
        event = AgentErrorEvent(
            workflow_id="test-workflow-123",
            data={
                "code": "GENERATION_FAILED",
                "message": "Failed to generate",
                "details": {}
            }
        )
        
        assert event.type == "error"
        assert event.data["code"] == "GENERATION_FAILED"


class TestJWTAuthenticationLogic:
    """Tests for JWT authentication logic used in Socket.IO."""
    
    def test_valid_token_decoded(self):
        """Test that valid JWT tokens are decoded correctly."""
        from app.core.security import decode_access_token
        
        token = create_access_token(data={"sub": "user-123"})
        payload = decode_access_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user-123"
    
    def test_invalid_token_returns_none(self):
        """Test that invalid tokens return None."""
        from app.core.security import decode_access_token
        
        payload = decode_access_token("invalid.token.string")
        assert payload is None
    
    def test_expired_token_returns_none(self):
        """Test that expired tokens return None."""
        from datetime import timedelta
        from app.core.security import decode_access_token
        
        token = create_access_token(
            data={"sub": "user-123"},
            expires_delta=timedelta(seconds=-10)  # Already expired
        )
        payload = decode_access_token(token)
        assert payload is None


# Note: Full Socket.IO integration tests require async Socket.IO client
# which may not work reliably in pytest. These tests cover the core logic.
