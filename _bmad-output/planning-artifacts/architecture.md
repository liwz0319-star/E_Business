---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7]
inputDocuments: ['f:/AAA Work\AIproject\E_Business\业务流程图.md', 'f:/AAA Work\AIproject\E_Business\_bmad-output\project-documentation\project-overview.md', 'f:/AAA Work\AIproject\E_Business\_bmad-output\project-documentation\api-contracts.md']
workflowType: 'architecture'
project_name: 'E_Business'
user_name: 'lwz'
date: '2026-01-21'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**
1.  **Knowledge-Enhanced Generation (RAG)**:
    *   System must maintain a "Best Practices" knowledge base.
    *   Deep Agents must retrieve relevant cases/rules from the knowledge base before generating copy/prompts.
2.  **Product Copy Generation (Text)**:
    *   Use **DeepSeek** model.
    *   Must expose complete Thinking/Planning process to the frontend.
3.  **Multimodal Generation (via MCP)**:
    *   Product Images and Ad Videos generation.
    *   Capabilities encapsulated via **MCP Server** (decoupling specific model providers).
4.  **Real-time Interaction**:
    *   Frontend must display Agent's thinking process in real-time (Streaming).

**Non-Functional Requirements:**
1.  **RAG Latency**: Retrieval must not significantly impact generation latency.
2.  **Modularity**: Decouple Logic (DeepSeek) from Tools (MCP).
3.  **Extensibility**: Knowledge base must support dynamic updates (user uploads).

**Scale & Complexity:**
*   **Primary Domain**: AI-Agent Orchestration & RAG
*   **Complexity**: High (RAG + Agent State Machine + Streaming)
*   **Critical Constraint**: Elegant integration of DeepSeek streaming and MCP tool calls within FastAPI.

### Technical Constraints & Dependencies

*   **Backend**: Python / FastAPI
*   **Agent Framework**: LangChain (Deep Agents)
*   **Model Provider**: DeepSeek API
*   **Tooling Protocol**: Model Context Protocol (MCP) servers for multimodal capabilities.
*   **Frontend**: Existing React app (modification required for streaming thought display).

### Cross-Cutting Concerns Identified

*   **Streaming Protocol**: WebSocket vs SSE for "Thought" transmission.
*   **State Management**: Persisting Agent state during long-running video generation tasks.
*   **Knowledge Base Vector Store**: Selection of Vector DB for RAG.

## Starter Template Evaluation

### Primary Technology Domain
**Backend API & AI Agent Orchestration (Python)**

### Selected Approach: Custom FastAPI + LangGraph Scaffold

**Rationale for Selection:**
Standard boilerplates do not fully support the "Deep Agent" patterns (Cyclic Graphs, Persistence) required by the project. A custom scaffold allows us to:
1.  Optimize **FastAPI** for WebSocket streaming of LangGraph events.
2.  Native integration of **DeepSeek** as the reasoning brain.
3.  Implement **MCP Client** interfaces for multimodal expansions.

**Architectural Decisions Provided:**
*   **Runtime**: Python 3.11+
*   **Orchestration**: LangGraph (Stateful Deep Agents)
*   **API Interface**: REST (Control) + WebSocket (Streaming Thoughts)
*   **Validation**: Pydantic v2
*   **Async**: Fully asynchronous I/O
*   **Agent Pattern**: ReAct / Plan-and-Execute (via LangGraph)

**Initialization Command:**
*(Custom scaffold will be built during Implementation phase)*

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**
*   **Streaming Protocol**: WebSocket
*   **Vector Database**: PostgreSQL (pgvector)
*   **Multi-Provider Strategy**: Abstract Factory Pattern

**Important Decisions (Shape Architecture):**
*   **State Store**: PostgreSQL (Async)
*   **Auth**: Token-based (Bearer)

### Data Architecture

*   **Vector Database**: **PostgreSQL + pgvector**
    *   **Rationale**: Simplifies stack (reuse existing DB), proven performance for RAG, easy ACID compliance.
    *   **Alternatives Considered**: Chroma (less mature), Pinecone (added cost/complexity).
*   **Agent State Store**: **PostgreSQL (Async)**
    *   **Rationale**: LangGraph requires a persistent checkpoint saver. Postgres ensures reliability for long-running workflows (e.g., video generation).
*   **ORM**: **SQLAlchemy (Async)** with Pydantic v2 validation.

