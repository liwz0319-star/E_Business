# Story 2.3: Thinking Stream Integration

Status: done

<!-- Story reviewed and updated on 2026-01-23 based on comprehensive audit -->

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **user**,
I want **to see the AI's "thinking" process (Step 1, Step 2...) in real-time**,
so that **I understand how the result is being generated**.

## Acceptance Criteria

1. **Given** a running Copywriting Agent workflow
2. **When** the agent transitions nodes or thinks
3. **Then** `socket_manager.emit_thought()` accepts `node_name` parameter without raising `TypeError`
4. **And** the event payload's `data` section contains `node_name` field when provided
5. **And** the payload's `data` section contains both `content` and optional `node_name`
6. **And** the frontend can receive these events in real-time
7. **And** DeepSeek's `reasoning_content` is streamed as `agent:thought` events during generation
8. **And** streaming failures are handled gracefully with fallback to non-streaming mode

## Tasks / Subtasks

- [x] **Task 1: Fix SocketManager.emit_thought() Signature** (AC: 3, 4)
  - [x] Subtask 1.1: Add `node_name` parameter to `emit_thought()` method
  - [x] Subtask 1.2: Include `node_name` in event payload's `data` section
  - [x] Subtask 1.3: Update docstring to reflect new parameter

- [x] **Task 2: Verify CopywritingAgent Integration** (AC: 2, 5)
  - [x] Subtask 2.1: Ensure all node transitions call `emit_thought()` with correct `node_name`
  - [x] Subtask 2.2: Test event emission reaches frontend in real-time
  - [x] Subtask 2.3: Verify payload structure matches frontend expectations

- [x] **Task 3: Enable DeepSeek Streaming Thoughts** (AC: 4, 5)
  - [x] Subtask 3.1: Switch `_generate()` calls to `_generate_with_streaming()` in nodes
  - [x] Subtask 3.2: Ensure DeepSeek `reasoning_content` is streamed as `agent:thought` events
  - [x] Subtask 3.3: Add error handling for streaming failures

- [x] **Task 4: Testing** (AC: 3-8)
  - [x] Subtask 4.1: Unit test for `emit_thought()` with `node_name`
  - [x] Subtask 4.2: Unit test for `emit_thought()` without `node_name` (edge case)
  - [x] Subtask 4.3: Integration test for complete workflow with streaming
  - [x] Subtask 4.4: Mock DeepSeek streaming responses
  - [x] Subtask 4.5: Verify Socket.io event payload structure
  - [x] Subtask 4.6: Test streaming failure fallback to non-streaming mode
  - [x] Subtask 4.7: Test socket disconnection handling during streaming

## Dev Notes

### Story Foundation

**Story Review Summary (2026-01-23):**
- **Original Score**: 4.6/5
- **Critical Bug Confirmed**: Story 2-2's `copywriting_agent.py` calls `emit_thought(node_name=...)` but `socket_manager.py` doesn't accept this parameter → Runtime TypeError
- **Updates Applied**:
  1. Enhanced Acceptance Criteria with verification steps (8 criteria total)
  2. Added edge case tests (node_name=None, streaming failures)
  3. Improved error handling with rate-limited logging (5-second cooldown)
  4. Added node_name usage convention guidelines
  5. Updated API contract examples to handle undefined node_name
  6. Clarified dependency issues with Story 2-2

**Epic Context (Epic 2: Intelligent Product Copywriting)**
- **Objective**: Enable real-time visibility into AI's reasoning process
- **Business Value**: Users gain transparency and trust by seeing AI's "thinking"
- **Technical Stack**: Socket.io (real-time) + DeepSeek streaming API

**Story-Specific Requirements:**
- Real-time streaming of AI thinking process to frontend
- Event payload must include `node_name` for UI categorization
- Stream DeepSeek's `reasoning_content` as it arrives
- Handle connection failures gracefully

### Architecture Patterns

**Clean Architecture Compliance:**
| Layer | Component | Purpose |
|-------|-----------|---------|
| Interface | `ws/socket_manager.py` | Socket.io event emission |
| Application | `agents/copywriting_agent.py` | Agent workflow with streaming callbacks |

**Event Payload Structure** (Target):
```json
{
  "type": "thought",
  "workflowId": "uuid-v4",
  "data": {
    "node_name": "plan|draft|critique|finalize",
    "content": "Thinking step text..."
  },
  "timestamp": "2024-01-23T10:30:00Z"
}
```

### Critical Issue Found

