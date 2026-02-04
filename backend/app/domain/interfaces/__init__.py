"""
Domain interfaces module.

Contains abstract interfaces that define contracts for infrastructure implementations.
"""

from .generator import IGenerator
from .user_repository import IUserRepository

__all__ = ["IUserRepository", "IGenerator"]

