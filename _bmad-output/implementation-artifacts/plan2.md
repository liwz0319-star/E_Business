# Plan 2: DeepSeek API Key Fix & E2E Verification

**Status:** Phase 7 Completed
**Date:** 2026-02-09

## 1. Current Situation
- **Issue:** Async copywriting workflow fails with "DeepSeek API key is required".
- **Findings:**
  - Standard API calls work (Sync context).
  - Background tasks fail (Async context).
  - **Critical Discovery (Phase 6/7):** `os.getenv('DEEPSEEK_API_KEY')` returns `None` in the running backend process, even when `.env` is read by Pydantic.

## 2. Progress Overview

| Phase | Description | Status |
|-------|-------------|--------|
| **Phase 1** | Initial Diagnosis & Environment Cleanup | ✅ Completed |
| **Phase 2** | Fix Config Caching | ✅ Completed (`@lru_cache` removed) |
| **Phase 3** | Fix .env Path Resolution | ✅ Completed (Absolute paths in `config.py`) |
| **Phase 4** | Priority Loading in `deepseek.py` | ✅ Completed (Check `os.getenv` first) |
| **Phase 5** | Dynamic Settings Loading | ✅ Completed (Avoid global `settings` in async agents) |
| **Phase 6** | System Restart & Verification | ✅ Completed (Identified `os.environ` missing) |

## 3. Detailed Root Cause Analysis
The application uses `pydantic-settings` to load configuration. While this correctly populates the `Settings` object, it **does not** automatically set system-level environment variables (`os.environ`).

The `DeepSeekGenerator` (and specifically its initialization logic in async workers) attempts to read from `os.getenv` as a fallback or primary source (Priority #2 in our fix). Since `os.environ` is empty of these keys, this lookup fails. If the `settings` object passed to the async thread is relying on global state that isn't perfectly propagated, the whole configuration fails.

**Conclusion:** We must ensure `.env` variables are promoted to real OS environment variables at application startup.

## 4. Phase 7 Plan: System Environment Variable Fix

### Goal
Ensure `.env` variables are loaded into `os.environ` at application startup so they are globally available to all threads, processes, and libraries.

### Implementation Steps
1.  [x] **Modify `backend/app/main.py`**:
    -   In the `lifespan` startup event, explicitly read the `.env` file and update `os.environ`.
2.  [x] **Restart Backend / Runtime Verification**:
    -   Verify `os.getenv('DEEPSEEK_API_KEY')` returns the correct key.
3.  [x] **Final Verification**:
    -   Run the copywriting E2E workflow.
    -   Verify success (no "API key required" error).

### Verification Command
```bash
# Verify env var is set
poetry run python -c "import os; print(os.getenv('DEEPSEEK_API_KEY'))"
```

### Completion Notes (2026-02-09)
- `backend/app/main.py` now uses stable `__file__`-based `.env` lookup and promotes keys to `os.environ` via `_promote_env_to_os_environ()`.
- Startup validation now refreshes runtime settings after `.env` promotion.
- Added regression tests: `backend/tests/test_main_startup_env.py`.
- Stabilized existing test for env-dependent behavior:
  - `backend/tests/test_deepseek_generator.py` now explicitly clears `DEEPSEEK_API_KEY` in `test_init_without_api_key_raises`.
- Validation results:
  - `poetry run pytest -q tests/test_main_startup_env.py tests/test_deepseek_generator.py` -> `24 passed`
  - `poetry run pytest -q tests/interface/routes/test_copywriting.py` -> `9 passed`
  - `poetry run python -c "import os; from app.main import _promote_env_to_os_environ; _promote_env_to_os_environ(); print('DEEPSEEK_API_KEY set:', bool(os.getenv('DEEPSEEK_API_KEY')))"` -> `True`
