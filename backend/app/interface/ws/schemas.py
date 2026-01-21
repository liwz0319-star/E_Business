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
