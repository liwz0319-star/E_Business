# Project Handover Report: Story 1.3 Socket.io Server

**Date**: 2026-01-21
**Status**: 🔴 **CRITICAL REGRESSION** (Files Missing)

## 🚨 Critical Situation
The following implementation files are **MISSING** from the disk (likely deleted as they were untracked):
- `backend/app/interface/ws/socket_manager.py`
- `backend/app/interface/ws/schemas.py`

## 🛠 Progress Snapshot
Before deletion, the following fixes were applied:
1. **Fixed Path Double Config**: Removed `socketio_path="/ws"` from manager to avoid `/ws/ws/` issue.
2. **Schema Aliases**: Added `alias="workflowId"` to Pydantic models.
3. **Settings**: Updated CORS to use `settings.cors_origins_list` instead of `os.getenv`.
4. **Resilience**: Added error handling to all `emit_*` methods.
5. **Modernization**: Replaced deprecated `datetime.utcnow`.

## 👉 Instructions for Next Agent

1. **RESTORE FILES**: recreate the files using the content provided below.
2. **GIT ADD**: Immediately run `git add backend/app/interface/ws/` to track them.
3. **RESUME FIXES**:
   - Issue **HIGH-4**: `tests/test_socketio_integration.py` uses mocks. Rewrite to use real `python-socketio` client.
   - Issue **MEDIUM-3**: Add rate limiting.

---

## 💾 Restoration Content

### 1. `backend/app/interface/ws/schemas.py`

```python
"""
Socket.IO Event Payload Schemas

Defines Pydantic models for real-time event payloads.
"""

from datetime import datetime, timezone
from typing import Any, Dict, Literal

from pydantic import BaseModel, ConfigDict, Field


class BaseEventPayload(BaseModel):
    """Base class for all Socket.IO event payloads."""
    
    model_config = ConfigDict(populate_by_name=True)
    
    workflow_id: str = Field(..., alias="workflowId", description="Unique ID of the workflow/conversation")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp in ISO8601 format")


class AgentThoughtEvent(BaseEventPayload):
    """
    Event for intermediate reasoning steps from the LLM.
    
    Emitted on: agent:thought
    """
    
    type: Literal["thought"] = "thought"
    data: Dict[str, Any] = Field(..., description="Thought content")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "thought",
                "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
                "data": {"content": "Analyzing the user request..."},
                "timestamp": "2026-01-21T12:00:00Z"
            }
        }
    }


class AgentToolCallEvent(BaseEventPayload):
    """
    Event when agent invokes a tool.
    
    Emitted on: agent:tool_call
    """
    
    type: Literal["tool_call"] = "tool_call"
    data: Dict[str, Any] = Field(..., description="Tool call details")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "tool_call",
                "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
                "data": {
                    "tool_name": "generate_image",
                    "status": "in_progress",
                    "message": "Generating image..."
                },
                "timestamp": "2026-01-21T12:00:01Z"
            }
        }
    }


class AgentResultEvent(BaseEventPayload):
    """
    Event for final output from agent.
    
    Emitted on: agent:result
    """
    
    type: Literal["result"] = "result"
    data: Dict[str, Any] = Field(..., description="Final result payload")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "result",
                "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
                "data": {
                    "status": "success",
                    "content_type": "text",
                    "content": "Here is your generated content..."
                },
                "timestamp": "2026-01-21T12:00:05Z"
            }
        }
    }


class AgentErrorEvent(BaseEventPayload):
    """
    Event for errors during agent execution.
    
    Emitted on: agent:error
    """
    
    type: Literal["error"] = "error"
    data: Dict[str, Any] = Field(..., description="Error details")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "error",
                "workflow_id": "550e8400-e29b-41d4-a716-446655440000",
                "data": {
                    "code": "GENERATION_FAILED",
                    "message": "Failed to generate content",
                    "details": {}
                },
                "timestamp": "2026-01-21T12:00:05Z"
            }
        }
    }
```

### 2. `backend/app/interface/ws/socket_manager.py`

