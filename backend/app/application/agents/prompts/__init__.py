"""
Prompt templates for AI agents.

This module provides centralized prompt management for agent workflows.
"""

from app.application.agents.prompts.copywriting_prompts import (
    COPYWRITING_PROMPTS,
    CopywritingPrompts,
)
from app.application.agents.prompts.image_prompts import (
    IMAGE_PROMPTS,
    ImagePrompts,
)

__all__ = [
    "COPYWRITING_PROMPTS",
    "CopywritingPrompts",
    "IMAGE_PROMPTS",
    "ImagePrompts",
]

