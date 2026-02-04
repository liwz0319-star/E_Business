# Story 2-1: DeepSeek Client Implementation

## Story Information

- **Story ID**: 2-1-deepseek-client-implementation
- **Epic**: Epic 2 - AI Provider Integration
- **Status**: done
- **Created**: 2025-01-22

## User Story

As a developer, I want to use the Generator interface to integrate DeepSeek API, so that the system can use that model to generate text.

## Acceptance Criteria

1. **Given** a valid DeepSeek API Key
2. **When** calling `DeepSeekGenerator.generate(prompt)`
3. **Then** return the API's text content as `GenerationResult`
4. **When** passing `stream=True`
5. **Then** yield `StreamChunk` objects with separate `content` and `reasoning_content` fields

## Technical Implementation

### DeepSeek API Specification

**Endpoint**: `https://api.deepseek.com/v1/chat/completions`

**Request Format**:
```json
{
  "model": "deepseek-chat",
  "messages": [{"role": "user", "content": "..."}],
  "temperature": 0.7,
  "max_tokens": 2000,
  "stream": false
}
```

**Streaming Response Format** (SSE):
```
data: {"choices":[{"delta":{"content":"..."},"finish_reason":null}]}

data: {"choices":[{"delta":{"content":"...","reasoning_content":"thinking..."},"finish_reason":"stop"}]}
data: [DONE]
```

**Parsing Requirements**:
1. Split lines by `data: ` prefix
2. Parse JSON (handle incomplete chunks gracefully)
3. Handle `[DONE]` sentinel
4. Separate `content` from `reasoning_content`
5. Detect `finish_reason`

**Key Feature**: DeepSeek supports reasoning process visibility (`reasoning_content`), requiring special handling in streaming responses.

### Implementation Structure

#### 1. DeepSeekGenerator Class

Location: `backend/app/infrastructure/generators/deepseek.py`

```python
class DeepSeekGenerator:
    """DeepSeek API client for text generation."""

    BASE_URL = "https://api.deepseek.com/v1"
    DEFAULT_MODEL = "deepseek-chat"
    DEFAULT_MAX_TOKENS = 2000

    async def __aenter__(self):
        """Initialize HTTP client context manager."""
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Cleanup resources."""
        ...

    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Synchronous generation."""
        ...

    async def generate_stream(self, request: GenerationRequest) -> AsyncIterator[StreamChunk]:
        """Streaming generation with thinking tokens."""
        ...

    def _build_payload(self, request: GenerationRequest, stream: bool = False) -> dict:
        """Build API request payload."""
        ...
```

#### 2. Configuration Updates

**backend/app/core/config.py**:
```python
deepseek_api_key: Optional[str] = Field(default=None, ...)
deepseek_model: str = Field(default="deepseek-chat", ...)
deepseek_max_tokens: int = Field(default=2000, ...)
deepseek_timeout: int = Field(default=120, ...)
```

**backend/.env.example**:
```bash
# DeepSeek Configuration
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_MAX_TOKENS=2000
DEEPSEEK_TIMEOUT=120
```

#### 3. ProviderFactory Registration

```python
# backend/app/main.py
from app.infrastructure.generators.deepseek import DeepSeekGenerator
from app.core.factory import ProviderFactory

ProviderFactory.register("deepseek", DeepSeekGenerator)
```

#### 0. BaseHTTPClient Extension (PREREQUISITE)

Location: `backend/app/core/http_client.py`

**Add SSE streaming support to maintain architectural consistency:**

```python
async def stream_sse(
    self,
    method: str,
    path: str,
    *,
    json: Any = None,
) -> AsyncIterator[Dict[str, Any]]:
    """Stream Server-Sent Events (SSE) responses.

    Yields parsed JSON objects from SSE stream.
    Handles [DONE] sentinel and JSON parsing errors.
    """
    if not self._session:
        await self.__aenter__()

    url = f"{self.base_url}/{path.lstrip('/')}" if self.base_url else path

    async with self._session.request(method, url, json=json) as response:
        response.raise_for_status()

        async for line in response.content:
            line_str = line.decode().strip()
            if not line_str or line_str == "data: [DONE]":
                break

            if line_str.startswith("data: "):
                try:
                    yield json.loads(line_str[6:])
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse SSE chunk: {e}")
```

### Architecture Compliance

| Specification | Requirement | Implementation |
|---------------|-------------|----------------|
| Clean Architecture | Infrastructure layer implements Domain interfaces | DeepSeekGenerator implements IGenerator |
| Domain Purity | Domain layer has no HTTP dependencies | Only Infrastructure uses http_client |
| Unified HTTP Client | All generators use BaseHTTPClient | Uses BaseHTTPClient |
| Abstract Factory | Get instances via string key | Registered to ProviderFactory |
| Async/Await | All I/O operations async | Uses async/await |
| Naming | Python code snake_case | Compliant |

### Error Handling Strategy

Map HTTP status codes to domain exceptions:

