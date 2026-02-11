"""
LangSmith 初始化模块

配置 LangSmith 用于追踪和监控 LangChain/LangGraph 应用。
"""
import logging
import os
from typing import Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def init_langsmith(
    api_key: Optional[str] = None,
    project_name: Optional[str] = None,
    endpoint: Optional[str] = None,
) -> bool:
    """
    初始化 LangSmith 追踪。

    Args:
        api_key: LangSmith API 密钥（如果为 None，从环境变量读取）
        project_name: 项目名称（如果为 None，从配置读取）
        endpoint: API 端点（如果为 None，从配置读取）

    Returns:
        bool: 是否成功初始化
    """
    try:
        settings = get_settings()

        # 检查是否启用追踪
        if not settings.langchain_tracing_v2:
            logger.info("LangSmith 追踪未启用")
            return False

        # 获取 API key
        langchain_api_key = api_key or settings.langchain_api_key or os.getenv("LANGCHAIN_API_KEY")
        if not langchain_api_key:
            logger.warning(
                "LangSmith 追踪已启用，但未提供 API key。"
                "请设置 LANGCHAIN_API_KEY 环境变量或 langchain_api_key 配置"
            )
            return False

        # 设置环境变量（LangChain 自动读取）
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = project_name or settings.langchain_project
        os.environ["LANGCHAIN_ENDPOINT"] = endpoint or settings.langchain_endpoint

        # 可选：设置会话采样率（100% 表示追踪所有会话）
        # os.environ["LANGCHAIN_SESSION_SAMPLING_RATE"] = "1.0"

        logger.info(
            f"LangSmith 初始化成功 - 项目: {os.environ['LANGCHAIN_PROJECT']}, "
            f"端点: {os.environ['LANGCHAIN_ENDPOINT']}"
        )
        return True

    except Exception as e:
        logger.error(f"LangSmith 初始化失败: {e}")
        return False


def get_langsmith_config() -> dict:
    """
    获取当前 LangSmith 配置信息。

    Returns:
        dict: 配置信息字典
    """
    settings = get_settings()
    return {
        "enabled": settings.langchain_tracing_v2,
        "project": settings.langchain_project,
        "endpoint": settings.langchain_endpoint,
        "api_key_configured": bool(settings.langchain_api_key or os.getenv("LANGCHAIN_API_KEY")),
        "tracing_env_var": os.getenv("LANGCHAIN_TRACING_V2", "false"),
    }


def enable_langsmith_tracing() -> None:
    """
    在运行时启用 LangSmith 追踪。

    如果您想动态启用追踪而不重启应用，可以调用此函数。
    """
    os.environ["LANGCHAIN_TRACING_V2"] = "true"
    logger.info("LangSmith 追踪已在运行时启用")


def disable_langsmith_tracing() -> None:
    """
    在运行时禁用 LangSmith 追踪。

    如果您想动态禁用追踪，可以调用此函数。
    """
    os.environ["LANGCHAIN_TRACING_V2"] = "false"
    logger.info("LangSmith 追踪已在运行时禁用")
