# Repository Guidelines

## Project Structure & Module Organization
- Frontend code lives at the repository root: `App.tsx`, `index.tsx`, UI in `components/`, business logic in `services/`, shared helpers in `utils/`, and hooks in `hooks/`.
- Frontend build config is in `vite.config.ts`, `vitest.config.ts`, and `tsconfig.json`.
- Backend code is in `backend/app/`, organized by Clean Architecture layers: `domain/`, `application/`, `infrastructure/`, `interface/`, and `core/`.
- Backend tests are in `backend/tests/` and mirror application layers (`application/`, `interface/`, `domain/`, `infrastructure/`, `e2e/`).
- `docker-compose.yml` orchestrates the local stack (API, PostgreSQL/pgvector, Redis, MinIO).

## Build, Test, and Development Commands
- `npm install` installs frontend dependencies.
- `npm run dev` starts the Vite frontend locally.
- `npm run build` creates a production bundle in `dist/`.
- `npm run test` runs Vitest in watch mode; `npm run test:run` runs once.
- `cd backend && poetry install` installs backend dependencies.
- `cd backend && poetry run uvicorn app.main:app --reload --port 8000` runs the FastAPI service.
- `cd backend && poetry run pytest -q` runs backend tests.
- `docker-compose up -d --build` starts the full local infrastructure.

## Coding Style & Naming Conventions
- TypeScript/React: 2-space indentation, single quotes, `PascalCase` for components (for example `UserProfileModal.tsx`), `camelCase` for functions/variables.
- Python: PEP 8 with 4-space indentation, `snake_case` modules/functions, and type hints for new/changed code.
- Keep backend boundaries strict: avoid coupling `domain` logic to transport or storage layers.

## Testing Guidelines
- Frontend tests use Vitest + Testing Library and follow `*.test.ts` / `*.test.tsx` naming near related code (for example `services/webSocket.test.ts`).
- Backend tests use Pytest and follow `test_*.py` naming under `backend/tests/`.
- For feature changes, add or update tests in the impacted layer and run both frontend and backend suites before opening a PR.

## Commit & Pull Request Guidelines
- Prefer Conventional Commit style used in history (`feat: ...`, `fix(scope): ...`).
- Keep commits focused and descriptive; avoid mixing unrelated frontend/backend changes.
- PRs should include a concise summary, linked issue/story, test commands and results, and screenshots or sample API payloads for behavior/UI changes.

## Security & Configuration Tips
- Do not commit secrets; use `.env.example` as the baseline for new variables.
- Validate auth, CORS, and external API key changes with integration tests before merge.
