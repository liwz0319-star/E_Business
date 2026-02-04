"""
Domain entities module.

Contains core business entities that represent the domain model.
"""

from .generation import (
    GenerationRequest,
    GenerationResult,
    GenerationStatus,
    GenerationType,
    StreamChunk,
)
from .user import User
from .agent_state import (
    CopywritingState,
    CopywritingStage,
    InvalidStageTransitionError,
    VALID_TRANSITIONS,
)

__all__ = [
    "User",
    "GenerationRequest",
    "GenerationResult",
    "GenerationStatus",
    "GenerationType",
    "StreamChunk",
    "CopywritingState",
    "CopywritingStage",
    "InvalidStageTransitionError",
    "VALID_TRANSITIONS",
]

