# Code Review Report - Story 6-4 (Analytics) + Uncommitted Workspace

Date: 2026-02-16  
Reviewer: Codex (CR lane)

## Scope

- Story baseline: `_bmad-output/implementation-artifacts/6-4-analytics-service.md`
- Reviewed files:
  - `backend/app/application/dtos/analytics_dtos.py`
  - `backend/app/application/services/analytics_service.py`
  - `backend/app/infrastructure/repositories/analytics_repository.py`
  - `backend/app/interface/routes/insights.py`
  - `backend/app/interface/routes/__init__.py`
  - `backend/app/main.py`
  - `backend/tests/test_analytics_api.py`
- Plus all uncommitted workspace changes for cross-story risk visibility (including `user_settings` changes).

## Validation Commands

Executed:

```bash
cd backend && poetry run pytest -q tests/test_analytics_api.py tests/test_user_settings_api.py tests/test_user_settings_service.py tests/test_user_settings_repository.py tests/test_user_settings_model.py
```

Result: `56 passed, 1 warning`

Executed:

```bash
cd backend && poetry run pytest -q
```

Result: `25 failed, 10 errors` (global suite currently red)

## Findings

### HIGH-1: AC mapping mismatch (`total_assets` not used)

- Story AC requires real basis from both projects and assets:
  - `_bmad-output/implementation-artifacts/6-4-analytics-service.md:31`
- Implementation reads `total_assets` but does not use it in KPI formulas:
  - `backend/app/application/services/analytics_service.py:54`
  - `backend/app/application/services/analytics_service.py:119`

Impact:
- AC1 data-source mapping is only partially implemented.

Recommendation:
- Include `total_assets` in at least one KPI formula and add deterministic assertions.

---

### HIGH-2: `top-assets` contract mismatch with current frontend behavior

- Backend outputs:
  - `platform="AI Generated"`: `backend/app/application/services/analytics_service.py:109`
  - `type` values from `TYPE_MAP`: `backend/app/application/services/analytics_service.py:16`
- Current frontend `Insights` logic expects different enums:
  - platform branching: `components/Insights.tsx:242`
  - type branching: `components/Insights.tsx:249`

Impact:
- UI icon/style logic can break once frontend switches to API-backed data.

Recommendation:
- Align backend enum values with frontend contract, or add explicit mapping adapter and contract tests.

---

### HIGH-3: Global quality gate red

- Full suite result: `25 failed, 10 errors` from `cd backend && poetry run pytest -q`.

Impact:
- Cannot claim release-safe state for integrated branch.

Recommendation:
- Classify failures into baseline vs newly introduced; enforce merge rule on selected gate set.

## MEDIUM Findings

### MEDIUM-1: `/charts` date window and SQL indexability concerns

- Query uses date-truncation in filter/group:
  - `backend/app/infrastructure/repositories/analytics_repository.py:87`
  - `backend/app/infrastructure/repositories/analytics_repository.py:93`
  - `backend/app/infrastructure/repositories/analytics_repository.py:96`
- Fill logic uses `days-1..0` loop:
  - `backend/app/application/services/analytics_service.py:191`

Impact:
- Potential off-by-one boundary and poorer index utilization.

Recommendation:
- Query with timestamp range (`>= start_dt`, `< end_dt`) and keep fill window exactly consistent.

---

### MEDIUM-2: AC-critical assertions are too weak

- Tests verify structure and basic status but not full formula semantics:
  - `backend/tests/test_analytics_api.py:95`
  - `backend/tests/test_analytics_api.py:137`
  - `backend/tests/test_analytics_api.py:347`

Impact:
- Business-rule drift may pass unnoticed.

Recommendation:
- Mock/freeze randomness and add exact formula/value assertions for AC1/AC3.

---

### MEDIUM-3: Story file list vs workspace reality divergence

- Story 6-4 file list is narrow:
  - `_bmad-output/implementation-artifacts/6-4-analytics-service.md:280`
- Actual uncommitted workspace includes many cross-story files (`user_settings`, migration, etc.).

Impact:
- Review traceability and change attribution are weaker.

Recommendation:
- Split commits by story scope or explicitly record mixed-scope changes in story docs.

## LOW Findings

### LOW-1: Minor maintainability cleanup

- Unused imports in insights route:
  - `backend/app/interface/routes/insights.py:8`
  - `backend/app/interface/routes/insights.py:10`

Recommendation:
- Remove unused imports to reduce lint noise.

## Conclusion

- Story 6-4 core API subset is functional (`analytics` and `user_settings` target suites pass together).
- However, full backend regression is red, and there are contract/AC consistency issues to address before considering branch-level completion.