**Problem Identified in Story 2-2 Implementation:**

The current `copywriting_agent.py` calls `emit_thought()` with a `node_name` parameter, but `socket_manager.py` doesn't accept this parameter!

**Dependency Issue:**
- Story 2-2 implemented `CopywritingAgent` with `node_name` parameter calls
- Story 2-2's `socket_manager.py` does NOT have `node_name` parameter
- This is a **breaking incompatibility** between Story 2-2 components
- Story 2-3 is required to fix this before the workflow can run

```python
# copywriting_agent.py line 167-171
await socket_manager.emit_thought(
    workflow_id=workflow_id,
    content=f"[plan] 正在为 {product_name} 规划营销大纲...",
    node_name="plan"  # ❌ This parameter doesn't exist!
)
```

**Current Signature in socket_manager.py:**
```python
async def emit_thought(
    self,
    workflow_id: str,
    content: str,
    sid: Optional[str] = None  # No node_name parameter!
) -> None:
```

**Impact:** Runtime `TypeError` will occur when the agent runs!

### Implementation Plan

**Step 1: Fix SocketManager.emit_thought() Signature**

```python
# File: backend/app/interface/ws/socket_manager.py

async def emit_thought(
    self,
    workflow_id: str,
    content: str,
    node_name: Optional[str] = None,  # NEW: Add node_name parameter
    sid: Optional[str] = None
) -> None:
    """
    Emit agent:thought event.

    Args:
        workflow_id: Workflow/conversation ID
        content: Thought content
        node_name: Optional node name (plan, draft, critique, finalize)
        sid: Optional specific socket ID (broadcasts if None)
    """
    payload = {
        "type": "thought",
        "workflowId": workflow_id,
        "data": {
            "content": content,
            **({"node_name": node_name} if node_name else {})  # NEW: Include node_name
        },
        "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    }

    try:
        await self.sio.emit("agent:thought", payload, room=sid)
        logger.debug(f"Emitted agent:thought: workflow_id={workflow_id}, node={node_name}")
    except Exception as e:
        logger.error(f"Failed to emit agent:thought: {e}")
```

**Step 2: Enable Streaming in CopywritingAgent Nodes**

The current implementation has `_generate_with_streaming()` method but nodes use `_generate()`. Need to switch:

```python
# File: backend/app/application/agents/copywriting_agent.py

async def plan_node(self, state: GraphState) -> GraphState:
    """Plan node: Create marketing outline for the product."""
    workflow_id = state["workflow_id"]
    product_name = state["product_name"]
    features = state["features"]

    # Emit node entry event
    await socket_manager.emit_thought(
        workflow_id=workflow_id,
        content=f"[plan] 正在为 {product_name} 规划营销大纲...",
        node_name="plan"
    )

    prompt = f"""你是一位专业的营销文案策划师。请为以下产品创建一份营销文案大纲。

产品名称: {product_name}

产品特点:
{chr(10).join(f"- {f}" for f in features)}

请创建一份包含以下内容的营销大纲:
1. 目标受众分析
2. 核心卖点提炼 (3-5个)
3. 情感诉求点
4. 推荐的文案结构
5. 关键词和标语建议

请用中文输出。"""

    try:
        # CHANGED: Use _generate_with_streaming to stream DeepSeek reasoning
        plan = await self._generate_with_streaming(
            prompt=prompt,
            workflow_id=workflow_id,
            node_name="plan"
        )

        # Emit completion thought
        await socket_manager.emit_thought(
            workflow_id=workflow_id,
            content=f"[plan] 营销大纲创建完成",
            node_name="plan"
        )

        return {
            **state,
            "plan": plan,
            "current_stage": CopywritingStage.PLAN.value,
        }
    except HTTPClientError as e:
        await socket_manager.emit_error(
            workflow_id=workflow_id,
            error_code="PLAN_FAILED",
            error_message=str(e)
        )
        raise
```

Apply same pattern to `draft_node`, `critique_node`, and `finalize_node`.

**Step 3: Verify Streaming Callback Implementation**

The `_generate_with_streaming()` method should stream DeepSeek's `reasoning_content`:

