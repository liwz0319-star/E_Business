"""
Debug routes for testing configuration loading.
"""
from fastapi import APIRouter
from app.core.config import get_settings

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/settings-test")
async def test_settings():
    """Test if get_settings() returns API key."""
    settings = get_settings()
    return {
        "has_api_key": bool(settings.deepseek_api_key),
        "api_key_preview": settings.deepseek_api_key[:8] + "..." + settings.deepseek_api_key[-4:] if settings.deepseek_api_key else None,
        "model": settings.deepseek_model,
        "timestamp": "test-endpoint-works"
    }