```python
"""
Socket.IO Manager

Provides Socket.IO server with JWT authentication for real-time agent events.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import socketio

from app.core.config import settings
from app.core.security import decode_access_token

logger = logging.getLogger(__name__)


class SocketManager:
    """
    Socket.IO Manager for handling WebSocket connections with JWT authentication.
    
    Provides methods for:
    - Authenticated connection handling
    - Event emission (agent:thought, agent:tool_call, agent:result, agent:error)
    """
    
    def __init__(self):
        # Get CORS origins from settings (filter empty strings)
        cors_origins = [
            origin for origin in settings.cors_origins_list 
            if origin  # Filter empty strings
        ]
        
        # Create async Socket.IO server
        self.sio = socketio.AsyncServer(
            async_mode="asgi",
            cors_allowed_origins=cors_origins,
            cors_credentials=True,
            logger=False,
            engineio_logger=False,
        )
        
        # Create ASGI app for mounting
        # Note: socketio_path is NOT set here because main.py mounts at /ws
        self.app = socketio.ASGIApp(self.sio)
        
        # Store connected users: {sid: user_id}
        self._connected_users: Dict[str, str] = {}
        
        # Register event handlers
        self._register_handlers()
    
    def _register_handlers(self) -> None:
        """Register Socket.IO event handlers."""
        
        @self.sio.event
        async def connect(sid: str, environ: dict, auth: Optional[dict] = None) -> bool:
            """
            Handle client connection with JWT authentication.
            
            Args:
                sid: Socket ID
                environ: WSGI environ dict
                auth: Authentication data from client handshake
                
            Returns:
                True if connection accepted, False to reject
            """
            logger.info(f"Connection attempt from sid={sid}")
            
            # Check for auth token
            if not auth or "token" not in auth:
                logger.warning(f"Connection rejected: No token provided (sid={sid})")
                raise socketio.exceptions.ConnectionRefusedError("Authentication required")
            
            token = auth.get("token", "")
            
            # Validate JWT token
            payload = decode_access_token(token)
            if payload is None:
                logger.warning(f"Connection rejected: Invalid token (sid={sid})")
                raise socketio.exceptions.ConnectionRefusedError("Invalid or expired token")
            
            # Extract user ID from token
            user_id = payload.get("sub")
            if not user_id:
                logger.warning(f"Connection rejected: No user ID in token (sid={sid})")
                raise socketio.exceptions.ConnectionRefusedError("Invalid token payload")
            
            # Store user mapping
            self._connected_users[sid] = user_id
            
            logger.info(f"Connection accepted: sid={sid}, user_id={user_id}")
            return True
        
        @self.sio.event
        async def disconnect(sid: str) -> None:
            """Handle client disconnection."""
            user_id = self._connected_users.pop(sid, None)
            logger.info(f"Client disconnected: sid={sid}, user_id={user_id}")
    
    async def emit_thought(
        self,
        workflow_id: str,
        content: str,
        sid: Optional[str] = None
    ) -> None:
        """
        Emit agent:thought event.
        
        Args:
            workflow_id: Workflow/conversation ID
            content: Thought content
            sid: Optional specific socket ID (broadcasts if None)
        """
        payload = {
            "type": "thought",
            "workflowId": workflow_id,
            "data": {"content": content},
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        
        try:
            await self.sio.emit("agent:thought", payload, room=sid)
            logger.debug(f"Emitted agent:thought: workflow_id={workflow_id}")
        except Exception as e:
            logger.error(f"Failed to emit agent:thought: {e}")
    
    async def emit_tool_call(
        self,
        workflow_id: str,
        tool_name: str,
        status: str,
        message: str,
        sid: Optional[str] = None
    ) -> None:
        """
        Emit agent:tool_call event.
        
        Args:
            workflow_id: Workflow/conversation ID
            tool_name: Name of the tool being called
            status: Status (e.g., "in_progress", "completed")
            message: Status message
            sid: Optional specific socket ID
        """
        payload = {
            "type": "tool_call",
            "workflowId": workflow_id,
            "data": {
                "tool_name": tool_name,
                "status": status,
                "message": message
            },
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        
        try:
            await self.sio.emit("agent:tool_call", payload, room=sid)
            logger.debug(f"Emitted agent:tool_call: workflow_id={workflow_id}, tool={tool_name}")
        except Exception as e:
            logger.error(f"Failed to emit agent:tool_call: {e}")
    
    async def emit_result(
        self,
        workflow_id: str,
        result_data: Dict[str, Any],
        sid: Optional[str] = None
    ) -> None:
        """
        Emit agent:result event.
        
        Args:
            workflow_id: Workflow/conversation ID
            result_data: Final result payload
            sid: Optional specific socket ID
        """
        payload = {
            "type": "result",
            "workflowId": workflow_id,
            "data": result_data,
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        
        try:
            await self.sio.emit("agent:result", payload, room=sid)
            logger.info(f"Emitted agent:result: workflow_id={workflow_id}")
        except Exception as e:
            logger.error(f"Failed to emit agent:result: {e}")
    
    async def emit_error(
        self,
        workflow_id: str,
        error_code: str,
        error_message: str,
        details: Optional[Dict[str, Any]] = None,
        sid: Optional[str] = None
    ) -> None:
        """
        Emit agent:error event.
        
        Args:
            workflow_id: Workflow/conversation ID
            error_code: Error code
            error_message: Error message
            details: Optional additional error details
            sid: Optional specific socket ID
        """
        payload = {
            "type": "error",
            "workflowId": workflow_id,
            "data": {
                "code": error_code,
                "message": error_message,
                "details": details or {}
            },
            "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        }
        
        try:
            await self.sio.emit("agent:error", payload, room=sid)
            logger.warning(f"Emitted agent:error: workflow_id={workflow_id}, code={error_code}")
        except Exception as e:
            logger.error(f"Failed to emit agent:error: {e}")
    
    def get_user_id(self, sid: str) -> Optional[str]:
        """Get user ID for a socket ID."""
        return self._connected_users.get(sid)
    
    def get_connected_count(self) -> int:
        """Get number of connected clients."""
        return len(self._connected_users)


# Singleton instance
socket_manager = SocketManager()
```
