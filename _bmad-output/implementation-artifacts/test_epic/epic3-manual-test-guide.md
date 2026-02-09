# Epic 3 Manual Test Guide - Visual Content Studio

## Overview
This guide validates the functionality of the Image Generation feature (Epic 3), including the backend Agent, MCP Client integration, and Frontend UI.

## Prerequisites
- Backend running (`poetry run uvicorn app.main:app --reload`)
- Frontend running (`npm run dev`)
- DeepSeek API Key configured in `.env`
- MCP Server (or Mock) configured

## Test Scenarios

### 1. Frontend Integration (Story 3-3)

steps:
1. Open browser to `http://localhost:5173/image-generation` (or appropriate URL).
2. Verify page loads with:
   - Prompt input area.
   - Style selector (optional/if implemented).
   - "Generate" button.
3. Enter prompt: "A futuristic city with neon lights".
4. Select style: "Cyberpunk" (if available).
5. Click "Generate".
6. Observe:
   - "Thinking..." log appears.
   - Real-time updates of agent steps (Planning -> Generating).
   - Final image displayed.
7. Click on the image to view full size (if supported).

**Expected Result:**
- High-quality image generated.
- Thinking process visible.
- No console errors.

### 2. Backend Agent Logic (Story 3-1)

steps:
1. Use Swagger UI (`http://localhost:8000/docs`) or `curl`.
2. POST `/api/v1/images/generate` with:
   ```json
   {
    "prompt": "A cute cat",
    "style": "anime",
    "width": 1024,
    "height": 1024
   }
   ```
3. Verify response contains `workflow_id`.
4. Connect to WebSocket `/ws` and listen for `agent:thought`, `agent:result`.

**Expected Result:**
- API returns 200 OK.
- WebSocket receives progress events.
- Final `agent:result` contains image URL.

### 3. Error Handling

steps:
1. Disconnect internet or provide invalid API key (temporarily).
2. Attempt generation.
3. Observe UI error message.

**Expected Result:**
- Graceful error message displayed to user.
- System recovers after restoring connection.

## Notes
- Ensure `MinIO` is running if using real storage.
- Check backend logs for detailed error traces.
