# Source Tree Analysis

## Directory Structure

```
E_Business/
├── components/          # Reusable UI Components
│   ├── Login.tsx        # Auth entry point
│   ├── Editor.tsx       # Content editing interface
│   ├── GeminiResult.tsx # AI output display (with streaming simulation)
│   ├── Sidebar.tsx      # Navigation
│   └── ... (20+ components)
├── services/            # Business Logic & API Layer
│   └── geminiService.ts # Google Gemini SDK implementation
├── docs/                # Project Documentation (Empty/Placeholder)
├── App.tsx              # Main Application Component (Router/State)
├── main.tsx             # Entry Point (Vite)
└── README.md            # Setup instructions
```

## Critical Files

### Core Application
- **`App.tsx`**: Central hub. Manages `currentView` state (Router simulation), high-level state (`userMessage`, `result`), and API usage triggers (`handleGenerate`).
- **`services/geminiService.ts`**: The "Brain" of the current app.
    - Encapsulates `GoogleGenAI` client.
    - Manages `GenerationType` enum (`TEXT`, `IMAGE`, `VIDEO`, `SEARCH`).
    - Handles video polling logic for Veo models.

### Key Components
- **`GeminiResult.tsx`**: Handles the visualization of AI responses, including "thinking" states and loading animations.
- **`Sidebar.tsx`**: Main navigation controller.
- **`AssetDetail.tsx`**: Viewer for generated content.

## Integration Points
- **External**: Google Gemini API (via `geminiService.ts`).
- **Internal**: `App.tsx` passes callbacks (`onGenerate`, `onNavigate`) down to components.
