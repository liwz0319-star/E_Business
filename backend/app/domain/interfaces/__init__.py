"""
Domain interfaces module.

Contains abstract interfaces that define contracts for infrastructure implementations.
"""

from .generator import IGenerator
from .user_repository import IUserRepository
from .image_generator import IImageGenerator

__all__ = ["IUserRepository", "IGenerator", "IImageGenerator"]


