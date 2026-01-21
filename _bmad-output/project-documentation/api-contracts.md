# API Contracts (External)

The application currently consumes external APIs directly. This document outlines the external dependencies that will likely be proxied or managed by the new Backend.

## Google Gemini API
**Client**: `@google/genai`
**Location**: `services/geminiService.ts`

### 1. Generate Content (Text/Search)
- **Model**: `gemini-3-flash-preview`
- **Input**: Prompt String, System Instruction ("You are a world-class e-commerce copywriter...")
- **Tools**: `googleSearch` (for Market Insight type)
- **Output**: Text Response

### 2. Generate Image
- **Model**: `gemini-2.5-flash-image`
- **Input**: Prompt String
- **Config**: `aspectRatio: "16:9"`
- **Output**: Base64 Data URI (`data:image/png;base64,...`)

### 3. Generate Video
- **Model**: `veo-3.1-fast-generate-preview`
- **Input**: Prompt String
- **Config**: `resolution: '720p'`, `aspectRatio: '16:9'`
- **Process**:
    1. Call `generateVideos` -> Returns Operation ID.
    2. Poll `getVideosOperation` every 10s until `done`.
    3. Fetch `video.uri` with API key.
    4. Convert Blob to ObjectURL.
- **Output**: Local Blob URL.

---

## Future Backend API Requirements
To support the migration, the Backend must expose endpoints that replace these direct calls, likely:

- `POST /api/generate/text`
- `POST /api/generate/image`
- `POST /api/generate/video` (Async/WebSocket for progress)
