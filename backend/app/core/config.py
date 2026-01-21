"""
Application Settings Configuration

Uses pydantic-settings for environment variable management and validation.
All settings are loaded from environment variables with .env file support.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Environment variables can be set directly or loaded from a .env file
    in the project root directory.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Database Configuration
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/e_business",
        description="PostgreSQL async connection URL"
    )
    
    # Redis Configuration
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    
    # Security Configuration
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT signing"
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="JWT token expiration in minutes"
    )
    
    # AI Provider Configuration
    deepseek_api_key: Optional[str] = Field(
        default=None,
        description="DeepSeek API key for AI generation"
    )
    
    # MinIO Configuration
    minio_endpoint: str = Field(
        default="localhost:9000",
        description="MinIO endpoint"
    )
    minio_access_key: str = Field(
        default="minioadmin",
        description="MinIO access key"
    )
    minio_secret_key: str = Field(
        default="minioadmin",
        description="MinIO secret key"
    )
    minio_bucket: str = Field(
        default="e-business",
        description="MinIO bucket name"
    )
    
    # Application Settings
    app_env: str = Field(
        default="development",
        description="Application environment"
    )
    debug: bool = Field(
        default=True,
        description="Debug mode"
    )
    cors_origins: str = Field(
        default="http://localhost:3000,http://localhost:8000",
        description="CORS allowed origins (comma-separated)"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level"
    )
    
    @field_validator("app_env")
    @classmethod
    def validate_app_env(cls, v: str) -> str:
        """Validate application environment."""
        allowed = {"development", "staging", "production"}
        if v.lower() not in allowed:
            raise ValueError(f"app_env must be one of: {allowed}")
        return v.lower()
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.app_env == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.app_env == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Uses lru_cache to create a singleton settings instance.
    """
    return Settings()


# Convenience export
settings = get_settings()
