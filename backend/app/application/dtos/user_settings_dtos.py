"""
User Settings DTOs

Pydantic models for User Settings API request/response.
Uses camelCase aliases for frontend compatibility.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.alias_generators import to_camel

from app.domain.entities.user_settings import (
    VALID_LANGUAGES,
    VALID_TONES,
    VALID_ASPECT_RATIOS,
)


# === Request DTOs ===

class UpdateAIPreferencesDTO(BaseModel):
    """DTO for updating AI preferences in PATCH request."""

    language: Optional[str] = Field(
        None,
        description="AI language preference (e.g., 'en-US', 'zh-CN')",
    )
    tone: Optional[str] = Field(
        None,
        description="AI tone preference (e.g., 'professional', 'casual')",
    )
    aspect_ratio: Optional[str] = Field(
        None,
        alias="aspectRatio",
        description="AI aspect ratio preference (e.g., '1:1', '16:9')",
    )

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        """Validate language is one of the allowed values."""
        if v is not None and v not in VALID_LANGUAGES:
            raise ValueError(f"Invalid language. Must be one of: {VALID_LANGUAGES}")
        return v

    @field_validator("tone")
    @classmethod
    def validate_tone(cls, v: Optional[str]) -> Optional[str]:
        """Validate tone is one of the allowed values."""
        if v is not None and v not in VALID_TONES:
            raise ValueError(f"Invalid tone. Must be one of: {VALID_TONES}")
        return v

    @field_validator("aspect_ratio")
    @classmethod
    def validate_aspect_ratio(cls, v: Optional[str]) -> Optional[str]:
        """Validate aspect ratio is one of the allowed values."""
        if v is not None and v not in VALID_ASPECT_RATIOS:
            raise ValueError(f"Invalid aspect ratio. Must be one of: {VALID_ASPECT_RATIOS}")
        return v


class IntegrationConfigDTO(BaseModel):
    """DTO for a single integration configuration in PATCH request."""

    # connected is optional in request to allow partial updates of extension fields
    connected: Optional[bool] = Field(
        None,
        description="Whether the integration is connected",
    )

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",  # Allow additional fields like storeName, region, etc.
    )


class UpdateIntegrationsDTO(BaseModel):
    """DTO for updating integration configurations in PATCH request."""

    shopify: Optional[IntegrationConfigDTO] = Field(
        None,
        description="Shopify integration configuration",
    )
    amazon: Optional[IntegrationConfigDTO] = Field(
        None,
        description="Amazon integration configuration",
    )
    tiktok: Optional[IntegrationConfigDTO] = Field(
        None,
        description="TikTok integration configuration",
    )


class UpdateUserSettingsRequestDTO(BaseModel):
    """DTO for PATCH /api/v1/user/settings request body."""

    ai_preferences: Optional[UpdateAIPreferencesDTO] = Field(
        None,
        alias="aiPreferences",
        description="AI preferences to update",
    )
    integrations: Optional[UpdateIntegrationsDTO] = Field(
        None,
        description="Integration configurations to update",
    )

    model_config = ConfigDict(populate_by_name=True)


# === Response DTOs ===

class AIPreferencesResponseDTO(BaseModel):
    """DTO for AI preferences in response."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    language: str = Field(..., description="AI language preference")
    tone: str = Field(..., description="AI tone preference")
    aspect_ratio: str = Field(..., alias="aspectRatio", description="AI aspect ratio preference")


class IntegrationResponseDTO(BaseModel):
    """DTO for a single integration in response."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",  # Allow additional fields
    )

    connected: bool = Field(..., description="Whether the integration is connected")


class IntegrationsResponseDTO(BaseModel):
    """DTO for all integrations in response."""

    shopify: IntegrationResponseDTO = Field(
        ...,
        description="Shopify integration status",
    )
    amazon: IntegrationResponseDTO = Field(
        ...,
        description="Amazon integration status",
    )
    tiktok: IntegrationResponseDTO = Field(
        ...,
        description="TikTok integration status",
    )


class UserSettingsResponseDTO(BaseModel):
    """
    DTO for GET /api/v1/user/settings response.

    Matches the format expected by Settings.tsx frontend component.
    Uses camelCase aliases for JSON serialization.
    """

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    ai_preferences: AIPreferencesResponseDTO = Field(
        ...,
        alias="aiPreferences",
        description="AI generation preferences",
    )
    integrations: IntegrationsResponseDTO = Field(
        ...,
        description="Platform integration configurations",
    )
    updated_at: datetime = Field(
        ...,
        alias="updatedAt",
        description="Last update timestamp",
    )
