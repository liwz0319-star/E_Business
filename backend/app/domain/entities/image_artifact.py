"""
Image Artifact Entity.

Domain entity representing a generated image and its metadata.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class ImageArtifact:
    """Domain entity for a generated image artifact.
    
    Represents the result of an image generation request,
    including the image URL and associated metadata.
    
    Attributes:
        url: URL where the generated image is accessible
        prompt: The optimized prompt used for generation
        original_prompt: The original user prompt before optimization
        provider: Name of the image generation provider (e.g., "mcp", "mock")
        width: Image width in pixels
        height: Image height in pixels
        created_at: Timestamp when the image was generated
        id: Unique identifier for this artifact
        workflow_id: ID of the workflow that generated this image
    """
    url: str
    prompt: str
    original_prompt: str = ""
    provider: str = "unknown"
    width: int = 512
    height: int = 512
    created_at: datetime = field(default_factory=datetime.utcnow)
    id: UUID = field(default_factory=uuid4)
    workflow_id: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert artifact to dictionary for serialization."""
        return {
            "id": str(self.id),
            "url": self.url,
            "prompt": self.prompt,
            "original_prompt": self.original_prompt,
            "provider": self.provider,
            "width": self.width,
            "height": self.height,
            "created_at": self.created_at.isoformat(),
            "workflow_id": self.workflow_id,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "ImageArtifact":
        """Create artifact from dictionary."""
        artifact_id = data.get("id")
        if artifact_id and isinstance(artifact_id, str):
            artifact_id = UUID(artifact_id)
        
        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        
        return cls(
            url=data.get("url", ""),
            prompt=data.get("prompt", ""),
            original_prompt=data.get("original_prompt", ""),
            provider=data.get("provider", "unknown"),
            width=data.get("width", 512),
            height=data.get("height", 512),
            created_at=created_at or datetime.utcnow(),
            id=artifact_id or uuid4(),
            workflow_id=data.get("workflow_id"),
        )
