"""
Base HTTP Client Module.

Provides a wrapper around aiohttp with retry logic and standard error handling.
"""
import asyncio
import json as json_module
import logging
import socket
from typing import Any, AsyncIterator, Dict, Optional, TypeVar

import aiohttp
from aiohttp import ClientTimeout

from app.domain.exceptions import (
    HTTPClientError,
    MaxRetriesExceededError,
    TimeoutError
)

logger = logging.getLogger(__name__)

T = TypeVar("T")

# Default settings (since config might be missing them)
DEFAULT_CONNECT_TIMEOUT = 5
DEFAULT_READ_TIMEOUT = 30
DEFAULT_TOTAL_TIMEOUT = 60
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE = 1.0


class BaseHTTPClient:
    """
    Base HTTP client with retry logic and timeout handling.
    """
    
    def __init__(
        self,
        base_url: str = "",
        timeout: int = DEFAULT_TOTAL_TIMEOUT,
        retries: int = DEFAULT_MAX_RETRIES,
        backoff: float = DEFAULT_BACKOFF_BASE,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def __aenter__(self):
        timeout = ClientTimeout(total=self.timeout, connect=DEFAULT_CONNECT_TIMEOUT)
        self._session = aiohttp.ClientSession(
            timeout=timeout,
            headers={"Content-Type": "application/json"}
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
            
    async def request(
        self,
        method: str,
        path: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        json: Any = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Execute HTTP request with retries.
        """
        if not self._session:
            # Auto-initialize if not used as context manager (fallback)
            self._session = aiohttp.ClientSession(
                timeout=ClientTimeout(total=self.timeout)
            )

        url = f"{self.base_url}/{path.lstrip('/')}" if self.base_url else path
        
        for attempt in range(self.retries):
            try:
                async with self._session.request(
                    method,
                    url,
                    headers=headers,
                    json=json,
                    params=params,
                    **kwargs
                ) as response:
                    # Handle 4xx/5xx errors
                    try:
                        response.raise_for_status()
                    except aiohttp.ClientResponseError as e:
                        if e.status in (408, 429, 500, 502, 503, 504):
                             # Retryable errors
                             raise  # caught below
                        # Non-retryable
                        raise HTTPClientError(f"HTTP {e.status}: {e.message}") from e
                        
                    # Success
                    if response.content_type == "application/json":
                        return await response.json()
                    return {"text": await response.text()}
                    
            except (aiohttp.ClientError, asyncio.TimeoutError, socket.gaierror) as e:
                is_last_attempt = attempt == self.retries - 1
                
                log_level = logging.ERROR if is_last_attempt else logging.WARNING
                logger.log(
                    log_level,
                    f"Request failed ({method} {url}) attempt {attempt+1}/{self.retries}: {str(e)}"
                )
                
                if is_last_attempt:
                    if isinstance(e, asyncio.TimeoutError):
                        raise TimeoutError(f"Request timed out: {url}") from e
                    raise MaxRetriesExceededError(f"Max retries exceeded for {url}") from e
                
                # Backoff
                delay = self.backoff * (2 ** attempt)
                await asyncio.sleep(delay)
                
        raise MaxRetriesExceededError(f"Max retries exceeded for {url}")

    async def stream_sse(
        self,
        method: str,
        path: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        json: Any = None,
    ) -> AsyncIterator[Dict[str, Any]]:
        """
        Stream Server-Sent Events (SSE) responses.

        Yields parsed JSON objects from SSE stream.
        Handles [DONE] sentinel and JSON parsing errors.

        Args:
            method: HTTP method (usually POST)
            path: API endpoint path
            headers: Optional request headers
            json: Optional JSON body

        Yields:
            Dict[str, Any]: Parsed JSON objects from SSE data lines
        """
        if not self._session:
            # Auto-initialize if not used as context manager
            self._session = aiohttp.ClientSession(
                timeout=ClientTimeout(total=self.timeout)
            )

        url = f"{self.base_url}/{path.lstrip('/')}" if self.base_url else path

        async with self._session.request(
            method,
            url,
            headers=headers,
            json=json,
        ) as response:
            try:
                response.raise_for_status()
            except aiohttp.ClientResponseError as e:
                raise HTTPClientError(f"HTTP {e.status}: {e.message}") from e

            async for line in response.content:
                line_str = line.decode().strip()

                # Skip empty lines
                if not line_str:
                    continue

                # Stop on [DONE] sentinel
                if line_str == "data: [DONE]":
                    break

                # Parse SSE data lines
                if line_str.startswith("data: "):
                    json_str = line_str[6:]  # Remove "data: " prefix
                    try:
                        yield json_module.loads(json_str)
                    except json_module.JSONDecodeError as e:
                        logger.warning(f"Failed to parse SSE chunk: {e}")
                        continue


def with_retry(max_attempts: int = 3, backoff: float = 1.0):
    """Decorator for retrying async functions."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == max_attempts - 1:
                        raise
                    await asyncio.sleep(backoff * (2 ** attempt))
            if last_exception:
                raise last_exception
        return wrapper
    return decorator