```python
# File: backend/app/application/agents/copywriting_agent.py

async def _generate_with_streaming(
    self,
    prompt: str,
    workflow_id: str,
    node_name: str,
) -> str:
    """Generate text with streaming callback for real-time thought updates."""
    async def stream_callback(chunk: StreamChunk) -> None:
        """Callback for streaming chunks."""
        # Emit reasoning content if available
        if chunk.reasoning_content:
            await socket_manager.emit_thought(
                workflow_id=workflow_id,
                content=chunk.reasoning_content,
                node_name=node_name
            )

    generator = ProviderFactory.get_provider("deepseek")
    async with generator:
        response = await generator.generate_stream_with_callback(
            request=GenerationRequest(
                prompt=prompt,
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            ),
            callback=stream_callback,
        )
        return response.content
```

### Project Structure Notes

**Files to Modify:**
```
backend/app/
├── interface/
│   └── ws/
│       └── socket_manager.py         # [MODIFY] Add node_name parameter
├── application/
│   └── agents/
│       └── copywriting_agent.py      # [MODIFY] Use _generate_with_streaming
└── tests/
    └── interface/
        └── test_socket_manager.py    # [CREATE/MODIFY] Test new signature
```

**Naming Conventions:**
- Python: `snake_case` (e.g., `node_name`, `workflow_id`)
- API JSON: `camelCase` (e.g., `nodeName`, `workflowId`) - but `node_name` in payload is acceptable as internal field

### Previous Story Intelligence (Story 2-2: Copywriting Agent Workflow)

**Learnings from Story 2-2:**
1. CopywritingAgent implements 4-node workflow: Plan → Draft → Critique → Finalize
2. Each node calls `socket_manager.emit_thought()` but with incompatible signature
3. `_generate_with_streaming()` method exists but is unused
4. All nodes use `_generate()` which doesn't stream DeepSeek reasoning

**Reusable Components:**
- `CopywritingState` entity from `app/domain/entities/agent_state.py`
- `CopywritingStage` enum for stage tracking
- `socket_manager` singleton for event emission
- `ProviderFactory.get_provider("deepseek")` for LLM access

**Known Compatibility Issues with Story 2-2:**
- **CRITICAL**: The `emit_thought()` calls in Story 2-2 will fail at runtime with `TypeError`
- This is because Story 2-2 implemented agent calls with `node_name` parameter
- But Story 2-2's `socket_manager.py` does NOT accept `node_name` parameter
- Story 2-3 must fix this breaking incompatibility before the workflow can run
- After fixing Story 2-3, re-test Story 2-2's complete workflow

### Git Intelligence

**Recent Relevant Commits:**
- `118b90b`: Socket.io rate limiting and security fixes (Story 1.3)
- Story 2-1: DeepSeek client with streaming support
- Story 2-2: CopywritingAgent workflow (but with emit_thought bug)

**Code Patterns Established:**
1. Use `async with` context managers for provider cleanup
2. Emit `agent:error` on any HTTPClientError
3. Include `workflow_id` in all event emissions
4. Use structured logging with `logger.debug/warning/error`

### Dependencies

**Required Dependencies** (from Story 1.x + 2-1 + 2-2):
```toml
[tool.poetry.dependencies]
python = "^3.11"
fastapi = "^0.104.0"
langgraph = "^0.0.20"
langchain = "^0.1.0"
python-socketio = "^5.10.0"
pydantic = "^2.5.0"
aiohttp = "^0.11.0"   # For HTTP client
```

### Testing Requirements

**Unit Test for SocketManager:**
```python
# tests/test_socket_manager.py
import pytest
from app.interface.ws.socket_manager import socket_manager

@pytest.mark.asyncio
async def test_emit_thought_with_node_name():
    """Test emit_thought includes node_name in payload."""
    # Mock the sio.emit method
    with patch.object(socket_manager.sio, 'emit') as mock_emit:
        await socket_manager.emit_thought(
            workflow_id="test-wf-id",
            content="Test thought",
            node_name="plan"
        )

        # Verify emit was called
        mock_emit.assert_called_once()
        call_args = mock_emit.call_args

        # Check payload structure
        payload = call_args[0][1]  # Second positional arg is payload
        assert payload["type"] == "thought"
        assert payload["workflowId"] == "test-wf-id"
        assert payload["data"]["content"] == "Test thought"
        assert payload["data"]["node_name"] == "plan"  # NEW: Verify node_name is included


@pytest.mark.asyncio
async def test_emit_thought_without_node_name():
    """Test emit_thought works when node_name is None (edge case)."""
    with patch.object(socket_manager.sio, 'emit') as mock_emit:
        await socket_manager.emit_thought(
            workflow_id="test-wf-id",
            content="Test without node_name"
            # node_name defaults to None
        )

        call_args = mock_emit.call_args
        payload = call_args[0][1]

        # node_name should NOT be in payload when None
        assert "node_name" not in payload["data"]
        assert payload["data"]["content"] == "Test without node_name"
```

