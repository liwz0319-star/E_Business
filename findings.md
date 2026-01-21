# Findings & Decisions
<!--
  WHAT: Your knowledge base for the task. Stores everything you discover and decide.
  WHY: Context windows are limited. This file is your "external memory" - persistent and unlimited.
  WHEN: Update after ANY discovery, especially after 2 view/browser/search operations (2-Action Rule).
-->

## Requirements
<!-- What the CommerceAI Assistant needs to do -->
Based on the project structure and documentation:

- **Multi-modal Content Generation**
  - Text: Product descriptions, marketing copy, ad content
  - Image: Product photos, marketing visuals (16:9 aspect ratio)
  - Video: Product showcase videos (async generation with polling)
  - Search: Market insights and trend analysis

- **Frontend Features**
  - Image editor for modifying generated images
  - User login and authentication
  - User profile management
  - Notification system for async operations (video generation)

- **Backend Services**
  - Gemini API integration
  - Video polling mechanism
  - Blob URL generation for video downloads

---

## Research Findings
<!-- Key discoveries during exploration -->
- **Google Gemini Models Used:**
  - `gemini-3-flash-preview`: Text generation and search
  - `gemini-2.5-flash-image`: Image generation (16:9 ratio)
  - `veo-3.1-fast-generate-preview`: Video generation (async, requires polling)

- **Video Generation Flow:**
  - Submit request → Get Operation object
  - Poll every ~10 seconds for status
  - When complete, get download link
  - Fetch video blob and create object URL

- **Architecture Pattern:**
  - Service-based architecture with `geminiService.ts`
  - Component-based React frontend
  - Separate backend directory for server-side logic

---

## Technical Decisions
| Decision | Rationale |
|----------|-----------|
| Base64 encoding for images | Easy storage and display, no separate file server needed |
| Blob URLs for videos | Temporary storage, no need for persistent video hosting |
| Async polling for video status | Gemini API doesn't return video immediately |
| System instruction for text | Ensures consistent e-commerce copywriting style |
| 16:9 aspect ratio for images | Standard for e-commerce product photos |

---

## Issues Encountered
| Issue | Resolution |
|-------|------------|
| | |

---

## Resources
<!-- URLs, file paths, API references -->
- **Project Documentation:**
  - Business flow: `业务流程图.md`
  - Agent design: `agent_design_structure.md`
  - AI Studio: https://ai.studio/apps/drive/1endc82X65sUG5nEnxaUEw4ccD98Qd1uM

- **Key Files:**
  - Main service: `services/geminiService.ts`
  - App entry: `App.tsx`
  - Config: `vite.config.ts`, `tsconfig.json`
  - Environment: `.env.example`

- **API Documentation:**
  - Google Gemini AI: https://ai.google.dev/
  - @google/genai SDK: npm package

---

## Visual/Browser Findings
<!-- CRITICAL: Update after every 2 view/browser operations -->
<!-- Multimodal content must be captured as text immediately -->
- Project structure shows:
  - Frontend: React app in root directory
  - Backend: Separate `backend/` folder
  - Documentation: Chinese and English markdown files
  - Agent-related directories: `.agent/`, `.bmad/`, `.bmad-output/`

---

## Architecture Notes

### Current Structure
```
E_Business/
├── App.tsx              # Main React component
├── services/            # Service layer
│   └── geminiService.ts # Gemini API integration
├── components/          # React components
├── backend/             # Backend services
├── 业务流程图.md         # Business flow docs (Chinese)
└── agent_design_structure.md
```

### Service Architecture
`geminiService.ts` handles:
- `generateContent(prompt, type)` - Main generation method
- Type parameter: TEXT | IMAGE | VIDEO | SEARCH
- System instruction for consistent copywriting style
- Async video polling mechanism

---
<!-- REMINDER: The 2-Action Rule -->
*Update this file after every 2 view/browser/search operations*
*This prevents visual information from being lost*
