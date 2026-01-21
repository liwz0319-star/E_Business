---
stepsCompleted: [1, 2, 3]
inputDocuments: ['f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md', 'f:/AAA Work/AIproject/E_Business/_bmad-output/project-documentation/project-overview.md']
---

# E_Business - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for E_Business, decomposing the requirements from the PRD, and Architecture requirements into implementable stories.

## Requirements Inventory

### Functional Requirements

FR1: System must maintain a "Best Practices" knowledge base (RAG) using PostgreSQL+pgvector.
FR2: Deep Agents must retrieve relevant cases/rules from knowledge base before generation.
FR3: Generate Product Copy using DeepSeek model.
FR4: Expose complete Thinking/Planning process to frontend via WebSocket/Socket.io.
FR5: Generate Product Images via MCP (Abstract Factory).
FR6: Generate Ad Videos via MCP (Abstract Factory).
FR7: Real-time streaming of Agent thoughts and tool calls to React frontend.

### NonFunctional Requirements

NFR1: RAG Retrieval must not significantly impact generation latency.
NFR2: Modularity: Decouple Logic (DeepSeek) from Tools (MCP).
NFR3: Extensibility: Knowledge base must support dynamic updates (user uploads).
NFR4: Backend must use Python 3.11+ and FastAPI.
NFR5: Agent Framework must be LangChain/LangGraph.
NFR6: Architecture must follow Pragmatic Clean Architecture.

### Additional Requirements

- **Starter Template**: Custom FastAPI + LangGraph Scaffold (Greenfield implementation in backend/).
- **Database**: PostgreSQL (Async) + pgvector.
- **Auth**: Bearer Token (JWT).
- **Transport**: Socket.io for streaming.
- **Structure**: Domain/App/Infra/Interface layers.
- **Frontend Integration**: Existing React app needs modification to consume Socket.io events.

### FR Coverage Map

FR1: Epic 5
FR2: Epic 5
FR3: Epic 2
FR4: Epic 1, Epic 2
FR5: Epic 3
FR6: Epic 4
FR7: Epic 1
NFR1: Epic 5
NFR4: Epic 1
NFR5: Epic 2
NFR6: Epic 1

## Epic List

### Epic 1: Backend Foundation & Streaming Core
Establish high-availability backend architecture and implement real-time full-duplex communication pipeline between frontend and AI.
**FRs covered:** FR4, FR7, NFR4, NFR6

### Epic 2: Intelligent Product Copywriting (Text Agent)
Implement the first core business Agent, enabling users to generate product copy using DeepSeek with visible thinking process.
**FRs covered:** FR3, FR4, NFR5

### Epic 3: Visual Content Studio (Image Agent)
Extend multimodal capabilities to support product image generation via MCP.
**FRs covered:** FR5

### Epic 4: Video Marketing Suite (Video Agent)
Implement handling of long-running video generation tasks via MCP and Async Task Queue.
**FRs covered:** FR6

### Epic 5: Smart Knowledge Base (RAG)
Enable AI to generate brand-aligned content by retrieving "Best Practices" from a knowledge base.
**FRs covered:** FR1, FR2, NFR1, NFR3

## Epic 1: Backend Foundation & Streaming Core

Establish high-availability backend architecture and implement real-time full-duplex communication pipeline between frontend and AI.

### Story 1.1: Backend Project Initialization

As a developer,
I want to initialize the FastAPI project structure with Docker and Poetry,
So that I have a consistent, runnable environment for development.

**Acceptance Criteria:**

**Given** a clean git branch
**When** I run the initialization commands
**Then** a `backend` directory is created with `app`, `tests` folders
**And** `pyproject.toml` includes fastapi, uvicorn, sqlalchemy, asyncpg, python-socketio dependencies
**And** `docker-compose.yml` successfully spins up `api`, `db`, and `redis` containers
**And** accessing `http://localhost:8000/health` returns 200 OK

### Story 1.2: Database & Auth Setup

As a user,
I want to authenticate via JWT,
So that my data and generations are secure.

**Acceptance Criteria:**

**Given** the database container is running
**When** I run `alembic upgrade head`
**Then** the `users` table is created in Postgres
**And** `POST /auth/login` with valid credentials returns a standard JWT Bearer token
**And** generic API dependency `get_current_user` correctly decodes the token

### Story 1.3: Socket.io Server & Security

As a developer,
I want to establish a secure Socket.io connection,
So that I can stream real-time events to the frontend.

**Acceptance Criteria:**

**Given** a running API server
**When** a client connects to `/ws` with a valid JWT in the handshake auth
**Then** the connection is accepted and the socket ID is logged
**When** a client connects without a token
**Then** the connection is rejected (401)
**And** the server supports CORS for the frontend domain

### Story 1.4: BaseHTTPClient & Provider Factory

As a developer,
I want a unified HTTP client and factory for generators,
So that I can easily add new AI providers without duplicating network logic.

**Acceptance Criteria:**

**Given** the `app/core/http_client.py` module
**When** I use `BaseHTTPClient` to make a request
**Then** it automatically handles retries (3 times) and timeouts
**And** `ProviderFactory` can instantiate a generator class based on a string key (e.g., "deepseek")
**And** `IGenerator` interface is defined in the Domain layer

