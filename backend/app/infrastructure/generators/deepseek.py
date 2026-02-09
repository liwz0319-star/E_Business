"""
DeepSeek API Generator Implementation.

Provides text generation using DeepSeek's API with support for
both synchronous and streaming responses.
"""
import logging
import os
from pathlib import Path
from typing import Any, AsyncIterator, Awaitable, Callable, Dict, Optional

from app.core.config import get_settings  # Import function instead of instance
from app.core.http_client import BaseHTTPClient
from app.domain.entities.generation import (
    GenerationRequest,
    GenerationResult,
    StreamChunk,
)
from app.domain.exceptions import HTTPClientError

logger = logging.getLogger(__name__)

# Type alias for streaming callback
StreamCallback = Callable[[StreamChunk], Awaitable[None]]

# Backward-compatible test hook:
# tests may patch `deepseek.settings`; production path uses get_settings().
settings = None


def _resolve_settings():
    """Return patched settings in tests, otherwise load runtime settings."""
    if settings is not None:
        return settings
    # FORCE REFRESH: bypass lru_cache if possible or just call it
    # Ideally we'd want to clear cache if key is missing, but for now let's just log
    s = get_settings()
    if not s.deepseek_api_key:
        logger.warning(f"Settings loaded in DeepSeekGenerator has NO API KEY. CWD: {os.getcwd()}")
    return s


def _candidate_env_files() -> list[Path]:
    """Build likely .env locations for runtime fallback loading."""
    backend_dir = Path(__file__).resolve().parents[3]
    project_dir = backend_dir.parent
    cwd = Path.cwd().resolve()
    return [
        backend_dir / ".env",
        project_dir / ".env",
        cwd / ".env",
        cwd / "backend" / ".env",
    ]


def _read_api_key_from_env_file(env_file: Path) -> Optional[str]:
    """Parse DEEPSEEK_API_KEY from a .env file without extra dependencies."""
    if not env_file.exists():
        return None
    try:
        for raw_line in env_file.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "DEEPSEEK_API_KEY":
                parsed = value.strip().strip("'\"")
                return parsed or None
    except OSError:
        return None
    return None


def _resolve_api_key(
    explicit_api_key: Optional[str],
    settings_obj: Any,
    allow_fallback: bool,
) -> Optional[str]:
    """Resolve API key from explicit arg/settings and optional runtime fallback.
    
    Priority order:
    1. Explicit parameter
    2. Direct environment variable (most reliable for async tasks)
    3. Settings object
    4. Fallback .env file parsing
    """
    # 1. Explicit parameter has highest priority
    if explicit_api_key:
        return explicit_api_key

    # 2. Direct environment variable - most reliable for async tasks
    env_key = os.getenv("DEEPSEEK_API_KEY")
    if env_key:
        return env_key

    # 3. Settings object
    settings_key = getattr(settings_obj, "deepseek_api_key", None)
    if settings_key:
        return settings_key

    # Keep unit-test behavior deterministic when settings is monkeypatched.
    if not allow_fallback:
        return None

    # 4. Fallback: parse .env files directly
    for env_file in _candidate_env_files():
        file_key = _read_api_key_from_env_file(env_file)
        if file_key:
            logger.warning(
                "DeepSeek API key recovered from fallback env path: %s",
                env_file,
            )
            return file_key

    return None


