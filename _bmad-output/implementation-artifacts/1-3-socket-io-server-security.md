# Story 1.3: Socket.io Server & Security

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want to establish a secure Socket.io connection,
so that I can stream real-time events to the frontend.

## Acceptance Criteria

1. **Given** a running API server
   **When** a client connects to `/ws` with a valid JWT in the handshake auth
   **Then** the connection is accepted and the socket ID is logged

2. **Given** a running API server
   **When** a client connects to `/ws` without a token
   **Then** the connection is rejected (401)

3. **And** the server supports CORS for the frontend domain

## Tasks / Subtasks

- [x] Create Socket.io Directory Structure (AC: 1, 2, 3)
  - [x] Create `backend/app/interface/ws/` directory
  - [x] Create `backend/app/interface/ws/__init__.py`
  - [x] Create `backend/app/interface/ws/socket_manager.py` for Socket.io manager

- [x] Install Socket.io Dependencies (AC: 1, 2, 3)
  - [x] Add `python-socketio[asyncio]` to `backend/pyproject.toml`
  - [x] Add `aiohttp` to `backend/pyproject.toml` (Required for async client/server stability)
  - [x] Run `poetry lock` and `poetry install` (or rebuild Docker)

- [x] Create Socket.io Manager (AC: 1)
  - [x] Create `SocketManager` class in `socket_manager.py`
  - [x] Initialize Async Socket.io server with `/ws` path
  - [x] Configure CORS with origins from environment variable
  - [x] Implement event emission methods (agent:thought, agent:tool_call, agent:result, agent:error)

- [x] Implement JWT Authentication Middleware (AC: 1, 2)
  - [x] Create connection handler that validates JWT from handshake auth
  - [x] Reuse `get_current_user` dependency logic from Story 1-2
  - [x] Return 401 error for invalid/missing tokens
  - [x] Log successful connections with socket ID and user ID

- [x] Define Event Payload Structures (AC: 1)
  - [x] Create Pydantic models for event payloads in `app/interface/ws/schemas.py`
  - [x] Define `AgentThoughtEvent`, `AgentToolCallEvent`, `AgentResultEvent`, `AgentErrorEvent`
  - [x] Include fields: type, workflowId, data, timestamp

- [x] Integrate Socket.io with FastAPI (AC: 1, 2, 3)
  - [x] Mount Socket.io server to FastAPI app in `main.py`
  - [x] Ensure Socket.io uses the same ASGI app as FastAPI
  - [x] Configure async mode for Socket.io

- [x] Implement CORS Configuration (AC: 3)
  - [x] Read `CORS_ORIGINS` from environment variable (default: http://localhost:3000,http://localhost:8000)
  - [x] Configure Socket.io CORS with allowed origins
  - [x] Enable credentials support

- [x] Add Logging (AC: 1)
  - [x] Log connection events (connect/disconnect)
  - [x] Log authentication failures
  - [x] Log socket IDs for debugging

- [x] Unit Tests (AC: 1, 2, 3)
  - [x] Test Socket.io manager initialization
  - [x] Test JWT authentication on connection (mocked)
  - [x] Test connection rejection without valid token (mocked)
  - [x] Test event emission methods

- [x] Integration Tests (AC: 1, 2, 3)
  - [x] Test end-to-end Socket.io connection with valid JWT
  - [x] Test connection rejection with invalid/missing token
  - [x] Test CORS headers on connection

## Dev Notes


- **Architecture Compliance**:
  - Follow **Pragmatic Clean Architecture**:
    - `interface/ws/`: Socket.io event handlers and manager
    - Domain layer defines event payload interfaces (entities)
    - Infrastructure layer provides Socket.io implementation
  - **Socket.io Protocol** (from architecture.md):
    - Use `python-socketio` (asyncio mode)
    - **PROHIBITED**: Raw `websockets` library
    - Connection path: `/ws`
    - Must integrate with existing FastAPI ASGI application

- **Socket.io Event Names** (from architecture.md):
  - `agent:thought`: Intermediate reasoning steps from DeepSeek
  - `agent:tool_call`: When agent invokes a tool (e.g., "Generating Image...")
  - `agent:result`: Final output payload
  - `agent:error`: Error details

- **Event Payload Structure** (from architecture.md):
  ```json
  {
    "type": "thought",
    "workflowId": "uuid",
    "data": { "content": "..." },
    "timestamp": "ISO8601"
  }
  ```

- **JWT Authentication Integration** (from Story 1-2):
  - Reuse existing `get_current_user` dependency logic from `app/core/security.py`
  - Token algorithm: HS256
  - Handshake auth must contain valid JWT in `auth` parameter
  - Authentication failure returns 401
  - Decode token using existing `decode_token()` function

- **CORS Configuration** (from Story 1-1):
  - Default origins: `http://localhost:3000,http://localhost:8000`
  - Environment variable: `CORS_ORIGINS` (comma-separated)
  - Allow credentials: true
  - Allow all methods and headers

- **Code Patterns from Previous Stories**:
  - Use snake_case for files and functions (Story 1-1, 1-2)
  - Use PascalCase for class names (Story 1-1, 1-2)
  - Use Pydantic models for data validation (Story 1-1, 1-2)
  - Use structured logging (Story 1-1)
  - Async/await patterns for all I/O operations (Story 1-1, 1-2)

- **Dependencies** (from Story 1-1):
  - `python-socketio[asyncio]` - Already in pyproject.toml
  - `aiohttp` - Required for async Socket.io client
  - `fastapi` - For ASGI integration
  - `pydantic` - For event payload validation

- **Project Structure**:
  ```
  backend/app/
  ├── interface/
  │   └── ws/
  │       ├── __init__.py
  │       ├── socket_manager.py    # SocketIO manager class
  │       └── schemas.py            # Event payload Pydantic models
  ├── core/
  │   └── security.py              # JWT functions (reuse from Story 1-2)
  └── main.py                      # FastAPI app (mount Socket.io here)
  ```

- **Technical Constraints**:
  - Python 3.11+
  - FastAPI ASGI application
  - SQLAlchemy (async) for any DB operations
  - PostgreSQL + pgvector (from Story 1-1)

### Project Structure Notes

- **Clean Alignment**: The `interface/ws/` directory follows the Pragmatic Clean Architecture defined in Story 1-1
- **Integration Point**: Socket.io must be mounted to the same ASGI app as FastAPI in `main.py`
- **Security Layer**: JWT authentication logic is centralized in `app/core/security.py` (from Story 1-2)

### References

- [Epic 1 Story 1.3](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/epics.md#Story-1.3:-Socket.io-Server-&-Security)
- [Architecture - Socket.io Protocol](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md#Communication-Patterns)
- [Architecture - Project Structure](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md#Complete-Project-Directory-Structure)
- [Story 1.1 - Backend Initialization](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/1-1-backend-project-initialization.md)
- [Story 1.2 - Database & Auth](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/1-2-database-auth-setup.md)