## Epic 2: Intelligent Product Copywriting (Text Agent)

Implement the first core business Agent, enabling users to generate product copy using DeepSeek with visible thinking process.

### Story 2.1: DeepSeek Client Implementation

As a developer,
I want to integrate the DeepSeek API using the Generator interface,
So that the system can generate text using this model.

**Acceptance Criteria:**

**Given** a valid DeepSeek API Key
**When** `DeepSeekGenerator.generate(prompt)` is called
**Then** it returns text content from the API
**When** `stream=True` is passed
**Then** it yields chunks of text and "thinking" tokens separately

### Story 2.2: Copywriting Agent Workflow

As a user,
I want the AI to plan and draft product copy,
So that the output is high quality and structured.

**Acceptance Criteria:**

**Given** a product name and features
**When** the `CopywritingAgent` workflow executes
**Then** it transitions through `Plan` -> `Draft` -> `Critique` -> `Finalize` states
**And** the final state contains the polished marketing copy

### Story 2.3: Thinking Stream Integration

As a user,
I want to see the AI's "thinking" process (Step 1, Step 2...),
So that I understand how the result is being generated.

**Acceptance Criteria:**

**Given** a running Copywriting Agent
**When** the agent transitions nodes or thinks
**Then** `socket_manager.emit` is triggered with type `agent:thought`
**And** the payload contains `workflow_id`, `node_name`, and text content
**And** the frontend can receive these events in real-time

## Epic 3: Visual Content Studio (Image Agent)

Extend multimodal capabilities to support product image generation via MCP.

### Story 3.1: Image Generation Agent

As a user,
I want to generate product images by describing them,
So that I can visualize my product concepts.

**Acceptance Criteria:**

**Given** a text description of a product
**When** the `ImageAgent` is invoked
**Then** it refines the prompt using DeepSeek
**And** calls the `ImageGenerator` via MCP
**And** returns a URL to the generated image
**And** the image is persisted in `video_assets` table (reusing table for generic assets)

### Story 3.2: MCP Client for Image Tools

As a developer,
I want to call image generation tools via MCP,
So that I can switch providers without changing agent logic.

**Acceptance Criteria:**

**Given** a running MCP Server (or mock)
**When** `MCPImageGenerator` is called
**Then** it formats the request according to MCP protocol
**And** sends it to the configured tool server
**And** parses the result back into a standard `ImageArtifact` domain entity

## Epic 4: Video Marketing Suite (Video Agent)

Implement handling of long-running video generation tasks via MCP and Async Task Queue.

### Story 4.1: Async Video Task Queue

As a developer,
I want to offload video generation to a background queue,
So that long-running tasks don't block the WebSocket connection.

**Acceptance Criteria:**

**Given** a Redis instance
**When** a video generation task is submitted
**Then** it is pushed to the Celery queue
**And** `task_id` is immediately returned to the client
**And** the client receives a "queued" status update via Socket.io

### Story 4.2: Video Generation Agent

As a user,
I want to generate a short video ad,
So that I can use it for social media marketing.

**Acceptance Criteria:**

**Given** a product script or description
**When** the `VideoAgent` runs
**Then** it generates a storyboard (prompt sequence)
**And** submits generation tasks for each scene
**And** polls for completion status
**When** completed, it returns the final video URL

### Story 4.3: MCP Client for Video Service

As a developer,
I want to integrate video providers (e.g. Veo) via MCP,
So that the system supports diverse video models.

**Acceptance Criteria:**

**Given** an `IVideoGenerator` interface
**When** `MCPVideoGenerator` is called
**Then** it handles the async nature of video APIs (submit job -> poll id)
**And** normalizes the provider-specific status (processing, succeeded, failed) into Domain status

## Epic 5: Smart Knowledge Base (RAG)

Enable AI to generate brand-aligned content by retrieving "Best Practices" from a knowledge base.

### Story 5.1: Knowledge Ingestion API

As a user,
I want to upload my brand guidelines (PDF/Text),
So that the AI knows my brand voice.

**Acceptance Criteria:**

**Given** a text or PDF file
**When** I `POST /knowledge/upload`
**Then** the file is parsed into text chunks
**And** chunks are embedded using an embedding model
**And** vectors are stored in the `knowledge_embeddings` table in Postgres

### Story 5.2: Retrieval Tool Implementation

As a developer,
I want to provide a "RetrieveBestPractices" tool to Agents,
So that they can access the knowledge base.

**Acceptance Criteria:**

**Given** a search query
**When** the `RetrievalTool` is called
**Then** it performs a cosine similarity search in Postgres
**And** returns the top 3 most relevant text chunks
**And** latency is under 500ms

### Story 5.3: RAG-Enhanced Generation

As a user,
I want the generated copy to follow my brand rules,
So that I don't have to manually edit it.

**Acceptance Criteria:**

**Given** a user prompt and available knowledge base
**When** the `CopywritingAgent` runs
**Then** it first calls `RetrievalTool` with keywords from the prompt
**And** injects the retrieved rules into the DeepSeek system prompt
**And** the generated output adheres to the retrieved guidelines
