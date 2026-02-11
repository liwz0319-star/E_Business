"""
Debug routes for testing configuration loading.
"""
import os
from fastapi import APIRouter
from app.core.config import get_settings
from app.core.langchain_init import get_langsmith_config

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


@router.get("/langsmith")
async def check_langsmith_config():
    """
    检查 LangSmith 配置状态。

    Returns:
        LangSmith 配置信息，包括是否启用、项目名称、API key 状态等
    """
    return get_langsmith_config()


@router.get("/langsmith/env")
async def check_langsmith_env():
    """
    检查 LangSmith 相关的环境变量。

    用于调试环境变量是否正确设置。
    """
    return {
        "LANGCHAIN_TRACING_V2": os.getenv("LANGCHAIN_TRACING_V2", "not set"),
        "LANGCHAIN_API_KEY": "configured" if os.getenv("LANGCHAIN_API_KEY") else "not set",
        "LANGCHAIN_PROJECT": os.getenv("LANGCHAIN_PROJECT", "not set"),
        "LANGCHAIN_ENDPOINT": os.getenv("LANGCHAIN_ENDPOINT", "not set"),
        "LANGCHAIN_SESSION_SAMPLING_RATE": os.getenv("LANGCHAIN_SESSION_SAMPLING_RATE", "not set"),
    }
