# Story 2.2: Copywriting Agent Workflow

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **user**,
I want **the AI to plan and draft product copy using a multi-stage workflow**,
so that **the output is high quality, structured, and includes visible reasoning**.

## Acceptance Criteria

1. **Given** a product name and features
2. **When** the `CopywritingAgent` workflow executes
3. **Then** it transitions through `Plan` -> `Draft` -> `Critique` -> `Finalize` states
4. **And** the final state contains the polished marketing copy
5. **And** intermediate thoughts are streamed via Socket.io

## Tasks / Subtasks

- [x] **Task 1: Define Agent State Schema** (AC: 1, 2)
  - [x] Subtask 1.1: Create `CopywritingState` dataclass in `app/domain/entities/agent_state.py`
  - [x] Subtask 1.2: Define state fields: product_name, features, plan, draft, critique, final_copy, current_stage
  - [x] Subtask 1.3: Add state transition validation logic

- [x] **Task 2: Implement LangGraph Workflow Nodes** (AC: 2, 3)
  - [x] Subtask 2.1: Create `CopywritingAgent` in `app/application/agents/copywriting_agent.py`
  - [x] Subtask 2.2: Implement `plan_node` - analyzes requirements and creates outline
  - [x] Subtask 2.3: Implement `draft_node` - generates initial copy based on plan
  - [x] Subtask 2.4: Implement `critique_node` - reviews and improves the draft
  - [x] Subtask 2.5: Implement `finalize_node` - produces final polished copy
  - [x] Subtask 2.6: Build StateGraph with conditional edges for stage transitions

- [x] **Task 3: Integrate Socket.io Thought Streaming** (AC: 5)
  - [x] Subtask 3.1: Inject `socket_manager` into agent workflow
  - [x] Subtask 3.2: Emit `agent:thought` events on each node entry
  - [x] Subtask 3.3: Include workflow_id, node_name, and content in payload
  - [x] Subtask 3.4: Handle WebSocket connection errors gracefully

- [x] **Task 4: Create API Endpoint** (AC: 1, 4)
  - [x] Subtask 4.1: Add `POST /api/v1/copywriting/generate` endpoint
  - [x] Subtask 4.2: Accept product_name, features, optional brand_guidelines
  - [x] Subtask 4.3: Return workflow_id for tracking
  - [x] Subtask 4.4: Execute agent asynchronously

- [x] **Task 5: Testing** (AC: 1-5)
  - [x] Subtask 5.1: Unit tests for each node function
  - [x] Subtask 5.2: Integration test for complete workflow
  - [x] Subtask 5.3: Socket.io event emission tests
  - [x] Subtask 5.4: Mock DeepSeek API responses

## Dev Notes

### Story Foundation

**Epic Context (Epic 2: Intelligent Product Copywriting)**
- **Objective**: Implement the first core business Agent for AI-powered copywriting
- **Business Value**: Enable users to generate high-quality product copy with visible AI reasoning
- **Technical Stack**: LangGraph (agent framework) + DeepSeek (LLM) + Socket.io (streaming)

**Story-Specific Requirements:**
- Multi-stage agent workflow: Plan → Draft → Critique → Finalize
- Real-time thought streaming to frontend via Socket.io
- State persistence across workflow transitions
- Integration with DeepSeekGenerator from Story 2-1

### Architecture Patterns

**Clean Architecture Compliance:**
| Layer | Component | Purpose |
|-------|-----------|---------|
| Domain | `entities/agent_state.py` | Pure dataclass for agent state |
| Application | `agents/copywriting_agent.py` | LangGraph workflow logic |
| Interface | `api/v1/copywriting.py` | REST endpoint for triggering workflow |
| Infrastructure | `generators/deepseek.py` | LLM calls (reused from Story 2-1) |

**LangGraph Pattern Reference:**
```python
from langgraph.graph import StateGraph, END

# 1. Define state schema (Task 1)
class CopywritingState(TypedDict):
    product_name: str
    features: List[str]
    plan: Optional[str]
    draft: Optional[str]
    critique: Optional[str]
    final_copy: Optional[str]

# 2. Define nodes (Task 2)
async def plan_node(state: CopywritingState) -> CopywritingState:
    # Use DeepSeek to create outline
    ...

# 3. Build graph (Task 2)
workflow = StateGraph(CopywritingState)
workflow.add_node("plan", plan_node)
workflow.add_node("draft", draft_node)
workflow.add_node("critique", critique_node)
workflow.add_node("finalize", finalize_node)

# 4. Add edges with transitions
workflow.set_entry_point("plan")
workflow.add_conditional_edges(
    "plan",
    should_continue,  # Routing logic
    {"draft": "draft", "end": END}
)
```

### Socket.io Integration

**Event Payload Structure** (from `socket_manager.py`):

The `SocketManager` provides dedicated methods for emitting agent events. Each method automatically constructs the proper payload structure:

```python
# Emit agent:thought
await socket_manager.emit_thought(workflow_id, content, sid=None)

# Emit agent:tool_call
await socket_manager.emit_tool_call(workflow_id, tool_name, status, message, sid=None)

# Emit agent:result
await socket_manager.emit_result(workflow_id, result_data, sid=None)

# Emit agent:error
await socket_manager.emit_error(workflow_id, error_code, error_message, details=None, sid=None)
```

