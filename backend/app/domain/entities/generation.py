"""
Generation domain entities.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

class GenerationStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class GenerationType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"

@dataclass
class GenerationRequest:
    """Request for text generation."""
    prompt: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    
    # Provider specific config
    provider_config: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GenerationResult:
    """Result of text generation."""
    content: str
    raw_response: Dict[str, Any]
    usage: Optional[Dict[str, int]] = None

@dataclass
class StreamChunk:
    """Chunk of streaming response."""
    content: str
    reasoning_content: Optional[str] = None
    finish_reason: Optional[str] = None
