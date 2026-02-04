"""
Routes module.

Contains FastAPI router definitions.
"""

from .auth import router as auth_router
from .copywriting import router as copywriting_router

__all__ = ["auth_router", "copywriting_router"]