**Integration Test for Streaming:**
```python
# tests/test_copywriting_agent_streaming.py
import pytest
from app.application.agents.copywriting_agent import CopywritingAgent
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_plan_node_streams_thoughts():
    """Test plan_node streams reasoning content in real-time."""
    agent = CopywritingAgent()

    # Mock socket_manager.emit_thought to capture events
    events = []
    async def mock_emit(workflow_id, content, node_name=None, sid=None):
        events.append({"workflow_id": workflow_id, "content": content, "node_name": node_name})

    with patch('app.application.agents.copywriting_agent.socket_manager.emit_thought', side_effect=mock_emit):
        # Mock provider to return streaming chunks
        mock_chunks = [
            StreamChunk(content="", reasoning_content="Analyzing product..."),
            StreamChunk(content="", reasoning_content="Creating outline..."),
            StreamChunk(content="Final plan text", reasoning_content=None, finish_reason="stop")
        ]

        with patch('app.core.factory.ProviderFactory.get_provider') as mock_factory:
            mock_provider = AsyncMock()
            mock_provider.__aenter__ = AsyncMock(return_value=mock_provider)
            mock_provider.__aexit__ = AsyncMock()
            mock_provider.generate_stream_with_callback = AsyncMock(
                return_value=GenerationResult(content="Final plan text", raw_response={})
            )

            async def capture_stream(request, callback):
                for chunk in mock_chunks:
                    await callback(chunk)

            mock_provider.generate_stream_with_callback.side_effect = capture_stream
            mock_factory.return_value = mock_provider

            # Run plan node
            state = {
                "product_name": "Test Product",
                "features": ["Feature 1"],
                "workflow_id": "test-wf-123",
                "current_stage": None,
                "plan": None,
                "draft": None,
                "critique": None,
                "final_copy": None,
                "brand_guidelines": None,
            }

            result = await agent.plan_node(state)

            # Verify events were emitted
            assert len(events) >= 3  # At least entry + streaming + completion
            assert events[0]["node_name"] == "plan"
            assert "Analyzing product" in events[1]["content"] or "Creating outline" in events[1]["content"]
```

### Error Handling Strategy

**Handle Streaming Failures with Rate-Limited Logging:**
```python
import time
from collections import defaultdict

class CopywritingAgent:
    # Class-level rate limiting for error logs
    _error_log_times = defaultdict(float)
    _ERROR_LOG_COOLDOWN = 5  # seconds between same error logs

    def _should_log_error(self, error_key: str) -> bool:
        """Check if enough time has passed since last error log."""
        now = time.time()
        if now - self._error_log_times[error_key] > self._ERROR_LOG_COOLDOWN:
            self._error_log_times[error_key] = now
            return True
        return False

async def _generate_with_streaming(
    self,
    prompt: str,
    workflow_id: str,
    node_name: str,
) -> str:
    """Generate text with streaming callback for real-time thought updates."""
    async def stream_callback(chunk: StreamChunk) -> None:
        """Callback for streaming chunks."""
        try:
            if chunk.reasoning_content:
                await socket_manager.emit_thought(
                    workflow_id=workflow_id,
                    content=chunk.reasoning_content,
                    node_name=node_name
                )
        except Exception as e:
            # Rate-limited logging to prevent log flooding
            error_key = f"emit_thought_{workflow_id}"
            if self._should_log_error(error_key):
                logger.warning(
                    f"Failed to emit thought for {node_name} (will suppress similar errors for 5s): {e}"
                )

    try:
        generator = ProviderFactory.get_provider("deepseek")
        async with generator:
            response = await generator.generate_stream_with_callback(
                request=GenerationRequest(
                    prompt=prompt,
                    model=self.model,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                ),
                callback=stream_callback,
            )
            return response.content
    except Exception as e:
        # Fallback to non-streaming if streaming fails
        logger.warning(f"Streaming failed for {node_name}, falling back to regular generation: {e}")
        return await self._generate(prompt, workflow_id)
```

### API Contract

**Socket.io Events:**

**Event: `agent:thought`**
```javascript
// Frontend listens for:
socket.on("agent:thought", (data) => {
  const nodeName = data.data.node_name || "general";  // Handle undefined node_name
  console.log(`[${nodeName}] ${data.data.content}`);
  // Display in UI categorized by node_name
});
```

