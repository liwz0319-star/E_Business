"""
Routes module.

Contains FastAPI router definitions.
"""

from .auth import router as auth_router

__all__ = ["auth_router"]