### API & Communication Patterns

*   **Streaming Protocol**: **WebSocket**
    *   **Rationale**: Full-duplex communication allowing real-time "Thought" streaming and potential user intervention (Human-in-the-loop) during generation.
    *   **Path**: `/ws/generate/{workflow_id}`
*   **Multimodal Provider Design**: **Abstract Factory / Strategy Pattern**
    *   **Interface**: `IBaseGenerator` (Image/Video).
    *   **Adapters**: `GeminiAdapter`, `OpenRouterAdapter`, `VolcEngineAdapter`, `QwenAdapter`.
    *   **Config**: Dynamic Provider Switching via Agent Config or Env Vars.
    *   **Rationale**: Meets user requirement for provider diversity and easy switching.

### Authentication & Security

*   **Method**: **Bearer Token (JWT)**
    *   **Rationale**: Standard, stateless, easy integration with React frontend.

### Infrastructure & Deployment

*   **FastAPI Worker**: `uvicorn` (Asynchronous ASGI).
*   **Task Queue**: **Celery + Redis**
    *   **Rationale**: Handling extremely long-running video generation tasks (async polling) without blocking WebSocket connections.

### Decision Impact Analysis

**Implementation Sequence:**
1.  Setup FastAPI + Postgres (pgvector) + Redis.
2.  Implement Multi-Provider Interfaces (Image/Video Generators).
3.  Implement LangGraph Engine with DeepSeek.
4.  Implement WebSocket Streaming Layer.
5.  Frontend Integration.

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:**
3 areas where AI agents could make different choices: JSON Casing, Streaming Protocol, Code Organization.

### Naming Patterns

**Database Naming Conventions & Code Naming:**
*   **Python Internal**: `snake_case` (e.g., `user_id`, `get_user_data`)
*   **Database Tables**: `snake_case` (e.g., `generation_tasks`, `video_assets`)
*   **API Naming Conventions (Key Decision)**:
    *   **JSON Response Keys**: `camelCase` (e.g., `userId`, `taskStatus`)
    *   **Enforcement**: All Pydantic models MUST use `model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)`.
    *   *Rationale*: Ensures Pythonic backend code while strictly adhering to React/JavaScript frontend conventions.

### Structure Patterns

**Project Organization:**
*   `app/agents/`: Tangible LangGraph workflow definitions (e.g., `copywriter.py`, `media_planner.py`).
*   `app/core/`: Application core (Config, Logging, Security).
*   `app/services/generators/`: Concrete implementations of Multi-Provider Adapters (Gemini, Qwen, etc.).
*   `app/services/mcp/`: MCP Client implementations for tool calling.
*   `app/api/ws/`: Socket.io event handlers.

### Communication Patterns

**Streaming Protocol (Refined via Advanced Elicitation):**
*   **Protocol**: **Socket.io (Async)** via `python-socketio`.
    *   *Rationale*: Provides built-in reconnection, heartbeats, and ack mechanisms critical for robust Mobile/Web agent interactions, superior to raw WebSockets.
*   **Event Names**:
    *   `agent:thought`: Intermediate reasoning steps (Streaming from DeepSeek).
    *   `agent:tool_call`: When agent invokes a tool (e.g., "Generating Image...").
    *   `agent:result`: Final output payload.
    *   `agent:error`: Error details.
*   **Payload Structure**:
    ```json
    {
      "type": "thought",
      "workflowId": "uuid",
      "data": { "content": "Thinking about..." },
      "timestamp": "ISO8601"
    }
    ```

### Enforcement Guidelines

**All AI Agents MUST:**
1.  Use `python-socketio` for any real-time feature, NEVER raw `websockets`.
2.  Define Pydantic models with `alias_generator=to_camel` for all API I/O.
3.  Place all external API integrations (Gemini, etc.) in `app/services/generators/` adhering to the `IBaseGenerator` interface.

## Project Structure & Boundaries

### Complete Project Directory Structure