**IMPORTANT:** Always use optional chaining or default value for `node_name` since it may be `undefined` for legacy compatibility.

**Event Flow Example:**
```
1. User submits copywriting request
2. Frontend receives workflow_id in response
3. Frontend listens for agent:thought events
4. Agent emits: {"node_name": "plan", "content": "正在为 Smart Watch 规划营销大纲..."}
5. Agent emits: {"node_name": "plan", "content": "Analyzing target audience..."} (from DeepSeek reasoning)
6. Agent emits: {"node_name": "plan", "content": "营销大纲创建完成"}
7. Agent emits: {"node_name": "draft", "content": "正在根据大纲撰写初稿..."}
... and so on for each stage
```

### References

**Source Documents:**
- [Source: _bmad-output/planning-artifacts/epics.md#Epic-2-Story-2.3](../../planning-artifacts/epics.md) - Epic 2 Story 2.3 requirements
- [Source: _bmad-output/planning-artifacts/architecture.md](../../planning-artifacts/architecture.md) - Socket.io event patterns
- [Source: _bmad-output/implementation-artifacts/2-2-copywriting-agent-workflow.md](./2-2-copywriting-agent-workflow.md) - Previous story with bug
- [Source: _bmad-output/implementation-artifacts/2-1-deepseek-client-implementation.md](./2-1-deepseek-client-implementation.md) - DeepSeek streaming

**Socket.io Documentation:**
- https://python-socketio.readthedocs.io/ - Python Socket.io reference

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

N/A

### Completion Notes List

**2026-01-23 Implementation Completed:**

1. **Fixed SocketManager.emit_thought()** - Added `node_name` optional parameter, payload now conditionally includes `node_name` in `data` section when provided
2. **Enhanced CopywritingAgent** - Added rate-limited error logging (5s cooldown), streaming fallback to non-streaming on failure
3. **Switched all nodes to streaming** - All 4 nodes (plan, draft, critique, finalize) now use `_generate_with_streaming()`
4. **Comprehensive test coverage** - 32 tests total, all passing:
   - `test_socket_manager.py`: 7 tests (node_name in/out, payload structure, error handling)
   - `test_copywriting_agent_streaming.py`: 13 tests (streaming, fallback, rate-limiting)
   - `test_copywriting_agent.py`: 12 tests (existing tests still pass)

### File List

**Files Modified:**
1. `backend/app/interface/ws/socket_manager.py` - Added `node_name` parameter to `emit_thought()`, updated docstring
2. `backend/app/application/agents/copywriting_agent.py` - Added `time`, `defaultdict` imports; added `_should_log_error()` method; enhanced `_generate_with_streaming()` with error handling and fallback; switched all nodes to use streaming

**Files Created:**
3. `backend/tests/interface/test_socket_manager.py` - 7 unit tests for `emit_thought()` with `node_name`
4. `backend/tests/application/agents/test_copywriting_agent_streaming.py` - 13 tests for streaming functionality

**Files Referenced (No Changes):**
1. `backend/app/domain/entities/agent_state.py` - CopywritingState entity
2. `backend/app/domain/entities/generation.py` - StreamChunk entity
3. `backend/app/core/factory.py` - ProviderFactory
4. `backend/app/infrastructure/generators/deepseek.py` - DeepSeekGenerator with streaming support

### Node Name Usage Convention

**IMPORTANT: Consistent node_name Usage**

To maintain consistency across the codebase, follow these conventions:

| Context | node_name Value | Example |
|---------|-----------------|---------|
| Plan node entry | `"plan"` | `node_name="plan"` |
| Draft node entry | `"draft"` | `node_name="draft"` |
| Critique node entry | `"critique"` | `node_name="critique"` |
| Finalize node entry | `"finalize"` | `node_name="finalize"` |
| DeepSeek reasoning content | Same as current node | `node_name="plan"` (during plan) |
| Generic thoughts (no specific node) | `None` or omit parameter | `node_name=None` |

**Content Formatting:**
- Do NOT include node name prefix in `content` field when `node_name` is provided
- Frontend will display: `[node_name] content` based on payload structure
- Example: `content="正在为 Smart Watch 规划营销大纲..."` (NOT `"[plan] 正在为..."`)

**Migration Note:**
Current code in copywriting_agent.py includes node name in content prefix (e.g., `"[plan] 正在为..."`). After fixing emit_thought() signature, consider removing these prefixes to avoid duplication in frontend display.
