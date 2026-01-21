# Story 1.1: Backend Project Initialization

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a developer,
I want to initialize the FastAPI project structure with Docker and Poetry,
So that I have a consistent, runnable environment for development.

## Acceptance Criteria

1. **Given** a clean git branch
   **When** I execute `poetry install` and `docker-compose up -d --build`
   **Then** a `backend` directory is created with `app`, `tests` folders

2. **And** `pyproject.toml` includes fastapi, uvicorn, sqlalchemy, asyncpg, python-socketio dependencies

3. **And** `docker-compose.yml` successfully spins up `api`, `db`, and `redis` containers

4. **And** accessing `http://localhost:8000/health` returns 200 OK

## Tasks / Subtasks

- [x] Initialize Python Project (AC 1, 2)
  - [x] Create `backend` directory
  - [x] Initialize `poetry` project (Python 3.11)
  - [x] Add dependencies: `fastapi`, `uvicorn`, `sqlalchemy`, `asyncpg`, `python-socketio`, `pydantic-settings`, `alembic`
  - [x] Add dev dependencies: `pytest`, `pytest-asyncio`, `httpx`
- [x] Implement Project Structure (Clean Architecture) (AC 1)
  - [x] Create `app/domain` (Entities, Interfaces)
  - [x] Create `app/application` (Use Cases)
  - [x] Create `app/infrastructure` (implementations)
  - [x] Create `app/interface` (API routers)
  - [x] Create `app/main.py` entrypoint
- [x] Docker Setup (AC 3)
  - [x] Create `Dockerfile` for backend (Multi-stage build)
  - [x] Create/Update `docker-compose.yml` (Postgres 16 + pgvector, Redis, Minio, Backend)
- [x] Health Check Endpoint (AC 4)
  - [x] Implement `GET /health` in `app/main.py` (or interface layer)
- [x] Initialize Alembic for Database Migrations (AC 1, 2)
  - [x] Run `alembic init alembic` in backend directory
  - [x] Configure `alembic.ini` with database connection URL
  - [x] Create `backend/app/alembic/env.py` with async SQLAlchemy setup
  - [x] Create initial migration template
- [x] Create Configuration Templates (AC 1, 2)
  - [x] Create `.env.example` with required environment variables:
    - `DATABASE_URL` (PostgreSQL connection)
    - `REDIS_URL` (Redis connection)
    - `SECRET_KEY` (JWT signing)
    - `DEEPSEEK_API_KEY` (AI provider)
  - [x] Create `backend/app/core/config.py` using pydantic-settings
  - [x] Document environment variable requirements in Dev Notes
- [x] Create Project Documentation (AC 1)
  - [x] Create `backend/README.md` with:
    - Project overview and tech stack
    - Prerequisites (Docker, Poetry)
    - Quick start commands
    - Development setup instructions
    - Environment variable configuration guide
    - Running tests
  - [x] Add troubleshooting section for common issues

## Dev Notes

- **Architecture Compliance**:
  - Follow **Pragmatic Clean Architecture**:
    - `domain/`: Pure python, no external dependencies (except pydantic).
    - `application/`: Orchestration logic, depends on domain.
    - `infrastructure/`: DB, External APIs, depends on application/domain.
    - `interface/`: FastAPI routers, depends on application.
  - **Tooling**: Use `poetry` for dependency management.
  - **Database**: Use `pgvector/pgvector:phgc` image for Postgres to support future RAG.

### Project Structure Notes

- Ensure `backend/` is the root for python code.
- `docker-compose.yml` should be at project root (parent of `backend/`).

### References

- [Architecture Decision](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md#Implementation-Patterns)
- [Epics Source](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/epics.md#Story-1.1:-Backend-Project-Initialization)

## Dev Agent Record

### Agent Model Used

Antigravity (BMad Master)

### Debug Log References

### Completion Notes List

- Implemented standard FastAPI structure (Domain/App/Infra/Interface).
- Configured Poetry with required dependencies.
- Created Backend Dockerfile and root docker-compose.yml.
- Initialized Alembic with async SQLAlchemy configuration.
- Created configuration templates (.env.example, config.py).
- Created project README with setup instructions.
- Verified Health Check `GET /health` returns 200 OK via pytest.
- Verified full stack: Docker containers (api, db, redis) all healthy.
- Verified database connection pool initialized successfully.
- Verified Redis connection established.

### File List

- backend/pyproject.toml
- backend/Dockerfile
- docker-compose.yml
- backend/alembic.ini
- backend/app/alembic/env.py
- backend/app/alembic/script.py.mako
- .env.example
- backend/app/core/config.py
- backend/app/main.py
- backend/app/domain/__init__.py
- backend/app/application/__init__.py
- backend/app/infrastructure/__init__.py
- backend/app/interface/__init__.py
- backend/README.md
- backend/tests/test_health.py
