# Story 2.4: Frontend Copywriting UI Integration

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **User**,
I want **to generate product copy via the frontend and see the AI thinking process in real-time**,
so that **I can verify the AI's reasoning and obtain high-quality marketing text**.

## Acceptance Criteria

1.  **Given** the user enters product requirements in the input box
2.  **When** they click "Generate" (for Text Generation)
3.  **Then** the frontend calls `POST /api/v1/copywriting/generate` instead of the mock service
4.  **And** the UI displays "Thinking..." states corresponding to the `agent:thought` events received via Socket.io
5.  **And** the specific `node_name` (Plan, Draft, Critique, Finalize) is visibly distinguished in the UI (e.g., logs or progress steps)
6.  **And** the final output from `agent:result` is displayed in the main result area
7.  **And** any `agent:error` events are handled gracefully with user-friendly error messages

## Tasks / Subtasks

- [x] **Task 1: Create Copywriting API Service** (AC: 1, 3)
  - [x] Subtask 1.1: Create `services/copywriting.ts` using the existing `apiClient` from `authService` (or refactor to shared client)
  - [x] Subtask 1.2: Implement `startGeneration(payload)` method calling `POST /api/v1/copywriting/generate` - **CRITICAL**: Payload must use snake_case to match backend DTO (`product_name`, `features`, `brand_guidelines`)
  - [x] Subtask 1.3: Ensure proper error handling and type definitions matching backend response (`workflowId`)

- [x] **Task 2: Implement WebSocket Thought Listener** (AC: 2, 4, 5)
  - [x] Subtask 2.1: In `App.tsx` (or a new `ThinkingStream` component), initialize `socket.io-client` connection using `io(import.meta.env.VITE_API_URL, { path: '/socket.io', auth: { token: ... } })`
  - [x] Subtask 2.2: Implement listeners for `agent:thought`, `agent:result`, `agent:error`
  - [x] Subtask 2.3: Create state to track the "Thinking Stream" (array of thought objects with node/content) including the `reasoning_content` from DeepSeek

- [x] **Task 3: Update UI Components** (AC: 1, 5, 6)
  - [x] Subtask 3.1: Modify `handleGenerate` in `App.tsx` to use `copywriting.ts` for TEXT generation type
  - [x] Subtask 3.2: Create a `ThoughtLog` or `ThinkingIndicator` component to visualize the stream events (Plan -> Draft -> ...)
  - [x] Subtask 3.3: Update `GeminiResult` (or create `AgentResult`) to render the final markdown content

- [x] **Task 4: Integration & Cleanup** (AC: 1, 4, 7)
  - [x] Subtask 4.1: Verify authentication token is passed in Socket.io handshake (Critical)
  - [x] Subtask 4.2: Ensure proper cleanup of socket listeners on component unmount
  - [x] Subtask 4.3: Add specific error handling for WebSocket connection failures
  - [x] Subtask 4.4: (Optional) Remove or disable legacy `geminiService` text generation paths - Kept as fallback

## Dev Notes

### Architecture Patterns
- **Frontend Service Pattern**: Use the same Axios instance/pattern as `authService.ts` (Bearer token injection).
- **Socket.io Pattern**:
    - URL: `${VITE_API_URL}` (base URL, NOT `/ws`)
    - Auth: `auth: { token: authService.getCurrentUserToken() }` in `io()` options.
    - Path: `/socket.io` (default path used by backend python-socketio)
- **Event Contracts** (UPDATED based on actual backend implementation):
    - `agent:thought`: `{ type: "thought", workflowId, data: { node_name?, content }, timestamp }`
    - `agent:result`: `{ type: "result", workflowId, data: { final_copy, ... }, timestamp }`
    - `agent:error`: `{ type: "error", workflowId, data: { code, message, details }, timestamp }`
    - `agent:tool_call`: `{ type: "tool_call", workflowId, data: { tool_name, status, message }, timestamp }` (Optional - for debugging)

### Backend DTO Field Mapping (IMPORTANT)
Backend uses **snake_case**, frontend must match:
```typescript
// Backend CopywritingRequest (snake_case)
interface CopywritingRequest {
    product_name: string;       // NOT productName
    features: string[];         // matches
    brand_guidelines?: string;  // NOT brandGuidelines
}

// Helper function to convert camelCase to snake_case
const toSnakeCase = (obj: any): any => {
    return Object.keys(obj).reduce((acc, key) => {
        const snakeKey = key.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
        acc[snakeKey] = obj[key];
        return acc;
    }, {});
};
```

### Source Tree Locations
- `services/copywriting.ts` [NEW]
- `types/api.ts` [UPDATE] - API DTO types
- `App.tsx` [MODIFY] - Main logic integration
- `components/ThinkingLog.tsx` [NEW] (Recommended for cleanliness)

### Learning from Story 1-5 (Frontend Auth)
- **Problem**: Hardcoded API URLs caused issues.
- **Fix**: MUST use `import.meta.env.VITE_API_URL` with a fallback.
- **Problem**: Token expiry not checked.
- **Fix**: Ensure `authService.isAuthenticated()` is checked before opening socket connection.

### References
- [Backend Copywriting Agent](file:///backend/app/application/agents/copywriting_agent.py)
- [Socket Manager](file:///backend/app/interface/ws/socket_manager.py)
- [Story 1-5 Auth Service](file:///services/authService.ts)

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5

### Completion Notes List
- Created to address missing frontend integration identified in retro.
- Bypasses "Done" status of Epic 2 by filling necessary gap.
- 2026-02-06: Implementation complete:
  - Created `copywriting.ts` with snake_case DTO, error handling
  - Created `webSocket.ts` with Socket.io connection, auto-reconnect, event filtering
  - Created `ThinkingLog.tsx` with Plan/Draft/Critique/Finalize visualization
  - Modified `App.tsx` to use backend API for TEXT generation with real-time thinking stream
  - TypeScript compilation passes with no errors
  - Legacy geminiService kept as fallback for non-TEXT types and error recovery

---

## File List

### New Files
- `services/copywriting.ts` - Copywriting API service with snake_case DTO support
- `services/webSocket.ts` - WebSocket service for Socket.io agent events
- `components/ThinkingLog.tsx` - AI thinking process visualization component
- `services/copywriting.test.ts` - Unit tests for copywriting service (TEST-001 Fix)
- `services/webSocket.test.ts` - Unit tests for WebSocket service (TEST-001 Fix)
- `components/ThinkingLog.test.tsx` - Unit tests for ThinkingLog component (TEST-001 Fix)

### Modified Files
- `App.tsx` - Integrated WebSocket and copywriting service for TEXT generation
- `services/authService.ts` - Authentication service (dependency, created in Story 1-5)

---

## Change Log

- 2026-02-06: Story 2-4 implementation complete. All tasks finished.
- 2026-02-07: Code review fixes applied (ARCH-001, AC-001, ERROR-001, MEMORY-001, TEST-001)

---