**Payload Structure** (automatically constructed by `SocketManager`):
```json
{
  "type": "thought|tool_call|result|error",
  "workflowId": "uuid",
  "data": { /* event-specific data */ },
  "timestamp": "ISO8601"
}
```

**Implementation Pattern:**
```python
from app.interface.ws.socket_manager import socket_manager

async def plan_node(state: CopywritingState) -> CopywritingState:
    workflow_id = state.get("workflow_id")

    # Emit thinking event using dedicated method
    await socket_manager.emit_thought(
        workflow_id=workflow_id,
        content=f"[plan] Planning copy for: {state['product_name']}"
    )

    # Call DeepSeek for actual planning (with async context manager)
    async with ProviderFactory.get_provider("deepseek") as generator:
        prompt = f"Create marketing outline for {state['product_name']} with features: {state['features']}"
        response = await generator.generate(
            GenerationRequest(
                prompt=prompt,
                model="deepseek-chat"  # Required field
            )
        )

    return {**state, "plan": response.content}
```

### Project Structure Notes

**File Locations:**
```
backend/app/
├── domain/
│   └── entities/
│       └── agent_state.py          # [CREATE] CopywritingState dataclass
├── application/
│   ├── agents/
│   │   └── copywriting_agent.py   # [CREATE] LangGraph workflow
│   └── dtos/
│       └── copywriting.py          # [CREATE] Request/Response DTOs
├── interface/
│   └── api/
│       └── v1/
│           └── copywriting.py      # [CREATE] REST endpoint
└── infrastructure/
    └── generators/
        └── deepseek.py             # [REUSE] From Story 2-1
```

**Naming Conventions:**
- Python: `snake_case` (e.g., `copywriting_agent`, `plan_node`)
- API JSON: `camelCase` (e.g., `productName`, `workflowId`)
- Use Pydantic `alias_generator=to_camel` for DTOs

### Previous Story Intelligence (Story 2-1: DeepSeek Client)

**Learnings from Story 2-1:**
1. **DeepSeekGenerator** implements `IGenerator` with async `generate()` and `generate_stream()` methods
2. **StreamChunk** entity has separate `content` and `reasoning_content` fields
3. **BaseHTTPClient** has `stream_sse()` method for SSE streaming
4. **ProviderFactory** registers generators with string key lookup

**Reusable Components:**
```python
# Story 2-1 implementation already provides:
from app.infrastructure.generators.deepseek import DeepSeekGenerator
from app.core.factory import ProviderFactory
from app.domain.entities.generation import GenerationRequest, GenerationResult

# Get generator instance (no async, returns instance directly):
async with ProviderFactory.get_provider("deepseek") as generator:
    response = await generator.generate(
        GenerationRequest(
            prompt="Your prompt here",
            model="deepseek-chat",  # Required field
            temperature=0.7,
            max_tokens=2000
        )
    )
```

**Important:** Use `GenerationRequest` and `GenerationResult` entities from `app/domain/entities/generation.py` - do NOT create new request/response types.

### Git Intelligence

**Recent Relevant Commits:**
- `118b90b`: Socket.io rate limiting and security fixes (Story 1.3)
- `a969aee`: Agent design structure documentation
- `814ba53`: Frontend user profile and notification modals

**Code Patterns Established:**
1. Socket.io authentication via JWT in handshake
2. Rate limiting using `slowapi` library
3. CORS configuration for frontend domain
4. Async context managers for resource cleanup

**File Creation Pattern:**
- Use `__init__.py` exports for clean imports
- Separate domain entities from DTOs
- Pydantic models for API I/O with `to_camel` alias generator

### Dependencies

**Required Dependencies** (from Story 1.x + 2-1):
```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
langgraph = "^0.0.20"  # NEW: LangGraph for agent workflows
langchain = "^0.1.0"   # NEW: LangChain core
python-socketio = "^5.10.0"
pydantic = "^2.5.0"
sqlalchemy = "^2.0.23"
asyncpg = "^0.29.0"
aiohttp = "^0.11.0"   # For HTTP client (from Story 2-1)

[tool.poetry.dev-dependencies]
pytest = "^7.4.3"
pytest-asyncio = "^0.21.1"
```

**Import Dependencies:**
```python
# Agent workflow
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver  # For state persistence

# Domain entities
from app.domain.entities.agent_state import CopywritingState
from app.domain.entities.generation import GenerationRequest, GenerationResult

# Application services
from app.infrastructure.generators.deepseek import DeepSeekGenerator
from app.core.factory import ProviderFactory

# Interface
from app.interface.ws.socket_manager import socket_manager
```

### Testing Requirements

