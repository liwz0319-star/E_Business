"""
User Settings Domain Entity

Represents the core UserSettings entity in the domain layer.
This is a pure Python class with no external dependencies.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4


# Default settings values
DEFAULT_SETTINGS = {
    "language": "en-US",
    "tone": "professional",
    "aspect_ratio": "1:1",
    "shopify_config": {"connected": False},
    "amazon_config": {"connected": False},
    "tiktok_config": {"connected": False},
}

# Valid values for validation
VALID_LANGUAGES = ["en-US", "zh-CN", "zh-TW", "ja-JP", "ko-KR"]
VALID_TONES = ["professional", "casual", "playful", "luxury", "minimal"]
VALID_ASPECT_RATIOS = ["1:1", "4:3", "3:4", "16:9", "9:16"]


@dataclass
class UserSettings:
    """
    UserSettings domain entity.

    Stores user preferences for AI generation and platform integrations.
    One-to-one relationship with User entity.
    """

    user_id: UUID
    id: Optional[UUID] = None
    language: str = "en-US"
    tone: str = "professional"
    aspect_ratio: str = "1:1"
    shopify_config: Dict[str, Any] = field(default_factory=lambda: {"connected": False})
    amazon_config: Dict[str, Any] = field(default_factory=lambda: {"connected": False})
    tiktok_config: Dict[str, Any] = field(default_factory=lambda: {"connected": False})
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def create(
        cls,
        user_id: UUID,
        language: str = "en-US",
        tone: str = "professional",
        aspect_ratio: str = "1:1",
        shopify_config: Optional[Dict[str, Any]] = None,
        amazon_config: Optional[Dict[str, Any]] = None,
        tiktok_config: Optional[Dict[str, Any]] = None,
    ) -> "UserSettings":
        """
        Factory method to create a new UserSettings entity with defaults.

        Args:
            user_id: The user's UUID
            language: AI language preference
            tone: AI tone preference
            aspect_ratio: AI aspect ratio preference
            shopify_config: Shopify integration config
            amazon_config: Amazon integration config
            tiktok_config: TikTok integration config

        Returns:
            New UserSettings instance
        """
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            user_id=user_id,
            language=language,
            tone=tone,
            aspect_ratio=aspect_ratio,
            shopify_config=shopify_config or {"connected": False},
            amazon_config=amazon_config or {"connected": False},
            tiktok_config=tiktok_config or {"connected": False},
            created_at=now,
            updated_at=now,
        )

    @classmethod
    def create_with_defaults(cls, user_id: UUID) -> "UserSettings":
        """
        Factory method to create UserSettings with all default values.

        Args:
            user_id: The user's UUID

        Returns:
            New UserSettings instance with default values
        """
        return cls.create(user_id=user_id)

    def update(
        self,
        language: Optional[str] = None,
        tone: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        shopify_config: Optional[Dict[str, Any]] = None,
        amazon_config: Optional[Dict[str, Any]] = None,
        tiktok_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Update settings with partial values.

        Only updates fields that are explicitly provided.

        Args:
            language: New language preference (optional)
            tone: New tone preference (optional)
            aspect_ratio: New aspect ratio preference (optional)
            shopify_config: New Shopify config (optional, merged with existing)
            amazon_config: New Amazon config (optional, merged with existing)
            tiktok_config: New TikTok config (optional, merged with existing)
        """
        if language is not None:
            self.language = language
        if tone is not None:
            self.tone = tone
        if aspect_ratio is not None:
            self.aspect_ratio = aspect_ratio
        if shopify_config is not None:
            self.shopify_config = {**self.shopify_config, **shopify_config}
        if amazon_config is not None:
            self.amazon_config = {**self.amazon_config, **amazon_config}
        if tiktok_config is not None:
            self.tiktok_config = {**self.tiktok_config, **tiktok_config}

        self.updated_at = datetime.utcnow()

    @property
    def ai_preferences(self) -> Dict[str, str]:
        """
        Get AI preferences as a dictionary.

        Returns:
            Dict with language, tone, and aspect_ratio
        """
        return {
            "language": self.language,
            "tone": self.tone,
            "aspect_ratio": self.aspect_ratio,
        }

    @property
    def integrations(self) -> Dict[str, Dict[str, Any]]:
        """
        Get integration configs as a dictionary.

        Returns:
            Dict with shopify, amazon, and tiktok configs
        """
        return {
            "shopify": self.shopify_config,
            "amazon": self.amazon_config,
            "tiktok": self.tiktok_config,
        }