| HTTP Status | Error Type | Exception | Retryable |
|-------------|------------|-----------|-----------|
| 401 | Invalid API Key | `HTTPClientError` | No |
| 400 | Invalid Request | `HTTPClientError` | No |
| 429 | Rate Limit | `HTTPClientError` | Yes |
| 500 | Server Error | `HTTPClientError` | Yes |
| 503 | Service Unavailable | `HTTPClientError` | Yes |

**Implementation**:
```python
ERROR_MAPPING = {
    401: "Invalid API key",
    400: "Invalid request",
    429: "Rate limit exceeded",
    500: "DeepSeek server error",
    503: "DeepSeek service unavailable",
}

async def _handle_response(self, response):
    """Handle API response with proper error mapping."""
    if response.status not in (200, 201):
        message = self.ERROR_MAPPING.get(response.status, "Unknown error")
        raise HTTPClientError(f"{message} (HTTP {response.status})")
    return response
```

### Dependencies

- `aiohttp` (from Story 1.3)
- `pydantic>=2.0`
- `pytest-asyncio` (for testing)

### Key Dependencies

- `backend/app/domain/interfaces/generator.py` - IGenerator interface
- `backend/app/domain/entities/generation.py` - GenerationRequest/Result entities
- `backend/app/core/http_client.py` - BaseHTTPClient
- `backend/app/core/factory.py` - ProviderFactory
- `backend/app/core/config.py` - Settings
- `backend/app/domain/exceptions.py` - Exception types

## Testing Strategy

### Unit Tests Coverage

File: `backend/tests/test_deepseek_generator.py`

1. Test synchronous `generate()` method
2. Test streaming `generate_stream()` method
3. Test API error handling (401, 429, 500, etc.)
4. Test payload building logic
5. Test reasoning content separation in `StreamChunk`
6. Test context manager behavior
7. Test timeout behavior
8. Test retry logic on 500 errors
9. Test stream interruption handling
10. Test `provider_config` override
11. Test default values application

### Integration Tests

1. Test ProviderFactory registration
2. Test configuration injection
3. Test factory case-insensitive key lookup

### Mock Strategy

Use `pytest-asyncio` and mock HTTP responses:
```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_deepseek_generate():
    async with DeepSeekGenerator(api_key="test-key") as generator:
        # Mock HTTP response
        ...
```

## Verification Steps

1. **Configuration Verification**: Ensure `DEEPSEEK_API_KEY` environment variable is configurable
2. **Interface Verification**: DeepSeekGenerator conforms to IGenerator protocol
3. **Unit Tests**: Run `pytest tests/test_deepseek_generator.py`
4. **Integration Test**: Verify ProviderFactory integration
5. **Manual Test**: Test basic generation with real API key

## Files to Create/Modify

### Create
- `backend/app/infrastructure/generators/__init__.py`
- `backend/app/infrastructure/generators/deepseek.py`
- `backend/tests/test_deepseek_generator.py`

### Modify
- `backend/app/domain/entities/generation.py` - Add `reasoning_content` to `StreamChunk`
- `backend/app/core/http_client.py` - Add `stream_sse()` method
- `backend/app/core/config.py` - Add DeepSeek configuration fields
- `backend/.env.example` - Add DeepSeek environment variables
- `backend/app/infrastructure/__init__.py` - Add exports
- `backend/app/main.py` - Register provider factory

## Notes

- DeepSeek's `reasoning_content` field contains the model's thinking process
- `BaseHTTPClient` will be extended with `stream_sse()` method for SSE support
- Error handling must distinguish between retryable (429, 5xx) and non-retryable errors
- `StreamChunk.reasoning_content` is added to support DeepSeek's reasoning tokens
- HTTP session is created per instance (context manager pattern) and reused across requests

---

## Dev Agent Record

### Implementation Date
2026-01-23

### Files Created
- `backend/app/infrastructure/generators/__init__.py`
- `backend/app/infrastructure/generators/deepseek.py`
- `backend/tests/test_deepseek_generator.py`

### Files Modified
- `backend/app/domain/entities/generation.py` - Added `reasoning_content` to `StreamChunk`
- `backend/app/domain/interfaces/generator.py` - Updated `generate_stream` return type to `AsyncIterator[StreamChunk]`
- `backend/app/core/http_client.py` - Added `stream_sse()` method
- `backend/app/core/config.py` - Added DeepSeek configuration fields
- `backend/.env.example` - Added DeepSeek environment variables
- `backend/app/main.py` - Registered DeepSeek provider factory

### Change Log
- Implemented DeepSeekGenerator class with sync/stream generation
- Added `_map_error()` method to utilize ERROR_MAPPING for user-friendly error messages
- Added SSE streaming support to BaseHTTPClient
- Added `reasoning_content` field to StreamChunk entity
- Registered DeepSeek provider in ProviderFactory
- Created comprehensive unit tests

### Code Review Fixes Applied
- Fixed `IGenerator.generate_stream()` return type inconsistency
- Implemented ERROR_MAPPING usage via `_map_error()` method
- Verified generators module exports
