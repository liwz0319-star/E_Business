"""
Generator interface definition.
"""
from typing import AsyncIterator, Protocol, runtime_checkable

from app.domain.entities.generation import GenerationRequest, GenerationResult, StreamChunk

@runtime_checkable
class IGenerator(Protocol):
    """Interface for AI content generators."""
    
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Synchronous generation."""
        ...

    async def generate_stream(self, request: GenerationRequest) -> AsyncIterator[StreamChunk]:
        """Streaming generation with StreamChunk objects containing content and reasoning."""
        ...
