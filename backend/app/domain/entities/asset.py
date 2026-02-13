"""
Asset Domain Entity.

Unified domain entity representing all asset types (image, video, text)
for the Asset Gallery feature.
"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Any
from uuid import UUID, uuid4


def _relative_time(dt: datetime) -> str:
    """
    Generate a human-readable relative time string.

    Args:
        dt: The datetime to compare against now

    Returns:
        Human-readable string like "2 hours ago", "3 days ago", etc.
    """
    if dt is None:
        return "unknown"

    # Ensure we're comparing timezone-aware datetimes
    now = datetime.now(timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    diff = now - dt
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    elif seconds < 2592000:  # 30 days
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''} ago"
    elif seconds < 31536000:  # 365 days
        months = seconds // 2592000
        return f"{months} month{'s' if months != 1 else ''} ago"
    else:
        years = seconds // 31536000
        return f"{years} year{'s' if years != 1 else ''} ago"


@dataclass
class Asset:
    """
    Domain entity for a generated asset (image, video, or text).

    Represents the unified asset model used by the Asset Gallery API.
    Supports all three asset types with appropriate field handling.

    Attributes:
        id: Unique identifier (UUID)
        db_id: Database integer ID (set after persistence)
        title: Display title (nullable, fallback to truncated prompt)
        content: Text content for copy/text assets (nullable)
        url: URL for image/video assets (nullable for text-only)
        asset_type: Type of asset - 'image', 'video', or 'text'
        prompt: The prompt used to generate this asset
        original_prompt: Original user prompt before optimization
        provider: Provider name (e.g., 'mcp', 'deepseek')
        width: Width in pixels (0 for text assets)
        height: Height in pixels (0 for text assets)
        metadata: Additional metadata as dict (duration, format, etc.)
        user_id: Owner user ID
        workflow_id: Associated workflow ID
        created_at: Creation timestamp
    """
    id: UUID
    asset_type: str  # 'image', 'video', 'text'
    prompt: str
    db_id: Optional[int] = None  # Database integer ID
    title: Optional[str] = None
    content: Optional[str] = None
    url: Optional[str] = None
    original_prompt: Optional[str] = None
    provider: str = "unknown"
    width: int = 512
    height: int = 512
    metadata: Optional[dict] = None
    user_id: Optional[UUID] = None
    workflow_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate asset type."""
        valid_types = {"image", "video", "text"}
        if self.asset_type not in valid_types:
            raise ValueError(f"Invalid asset_type: {self.asset_type}. Must be one of {valid_types}")

    @property
    def is_vertical(self) -> bool:
        """Check if asset is vertically oriented (height > width)."""
        return self.height > self.width if self.width > 0 else False

    @property
    def is_text(self) -> bool:
        """Check if this is a text/copy asset."""
        return self.asset_type == "text"

    @property
    def display_title(self) -> str:
        """Get display title, falling back to truncated prompt if title is None."""
        if self.title:
            return self.title
        # Fallback to first 50 chars of prompt
        return self.prompt[:50] + "..." if len(self.prompt) > 50 else self.prompt

    @property
    def tag(self) -> str:
        """Get the tag for frontend display."""
        tag_mapping = {
            "image": "IMG",
            "video": "VIDEO",
            "text": "COPY",
        }
        return tag_mapping.get(self.asset_type, "ASSET")

    @property
    def category(self) -> str:
        """Get the category for frontend display."""
        category_mapping = {
            "image": "Product Images",
            "video": "Ad Videos",
            "text": "Marketing Copy",
        }
        return category_mapping.get(self.asset_type, "Assets")

    @property
    def meta_string(self) -> str:
        """Generate meta string for frontend display."""
        if self.asset_type == "image":
            resolution = "4K" if self.width >= 2160 or self.height >= 2160 else "High-res"
            return f"{resolution} Render • {self.width}x{self.height}"
        elif self.asset_type == "video":
            orientation = "9:16 Vertical" if self.is_vertical else "16:9 Horizontal"
            return f"{orientation} • Social Media"
        else:  # text
            return f"Generated {_relative_time(self.created_at)}"

    @property
    def duration(self) -> Optional[str]:
        """Get video duration from metadata if available."""
        if self.metadata and "duration" in self.metadata:
            return self.metadata["duration"]
        return None

    def to_dict(self) -> dict:
        """Convert asset to dictionary for serialization."""
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "url": self.url,
            "asset_type": self.asset_type,
            "prompt": self.prompt,
            "original_prompt": self.original_prompt,
            "provider": self.provider,
            "width": self.width,
            "height": self.height,
            "metadata": self.metadata,
            "user_id": str(self.user_id) if self.user_id else None,
            "workflow_id": self.workflow_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Asset":
        """Create asset from dictionary."""
        asset_id = data.get("id")
        if asset_id and isinstance(asset_id, str):
            asset_id = UUID(asset_id)

        user_id = data.get("user_id")
        if user_id and isinstance(user_id, str):
            user_id = UUID(user_id)

        created_at = data.get("created_at")
        if created_at and isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))

        return cls(
            id=asset_id or uuid4(),
            title=data.get("title"),
            content=data.get("content"),
            url=data.get("url"),
            asset_type=data.get("asset_type", "image"),
            prompt=data.get("prompt", ""),
            original_prompt=data.get("original_prompt"),
            provider=data.get("provider", "unknown"),
            width=data.get("width", 512),
            height=data.get("height", 512),
            metadata=data.get("metadata"),
            user_id=user_id,
            workflow_id=data.get("workflow_id"),
            created_at=created_at or datetime.utcnow(),
        )