```text
E_Business/
├── backend/
│   ├── app/
│   │   ├── domain/                  # [Core] Pure Business Definitions
│   │   │   ├── interfaces/          # Abstractions (IGenerator, IRepo) for providers
│   │   │   ├── entities/            # Pure Python Data Classes
│   │   │   └── exceptions.py        # Domain Exceptions
│   │   ├── application/             # [Orchestration] Business Logic
│   │   │   ├── agents/              # LangGraph Deep Agents (Workflows)
│   │   │   ├── services/            # App Services (TaskList, PlanManager)
│   │   │   └── dtos/                # Data Transfer Objects
│   │   ├── infrastructure/          # [Implementation] Adapters & Details
│   │   │   ├── db/                  # Database Implementation
│   │   │   │   ├── models/          # SQLAlchemy Models
│   │   │   │   └── repositories/    # Repo Implementations
│   │   │   ├── generators/          # [Strategy] Provider Implementations
│   │   │   │   ├── gemini.py
│   │   │   │   ├── qwen.py
│   │   │   │   └── volc_engine.py
│   │   │   └── mcp/                 # MCP Clients
│   │   ├── interface/               # [Gateway] Entry Points
│   │   │   ├── api/                 # FastAPI REST Endpoints
│   │   │   │   ├── v1/
│   │   │   │   └── dependencies.py
│   │   │   └── ws/                  # Socket.io Event Handlers
│   │   ├── core/                    # [Cross-Cutting] Config & Utils
│   │   │   ├── config.py            # Settings
│   │   │   ├── security.py          # Auth logic
│   │   │   └── logging.py           # Structured Logger
│   │   └── main.py                  # App Entrypoint
│   ├── tests/                       # Pytest Suite
│   ├── alembic.ini                  # Migration Config
│   ├── pyproject.toml               # Poetry/Pip dependencies
│   ├── Dockerfile
│   └── docker-compose.yml
```

### Architectural Boundaries

**Pragmatic Clean Architecture:**
This structure enforces strict dependency rules: `Domain` depends on nothing. `Application` depends only on `Domain`. `Infrastructure` and `Interface` depend on everything. This structure is specifically chosen to support the **Abstract Factory based Multi-Provider Strategy**.

**Layer Responsibilities:**
*   **Domain**: Defines `IGenerator` interface. Knows nothing about Gemini or Qwen.
*   **Infrastructure/Generators**: Implements `GeminiGenerator`, `QwenGenerator`. Contains all vendor-specific dirty code.
*   **Application/Agents**: Uses `IGenerator` to request images/videos. Agnostic of which provider is active.

### Requirements to Structure Mapping

**Functional Requirements:**
*   **Text Generation (DeepSeek)**: `app/application/agents/text_agent.py` -> `app/infrastructure/generators/deepseek.py`
*   **Image/Video (Multi-Provider)**: `app/infrastructure/generators/{provider}.py`
*   **Streaming (Real-time)**: `app/interface/ws/socket_manager.py` (Socket.io)

### Integration Points

**Plugin System (Multi-Provider):**
*   New providers (e.g., "VolcEngine") are added by creating `app/infrastructure/generators/volc.py` implementing `IGenerator`, then registering in `app/core/config.py`. No changes needed in Agent logic.

## Architecture Validation Results

### Coherence Validation ✅

*   **Decision Compatibility**: socket.io fits perfectly with the event-driven nature of LangGraph.
*   **Structure Alignment**: The 4-layer Clean Architecture strictly isolates the "Multi-Provider" logic in `infrastructure/`, creating a stable core.

### Requirements Coverage Validation ✅

*   **RAG**: Supported via `domain/interfaces/IRepository` -> `infrastructure/db/pgvector`.
*   **Deep Agents**: Supported via `application/agents/` (LangGraph).
*   **Human-in-loop**: Enabled by socket.io full-duplex events.

### Implemented Refinements (Party Mode)

1.  **Pure Domain Entities**: `app/domain/entities` MUST use Python `dataclasses`. Pydantic models are restricted to `app/application/dtos` and `app/infrastructure/db`.
2.  **Unified HTTP Client**: Add `app/core/http_client.py` (`BaseHTTPClient`) to handle retries/timeouts centrally for all generator adapters.
3.  **Mock Server**: Add `tests/mocks/mock_agent_server.py` to simulate DeepSeek streaming during frontend integration tests.

### Architecture Readiness Assessment

**Overall Status**: READY FOR IMPLEMENTATION

**Confidence Level**: High

**Key Strengths**:
*   Clean separation of concerns (Logic vs Tools).
*   Robust streaming protocol (Socket.io).
*   Future-proof multi-provider support.

**Implementation Handoff:**
*   Follow the directory structure exactly.
*   Ensure Domain Entities are pure.
*   Implement `IBaseGenerator` first before adding concrete providers.
