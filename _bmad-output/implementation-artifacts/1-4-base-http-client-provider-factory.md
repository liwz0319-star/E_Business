# Story 1.4: BaseHTTPClient & Provider Factory

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want a unified HTTP client and factory for generators,
so that I can easily add new AI providers without duplicating network logic.

## Acceptance Criteria

1. **Given** the `app/core/http_client.py` module
   **When** I use `BaseHTTPClient` to make a request
   **Then** it automatically handles retries (3 times) and timeouts
   **And** uses exponential backoff between retry attempts

2. **Given** the `ProviderFactory` is configured
   **When** I request a generator using a string key (e.g., "deepseek")
   **Then** it returns the correct generator class instance
   **And** the factory supports dynamic provider registration

3. **Given** the Domain layer
   **When** I inspect the interfaces
   **Then** `IGenerator` protocol is defined in `app/domain/interfaces/generator.py`
   **And** it specifies `async def generate(request: GenerationRequest) -> GenerationResult`
   **And** it specifies `async def generate_stream(request: GenerationRequest) -> AsyncIterator[str]`

4. **Given** the BaseHTTPClient
   **When** max retries are exceeded
   **Then** it raises `MaxRetriesExceededError` with original exception chained

## Tasks / Subtasks

- [ ] Create Domain Interface for Generators (AC: 3)
  - [ ] Create `backend/app/domain/interfaces/` directory
  - [ ] Create `backend/app/domain/interfaces/__init__.py`
  - [ ] Create `backend/app/domain/interfaces/generator.py` with `IGenerator` protocol

- [ ] Implement BaseHTTPClient (AC: 1)
  - [ ] Create `backend/app/core/http_client.py`
  - [ ] Implement `BaseHTTPClient` class with async context manager support
  - [ ] Add retry logic (3 attempts with exponential backoff)
  - [ ] Add timeout configuration (default: 30 seconds)
  - [ ] Add structured logging for requests and retries
  - [ ] Handle HTTP errors with proper exception types

- [ ] Implement ProviderFactory (AC: 2)
  - [ ] Create `backend/app/core/factory.py`
  - [ ] Implement `ProviderFactory` class with registry pattern
  - [ ] Add `register_provider()` method for dynamic registration
  - [ ] Add `get_provider()` method that accepts string keys
  - [ ] Add validation for registered provider types
  - [ ] Raise descriptive exceptions for unknown providers

- [ ] Create HTTP Client Configuration (AC: 1)
  - [ ] Add timeout settings to `app/core/config.py`
  - [ ] Add retry count settings to config
  - [ ] Add backoff factor settings to config
  - [ ] Support per-provider timeout overrides
  - [ ] Add environment variable documentation to `.env.example` (HTTP_TIMEOUT_CONNECT, HTTP_TIMEOUT_READ, HTTP_MAX_RETRIES, HTTP_BACKOFF_BASE)

- [ ] Create Exception Hierarchy (AC: 1)
  - [ ] Create `backend/app/domain/exceptions.py`
  - [ ] Define `HTTPClientError` base exception
  - [ ] Define `MaxRetriesExceededError` for retry failures
  - [ ] Define `ProviderNotFoundError` for factory lookup failures
  - [ ] Define `TimeoutError` for request timeouts

- [ ] Unit Tests for BaseHTTPClient (AC: 1)
  - [ ] Test successful HTTP request
  - [ ] Test retry on transient failures (status: 408, 429, 500, 502, 503, 504)
  - [ ] Test timeout handling
  - [ ] Test exponential backoff timing
  - [ ] Test logging of retry attempts
  - [ ] Test exception propagation on max retries (AC: 4)

- [ ] Unit Tests for ProviderFactory (AC: 2, 3)
  - [ ] Test provider registration
  - [ ] Test provider retrieval by string key
  - [ ] Test `ProviderNotFoundError` for unknown keys
  - [ ] Test duplicate registration handling
  - [ ] Test IGenerator interface compliance

- [ ] Integration Tests (AC: 1, 2, 3)
  - [ ] Test full flow: factory → provider → http_client → request
  - [ ] Test with mock HTTP server simulating provider API
  - [ ] Test concurrent provider instantiations

## Dev Notes

### Architecture Compliance

- **Pragmatic Clean Architecture**:
  - `domain/interfaces/generator.py`: Protocol definition for all generators
  - `core/http_client.py`: Shared HTTP infrastructure (cross-cutting concern)
  - `core/factory.py`: Provider instantiation logic

