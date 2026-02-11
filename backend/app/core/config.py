"""
Application Settings Configuration

Uses pydantic-settings for environment variable management and validation.
All settings are loaded from environment variables with .env file support.
"""

from pathlib import Path
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
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
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
    deepseek_model: str = Field(
        default="deepseek-chat",
        description="DeepSeek model name"
    )
    deepseek_max_tokens: int = Field(
        default=2000,
        description="Maximum tokens for DeepSeek generation"
    )
    deepseek_timeout: int = Field(
        default=120,
        description="Timeout in seconds for DeepSeek API calls"
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
    error_log_cooldown_seconds: int = Field(
        default=5,
        description="Cooldown in seconds between same error logs"
    )
    
    # MCP Image Generation Configuration
    mcp_image_server_url: str = Field(
        default="http://localhost:3000",
        description="MCP Server URL for image generation"
    )
    mcp_image_use_stdio: bool = Field(
        default=False,
        description="Use Stdio mode instead of HTTP for MCP"
    )
    mcp_image_timeout: int = Field(
        default=60,
        description="Request timeout in seconds for MCP image generation"
    )
    mcp_image_model: str = Field(
        default="stable-diffusion-xl",
        description="Default model for image generation"
    )
    image_generator_provider: str = Field(
        default="mock",
        description="Image generator provider: 'mock' or 'mcp'"
    )
    minio_secure: bool = Field(
        default=False,
        description="Use HTTPS for MinIO connections"
    )
    minio_max_size_mb: int = Field(
        default=10,
        description="Maximum upload size in MB for MinIO"
    )
    mcp_allowed_domains: str = Field(
        default="localhost,127.0.0.1,minio",
        description="Comma-separated list of allowed domains for MCP URL validation (SSRF prevention)"
    )
    
    @property
    def mcp_allowed_domains_set(self) -> set:
        """Parse allowed domains string to set."""
        return {domain.strip() for domain in self.mcp_allowed_domains.split(",") if domain.strip()}

    # LangSmith Configuration
    langchain_tracing_v2: bool = Field(
        default=False,
        description="Enable LangSmith tracing"
    )
    langchain_api_key: Optional[str] = Field(
        default=None,
        description="LangSmith API key"
    )
    langchain_project: str = Field(
        default="e-business",
        description="LangSmith project name"
    )
    langchain_endpoint: str = Field(
        default="https://api.smith.langchain.com",
        description="LangSmith API endpoint"
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


def get_settings() -> Settings:
    """
    Get fresh settings instance.
    
    Returns a new Settings instance on each call to ensure
    environment variables are always read fresh, especially
    important for async task contexts.
    """
    return Settings()


# Convenience export
settings = get_settings()
