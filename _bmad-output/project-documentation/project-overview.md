# Project Overview: CommerceAI Assistant (E_Business)

## Executive Summary
CommerceAI Assistant is a React-based e-commerce content generation tool that leverages Google's Gemini models (Multimodal AI) to generate:
- **Product Copy**: High-converting text descriptions.
- **Product Images**: Studio-quality visual assets.
- **Marketing Videos**: 15s social media video ads using Veo.
- **Market Insights**: Search-grounded competitive analysis.

The current implementation is a **Client-Side SPA** (Single Page Application) built with Vite, interacting directly with Google APIs. The next phase involves migrating logic to a Python/FastAPI backend to support complex agentic workflows (LangChain Deep Agents).

## Technology Stack

| Category | Technology | Version | Justification |
|/---|---|---|---|
| **Frontend Framework** | React | 19.x | Modern UI library with concurrent features |
| **Build Tool** | Vite | 6.x | Fast development server and build tool |
| **Language** | TypeScript | 5.8 | Type safety for complex state management |
| **AI SDK** | @google/genai | 1.x | Direct access to Gemini 1.5/2.0/Veo models |
| **Styling** | Tailwind CSS * | (Inferred from class names) | Utility-first styling |
| **Icons** | Material Icons | - | UI consistency |

*\*Note: Tailwind usage inferred from codebase patterns (e.g., `bg-slate-100`, `text-primary`).*

## Architecture Pattern
**Current:** **Monolithic Client-Side Application**
- **Logic**: All generation logic resides in `services/geminiService.ts`.
- **State**: React `useState` and Context (implicit).
- **Communication**: Direct REST/RPC calls to Google Cloud from the browser.

**Target (Backend Dev):** **Client-Server Architecture**
- **Frontend**: React (UI only)
- **Backend**: FastAPI (Agent Orchestration, API Proxy)
- **Protocol**: WebSocket/SSE for streaming agent thoughts.

## Repository Structure
- **Type**: Monolith (Frontend-focused)
- **Root**: `f:\AAA Work\AIproject\E_Business`