- **Domain Layer Purity** (from architecture.md Party Mode refinement #1):
  - `IGenerator` MUST be a Python `Protocol` or Abstract Base Class
  - Domain interfaces MUST NOT depend on httpx/aiohttp or any HTTP library
  - Domain entities MUST use pure Python `dataclasses`

- **Unified HTTP Client** (from architecture.md Party Mode refinement #2):
  - All generator adapters MUST use `BaseHTTPClient` for external API calls
  - Centralized retry/timeout logic prevents code duplication
  - Enables consistent error handling across all providers

### Technical Requirements

**HTTP Client Specifications:**
- **Library**: `aiohttp.ClientSession` (consistent with Story 1.3 Socket.io implementation)
  - Async-only to match FastAPI architecture
  - Already installed as dependency from Story 1.3
- **Retry Strategy**:
  - Maximum retries: 3 (configurable)
  - Backoff: Exponential (2^n seconds: 1s, 2s, 4s)
  - Retryable status codes: 408, 429, 500, 502, 503, 504
- **Timeout Defaults**:
  - Connect timeout: 5 seconds
  - Read timeout: 30 seconds
  - Total timeout: 60 seconds

**Provider Factory Design:**
```python
# Factory pattern with registry
class ProviderFactory:
    _providers: Dict[str, Type[IGenerator]] = {}

    @classmethod
    def register(cls, key: str, provider_class: Type[IGenerator]) -> None
    @classmethod
    def get_provider(cls, key: str, **kwargs) -> IGenerator
```

**IGenerator Interface** (Domain Layer):
```python
from typing import AsyncIterator, Protocol

# NOTE: GenerationResult and GenerationRequest entities will be created
# in future stories (DeepSeek provider implementation). For this story,
# use placeholder imports or define stub types for interface compliance.
from app.domain.entities import GenerationResult, GenerationRequest

class IGenerator(Protocol):
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Synchronous generation"""
        ...

    async def generate_stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        """Streaming generation for real-time responses"""
        ...
```

### Project Structure Notes

- **New Directory**: `backend/app/domain/interfaces/` (first domain layer directory)
- **Clean Alignment**: `http_client.py` and `factory.py` in `core/` as cross-cutting utilities
- **Dependency Flow**: Infrastructure → Domain (generators implement IGenerator), Factory → Domain (creates IGenerator instances)

### Previous Story Intelligence

**From Story 1.3 (Socket.io):**
- Async/await patterns are established throughout the codebase
- Use `structured logging` pattern from Story 1.1
- Environment-based configuration in `app/core/config.py`

**From Story 1.2 (Database & Auth):**
- Use `pydantic` for all configuration validation
- Follow `snake_case` for Python code, `camelCase` for API responses

**From Story 1.1 (Project Initialization):**
- All new code MUST be testable with pytest
- Use `asyncio` for all I/O operations
- Docker environment variables in `.env.example`

### Code Patterns to Follow

**Async Context Manager for HTTP Client:**
```python
import aiohttp
from typing import Optional

class BaseHTTPClient:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
```

**Retry Decorator Pattern:**
```python
def retry(max_attempts: int = 3, backoff_base: float = 1.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except RetryableError as e:
                    if attempt == max_attempts - 1:
                        raise MaxRetriesExceededError() from e
                    await asyncio.sleep(backoff_base * (2 ** attempt))
```

**Factory Registry Pattern:**
```python
class ProviderFactory:
    _registry: Dict[str, Type[IGenerator]] = {}

    @classmethod
    def register(cls, key: str, provider: Type[IGenerator]) -> None:
        if key in cls._registry:
            raise ValueError(f"Provider {key} already registered")
        cls._registry[key] = provider

    @classmethod
    def create(cls, key: str, **config) -> IGenerator:
        if key not in cls._registry:
            raise ProviderNotFoundError(f"Unknown provider: {key}")
        return cls._registry[key](**config)
```

### Testing Requirements

**Unit Test Coverage:**
- `BaseHTTPClient`: 90%+ coverage
- `ProviderFactory`: 100% coverage (critical infrastructure)
- `IGenerator`: Interface compliance tests

**Test Doubles:**
- Use `aiohttp test utils` or `pytest-aiohttp` for HTTP mocking
- Create fake generator implementations for factory tests

**Integration Test Requirements:**
- Mock external APIs (DeepSeek, Gemini, etc.)
- Test retry behavior with simulated failures
- Test concurrent provider usage

### Configuration Requirements

Add to `app/core/config.py`:
```python
class HTTPClientConfig(BaseSettings):
    model_config = ConfigDict(env_prefix="HTTP_")

    timeout_connect: int = 5
    timeout_read: int = 30
    timeout_total: int = 60
    max_retries: int = 3
    retry_backoff_base: float = 1.0
```

### References

- [Epic 1 Story 1.4](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/epics.md#Story-1.4:-BaseHTTPClient-&-Provider-Factory)
- [Architecture - Multi-Provider Strategy](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md#Multi-Provider-Strategy)
- [Architecture - Party Mode Refinements](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md#Implemented-Refinements-(Party-Mode))
- [Story 1.3 - Socket.io](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/1-3-socket-io-server-security.md)
- [Story 1.2 - Database & Auth](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/1-2-database-auth-setup.md)
- [Story 1.1 - Project Initialization](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/1-1-backend-project-initialization.md)

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (glm-4.7)

### Debug Log References

None

### Completion Notes List

- Story document created with comprehensive developer context
- Architecture compliance verified against Party Mode refinements
- Code patterns inherited from Stories 1-1, 1-2, 1-3
- Domain layer purity requirements enforced
- Ready for development assignment

### File List

**To Create:**
- `backend/app/domain/interfaces/__init__.py`
- `backend/app/domain/interfaces/generator.py` (IGenerator protocol)
- `backend/app/domain/exceptions.py` (Domain exception hierarchy)
- `backend/app/core/http_client.py` (BaseHTTPClient)
- `backend/app/core/factory.py` (ProviderFactory)

**To Modify:**
- `backend/app/core/config.py` (Add HTTP client settings)
