"""
Routes module.

Contains FastAPI router definitions.
"""

from .auth import router as auth_router
from .copywriting import router as copywriting_router
from .images import router as images_router
from .product_packages import router as product_packages_router
from .assets import router as assets_router
from .insights import router as insights_router
from .user_settings import router as user_settings_router

__all__ = [
    "auth_router",
    "copywriting_router",
    "images_router",
    "product_packages_router",
    "assets_router",
    "insights_router",
    "user_settings_router",
]

