"""
Image Generator Factory Module.

Manages registration and instantiation of image generation providers.
"""
import logging
from typing import Any, Callable, Dict, Optional

from app.domain.interfaces.image_generator import IImageGenerator
from app.domain.exceptions import ProviderNotFoundError
from app.core.config import settings


logger = logging.getLogger(__name__)


# Type for factory functions that create image generators
ImageGeneratorFactory = Callable[..., IImageGenerator]


class ImageProviderFactory:
    """
    Factory for creating image generator instances.
    
    Supports lazy registration of providers to avoid circular imports
    and unnecessary initialization.
    """
    _registry: Dict[str, ImageGeneratorFactory] = {}
    _initialized: bool = False

    @classmethod
    def register(cls, key: str, factory: ImageGeneratorFactory) -> None:
        """
        Register an image generator factory with a string key.
        
        Args:
            key: Provider key (e.g., "mock", "mcp")
            factory: Callable that creates an IImageGenerator instance
        """
        key = key.lower()
        if key in cls._registry:
            logger.warning(f"Overwriting image provider registration for key: {key}")
        
        cls._registry[key] = factory
        logger.info(f"Registered image provider: {key}")

    @classmethod
    def get_provider(cls, key: Optional[str] = None, **kwargs) -> IImageGenerator:
        """
        Get an instance of an image generator by key.
        
        Args:
            key: Provider key. If None, uses settings.image_generator_provider
            **kwargs: Additional arguments passed to factory
            
        Returns:
            IImageGenerator instance
            
        Raises:
            ProviderNotFoundError: If provider not found
        """
        # Initialize providers if not done
        if not cls._initialized:
            cls._initialize_providers()
        
        # Use config default if not specified
        if key is None:
            key = settings.image_generator_provider
        
        key = key.lower()
        factory = cls._registry.get(key)
        
        if not factory:
            valid_keys = ", ".join(cls._registry.keys())
            raise ProviderNotFoundError(
                f"Unknown image provider '{key}'. Available: {valid_keys}"
            )
        
        return factory(**kwargs)

    @classmethod
    def _initialize_providers(cls) -> None:
        """
        Initialize default providers.
        
        Called lazily to avoid circular imports during module loading.
        """
        if cls._initialized:
            return
        
        # Register mock provider
        def create_mock_generator(**kwargs) -> IImageGenerator:
            from app.infrastructure.mcp.image_client import MockMCPImageGenerator
            return MockMCPImageGenerator(**kwargs)
        
        cls.register("mock", create_mock_generator)
        
        # Register MCP provider
        def create_mcp_generator(**kwargs) -> IImageGenerator:
            from app.infrastructure.mcp import MCPImageGenerator, MCPHttpClient
            from app.infrastructure.storage import MinIOClient
            
            # Create MCP client
            mcp_client = MCPHttpClient(
                server_url=kwargs.get("server_url", settings.mcp_image_server_url),
                timeout=kwargs.get("timeout", settings.mcp_image_timeout),
            )
            
            # Create MinIO client with size limit
            minio_client = MinIOClient(
                endpoint=settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                bucket=settings.minio_bucket,
                secure=settings.minio_secure,
                max_size_bytes=settings.minio_max_size_mb * 1024 * 1024,
            )
            
            return MCPImageGenerator(
                mcp_client=mcp_client,
                minio_client=minio_client,
                model=kwargs.get("model", settings.mcp_image_model),
                allowed_domains=kwargs.get("allowed_domains", settings.mcp_allowed_domains_set),
            )
        
        cls.register("mcp", create_mcp_generator)
        
        cls._initialized = True
        logger.info("Image providers initialized")

    @classmethod
    def reset(cls) -> None:
        """Reset the factory (for testing purposes)."""
        cls._registry.clear()
        cls._initialized = False
