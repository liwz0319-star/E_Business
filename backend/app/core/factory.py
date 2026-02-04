"""
Provider Factory Module.

Manages registration and instantiation of AI providers.
"""
import logging
from typing import Dict, Type

from app.domain.interfaces.generator import IGenerator
from app.domain.exceptions import ProviderNotFoundError

logger = logging.getLogger(__name__)


class ProviderFactory:
    """
    Factory for creating AI generator instances.
    """
    _registry: Dict[str, Type[IGenerator]] = {}

    @classmethod
    def register(cls, key: str, provider: Type[IGenerator]) -> None:
        """
        Register a provider class with a string key.
        """
        key = key.lower()
        if key in cls._registry:
            logger.warning(f"Overwriting provider registration for key: {key}")
        
        cls._registry[key] = provider
        logger.info(f"Registered provider: {key} -> {provider.__name__}")

    @classmethod
    def get_provider(cls, key: str, **kwargs) -> IGenerator:
        """
        Get an instance of a provider by key.
        """
        key = key.lower()
        provider_cls = cls._registry.get(key)
        
        if not provider_cls:
            valid_keys = ", ".join(cls._registry.keys())
            raise ProviderNotFoundError(
                f"Unknown provider '{key}'. Available: {valid_keys}"
            )
            
        return provider_cls(**kwargs)
