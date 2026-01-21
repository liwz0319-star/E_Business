"""
Dependencies module.

Contains FastAPI dependency injection utilities.
"""

from .auth import get_current_active_user, get_current_user

__all__ = ["get_current_active_user", "get_current_user"]