**Unit Test Structure:**
```python
# tests/test_copywriting_agent.py
import pytest
from app.application.agents.copywriting_agent import CopywritingAgent
from app.domain.entities.agent_state import CopywritingState

@pytest.mark.asyncio
async def test_plan_node():
    agent = CopywritingAgent()
    state = CopywritingState(
        product_name="Test Product",
        features=["Feature 1", "Feature 2"]
    )
    result = await agent.plan_node(state)
    assert result["plan"] is not None
    assert "outline" in result["plan"].lower()

@pytest.mark.asyncio
async def test_full_workflow():
    agent = CopywritingAgent()
    result = await agent.run(
        product_name="Test Product",
        features=["Feature 1"]
    )
    assert result["final_copy"] is not None
```

**Mock Strategy:**
- Mock `DeepSeekGenerator.generate()` to return predefined responses
- Mock `socket_manager.emit()` to verify event emissions
- Use `pytest-asyncio` for async test execution

**Coverage Requirements:**
- Each node function: ≥80% coverage
- State transition logic: 100% coverage
- Error handling paths: ≥70% coverage

### Error Handling Strategy

**Agent-Level Errors:**
```python
from app.domain.exceptions import HTTPClientError

async def plan_node(state: CopywritingState) -> CopywritingState:
    try:
        async with ProviderFactory.get_provider("deepseek") as generator:
            response = await generator.generate(
                GenerationRequest(
                    prompt=...,
                    model="deepseek-chat"
                )
            )
        return {**state, "plan": response.content}
    except HTTPClientError as e:
        await socket_manager.emit_error(
            workflow_id=state["workflow_id"],
            error_code="PLANNING_FAILED",
            error_message=str(e)
        )
        raise  # Re-raise the original exception for proper handling
```

**State Persistence:**
- Use `SqliteSaver` for LangGraph checkpointing
- Store workflow_id in state for Socket.io correlation
- Handle workflow interruption gracefully

### API Contract

**Endpoint:** `POST /api/v1/copywriting/generate`

**Request:**
```json
{
  "productName": "Smart Watch Pro",
  "features": [
    "Heart rate monitoring",
    "GPS tracking",
    "7-day battery life"
  ],
  "brandGuidelines": "Optional brand voice instructions"
}
```

**Response:**
```json
{
  "workflowId": "uuid-v4",
  "status": "started",
  "message": "Copywriting workflow initiated. Listen for agent:thought events."
}
```

**Socket.io Events:**
```javascript
// Frontend listens for:
socket.on("agent:thought", (data) => {
  console.log(`[${data.node}] ${data.content}`);
});

socket.on("agent:result", (data) => {
  console.log("Final copy:", data.finalCopy);
});

socket.on("agent:error", (data) => {
  console.error("Agent error:", data.error);
});
```

### References

**Source Documents:**
- [Source: _bmad-output/planning-artifacts/epics.md#Epic-2](../../planning-artifacts/epics.md) - Epic 2 complete requirements
- [Source: _bmad-output/planning-artifacts/architecture.md](../../planning-artifacts/architecture.md) - Architecture patterns and structure
- [Source: _bmad-output/implementation-artifacts/2-1-deepseek-client-implementation.md](./2-1-deepseek-client-implementation.md) - DeepSeek integration details

**LangGraph Documentation:**
- https://langchain-ai.github.io/langgraph/ - StateGraph API reference
- https://langchain-ai.github.io/langgraph/concepts/persistence/ - Checkpoint saving

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

### Completion Notes List

- ✅ 创建了 `CopywritingState` dataclass 和 `CopywritingStage` 枚举，包含完整的状态转换验证逻辑
- ✅ 实现了 `CopywritingAgent` 类，包含 plan_node, draft_node, critique_node, finalize_node 四个工作流节点
- ✅ 集成 socket_manager 用于实时推送 agent:thought 和 agent:result 事件
- ✅ 创建 POST /api/v1/copywriting/generate 端点，支持异步执行工作流
- ✅ 添加了 Pydantic DTOs 并使用 camelCase 别名
- ✅ 编写了完整的单元测试和集成测试，覆盖所有节点和 API 端点
- ⚠️ 需要在 Docker 环境中运行测试（因为依赖需要在容器中安装）

### File List

**Files to Create:**
1. `backend/app/domain/entities/agent_state.py` - CopywritingState dataclass
2. `backend/app/application/agents/copywriting_agent.py` - LangGraph workflow
3. `backend/app/application/dtos/copywriting.py` - Request/Response DTOs
4. `backend/app/interface/routes/copywriting.py` - REST endpoint
5. `backend/tests/application/agents/test_copywriting_agent.py` - Unit tests
6. `backend/tests/interface/routes/test_copywriting.py` - API endpoint tests

**Files to Modify:**
1. `backend/app/main.py` - Include copywriting router
2. `backend/app/domain/entities/__init__.py` - Export agent_state
3. `backend/app/application/agents/__init__.py` - Export CopywritingAgent
4. `backend/requirements.txt` or `backend/pyproject.toml` - Add langgraph, langchain dependencies

**Files to Reference (No Changes):**
1. `backend/app/infrastructure/generators/deepseek.py` - Reuse from Story 2-1
2. `backend/app/core/factory.py` - ProviderFactory from Story 2-1
3. `backend/app/interface/ws/socket_manager.py` - Socket.io manager from Story 1.3