class DeepSeekGenerator:
    """
    DeepSeek API client for text generation.
    
    Implements the IGenerator protocol for AI content generation
    using DeepSeek's chat completion API.
    
    Features:
    - Synchronous generation via generate()
    - Streaming generation via generate_stream()
    - Reasoning content extraction from thinking tokens
    - Configurable model, temperature, and max_tokens
    
    Usage:
        async with DeepSeekGenerator(api_key="...") as generator:
            result = await generator.generate(request)
    """
    
    BASE_URL = "https://api.deepseek.com/v1"
    DEFAULT_MODEL = "deepseek-chat"
    DEFAULT_MAX_TOKENS = 2000
    DEFAULT_TIMEOUT = 120
    
    # Error message mapping for HTTP status codes
    ERROR_MAPPING = {
        400: "Invalid request",
        401: "Invalid API key",
        403: "Access forbidden",
        404: "Resource not found",
        429: "Rate limit exceeded",
        500: "DeepSeek server error",
        502: "Bad gateway",
        503: "DeepSeek service unavailable",
        504: "Gateway timeout",
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
        timeout: Optional[int] = None,
    ):
        """
        Initialize DeepSeek generator.

        Args:
            api_key: DeepSeek API key (defaults to settings.deepseek_api_key)
            model: Model name (defaults to settings.deepseek_model)
            max_tokens: Max tokens (defaults to settings.deepseek_max_tokens)
            timeout: Request timeout (defaults to settings.deepseek_timeout)
        """
        # Call get_settings() dynamically instead of using cached module globals.
        settings_obj = _resolve_settings()

        self.api_key = _resolve_api_key(
            explicit_api_key=api_key,
            settings_obj=settings_obj,
            allow_fallback=(settings is None),
        )
        self.model = model or settings_obj.deepseek_model or self.DEFAULT_MODEL
        self.max_tokens = max_tokens or settings_obj.deepseek_max_tokens or self.DEFAULT_MAX_TOKENS
        self.timeout = timeout or settings_obj.deepseek_timeout or self.DEFAULT_TIMEOUT

        if not self.api_key:
            logger.error(
                f"DeepSeek API key not found. "
                f"Settings has key: {bool(getattr(settings_obj, 'deepseek_api_key', None))}, "
                f"CWD: {Path.cwd()}"
            )
            raise ValueError("DeepSeek API key is required")

        logger.info("DeepSeekGenerator initialized with API key suffix: ***%s", self.api_key[-4:])

        self._client: Optional[BaseHTTPClient] = None
    
    async def __aenter__(self) -> "DeepSeekGenerator":
        """Initialize HTTP client context manager."""
        self._client = BaseHTTPClient(
            base_url=self.BASE_URL,
            timeout=self.timeout,
        )
        await self._client.__aenter__()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Cleanup resources."""
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)
            self._client = None
    
    def _build_payload(
        self,
        request: GenerationRequest,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """
        Build API request payload.
        
        Args:
            request: Generation request with prompt and parameters
            stream: Whether to enable streaming response
            
        Returns:
            Dict containing the API request payload
        """
        payload = {
            "model": request.model or self.model,
            "messages": [{"role": "user", "content": request.prompt}],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens or self.max_tokens,
            "stream": stream,
        }
        
        # Merge provider-specific config
        if request.provider_config:
            payload.update(request.provider_config)
        
        return payload
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    def _map_error(self, error: HTTPClientError) -> HTTPClientError:
        """
        Map HTTP errors to user-friendly error messages using ERROR_MAPPING.
        
        Args:
            error: Original HTTPClientError
            
        Returns:
            HTTPClientError with enhanced message if status code is known
        """
        error_str = str(error)
        for status_code, message in self.ERROR_MAPPING.items():
            if f"HTTP {status_code}" in error_str or f"status {status_code}" in error_str.lower():
                return HTTPClientError(f"DeepSeek API error: {message} (HTTP {status_code})")
        return error

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """
        Synchronous generation.
        
        Args:
            request: Generation request with prompt and parameters
            
        Returns:
            GenerationResult with generated content
            
        Raises:
            HTTPClientError: On API errors
            ValueError: If client not initialized
        """
        if not self._client:
            raise ValueError("Generator not initialized. Use 'async with' context manager.")
        
        payload = self._build_payload(request, stream=False)
        
        try:
            response = await self._client.request(
                "POST",
                "/chat/completions",
                headers=self._get_headers(),
                json=payload,
            )
            
            # Extract content from response
            content = response["choices"][0]["message"]["content"]
            usage = response.get("usage")
            
            return GenerationResult(
                content=content,
                raw_response=response,
                usage=usage,
            )
            
        except HTTPClientError as e:
            raise self._map_error(e) from e
        except Exception as e:
            logger.error(f"DeepSeek generate error: {e}")
            raise HTTPClientError(f"Generation failed: {e}") from e
    
    async def generate_stream(
        self,
        request: GenerationRequest,
    ) -> AsyncIterator[StreamChunk]:
        """
        Streaming generation with thinking tokens.

        Yields StreamChunk objects with separate content and reasoning_content
        fields for DeepSeek's reasoning process visibility.

        Args:
            request: Generation request with prompt and parameters

        Yields:
            StreamChunk with content and optional reasoning_content

        Raises:
            HTTPClientError: On API errors
            ValueError: If client not initialized
        """
        if not self._client:
            raise ValueError("Generator not initialized. Use 'async with' context manager.")

        payload = self._build_payload(request, stream=True)

        try:
            async for chunk in self._client.stream_sse(
                "POST",
                "/chat/completions",
                headers=self._get_headers(),
                json=payload,
            ):
                # Extract delta from choices
                choices = chunk.get("choices", [])
                if not choices:
                    continue

                delta = choices[0].get("delta", {})
                finish_reason = choices[0].get("finish_reason")

                # Extract content and reasoning_content
                content = delta.get("content", "")
                reasoning_content = delta.get("reasoning_content")

                # Yield chunk if there's any content
                if content or reasoning_content or finish_reason:
                    yield StreamChunk(
                        content=content,
                        reasoning_content=reasoning_content,
                        finish_reason=finish_reason,
                    )

        except HTTPClientError as e:
            raise self._map_error(e) from e
        except Exception as e:
            logger.error(f"DeepSeek stream error: {e}")
            raise HTTPClientError(f"Streaming failed: {e}") from e

    async def generate_stream_with_callback(
        self,
        request: GenerationRequest,
        callback: Optional[StreamCallback] = None,
    ) -> GenerationResult:
        """
        Stream generation with optional callback for real-time events.

        This method streams the generation and calls the provided callback
        with each chunk, allowing for real-time progress updates.

        Args:
            request: Generation request with prompt and parameters
            callback: Optional async callback function called with each StreamChunk

        Returns:
            GenerationResult with complete content (accumulated from stream)

        Raises:
            HTTPClientError: On API errors
            ValueError: If client not initialized
        """
        if not self._client:
            raise ValueError("Generator not initialized. Use 'async with' context manager.")

        payload = self._build_payload(request, stream=True)

        content_parts: list[str] = []
        reasoning_parts: list[str] = []

        try:
            async for chunk in self._client.stream_sse(
                "POST",
                "/chat/completions",
                headers=self._get_headers(),
                json=payload,
            ):
                # Extract delta from choices
                choices = chunk.get("choices", [])
                if not choices:
                    continue

                delta = choices[0].get("delta", {})
                finish_reason = choices[0].get("finish_reason")

                # Extract content and reasoning_content
                content = delta.get("content", "")
                reasoning_content = delta.get("reasoning_content")

                # Accumulate content
                if content:
                    content_parts.append(content)
                if reasoning_content:
                    reasoning_parts.append(reasoning_content)

                # Create StreamChunk and call callback if provided
                if content or reasoning_content or finish_reason:
                    stream_chunk = StreamChunk(
                        content=content,
                        reasoning_content=reasoning_content,
                        finish_reason=finish_reason,
                    )
                    if callback:
                        await callback(stream_chunk)

            # Combine accumulated content
            full_content = "".join(content_parts)
            full_reasoning = "".join(reasoning_parts) if reasoning_parts else None

            # Construct a mock response for GenerationResult
            response = {
                "choices": [
                    {
                        "message": {
                            "content": full_content,
                            "reasoning_content": full_reasoning,
                        },
                        "finish_reason": finish_reason,
                    }
                ],
            }

            return GenerationResult(
                content=full_content,
                raw_response=response,
            )

        except HTTPClientError as e:
            raise self._map_error(e) from e
        except Exception as e:
            logger.error(f"DeepSeek stream with callback error: {e}")
            raise HTTPClientError(f"Streaming with callback failed: {e}") from e
