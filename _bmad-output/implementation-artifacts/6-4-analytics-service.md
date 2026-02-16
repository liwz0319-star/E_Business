# Story 6.4: Analytics Service (Basic)

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **User**,
I want **to view insights and performance metrics (Statistics, Charts, Top Assets)**,
so that **I can track my usage, productivity, and the impact of my generated content.**

## Acceptance Criteria

1.  **API Endpoint - Get Stats (`GET /api/v1/insights/stats`)**:
    *   Returns array of KPI stat items for frontend "Summary Cards".
    *   **Response Format** (matches `Insights.tsx`):
        ```json
        [
          { "label": "Total Views", "value": "1.2M", "trend": "+12%", "icon": "visibility" },
          { "label": "Click-Through Rate", "value": "3.8%", "trend": "+0.5%", "icon": "ads_click" },
          { "label": "Conversion Rate", "value": "2.1%", "trend": "+0.1%", "icon": "shopping_cart" },
          { "label": "AI Efficiency Gain", "value": "40hrs Saved", "trend": "ROI +200%", "icon": "auto_awesome" }
        ]
        ```
    *   **Data Source Mapping**:
        - Total Views: `total_projects * random(100, 500)` (Mock)
        - CTR: `round(random.uniform(3.0, 5.0), 1)%` (Mock)
        - Conversion Rate: `round(random.uniform(1.5, 3.0), 1)%` (Mock)
        - AI Efficiency: `total_projects * random(5, 15)` hours saved (Mock)
    *   **Real Data Basis**: Total Projects (from `ProductPackageModel`), Total Assets (from `VideoAssetModel`) used as multipliers.

2.  **API Endpoint - Get Charts (`GET /api/v1/insights/charts`)**:
    *   Returns time-series data for the "Activity" chart.
    *   **Real Data**: Daily generation count over last 30 days (aggregated from `created_at` in DB).
    *   Response format: `[{ date: '2023-01-01', value: 12 }, ...]`
    *   **Date Filling**: Missing dates must be filled with `value: 0` for continuous chart display.
    *   Query parameter: `days` (default: 30, min: 7, max: 90).

3.  **API Endpoint - Get Top Assets (`GET /api/v1/insights/top-assets`)**:
    *   Returns a list of high-performing assets.
    *   **Hybrid**: Returns real assets definitions but injects mocked "performance score".
    *   **Response Format** (matches `Insights.tsx`):
        ```json
        [
          {
            "id": "uuid-string",
            "name": "Product Image 001",
            "created": "2026-02-13T10:00:00",
            "platform": "AI Generated",
            "type": "Product Image",
            "score": 95,
            "img": "https://example.com/asset.png"
          }
        ]
        ```
    *   Limit to top 5 (configurable via `limit` query param, max: 10).

4.  **Frontend Compatibility**:
    *   JSON responses MUST use `camelCase` keys.
    *   Structure must align with `components/Insights.tsx`.

## Tasks / Subtasks

- [x] **Domain Layer**:
    - [x] Create `app/domain/entities/analytics.py` (optional, DTOs may suffice for efficient aggregation).
    - [x] Define `KPIStats`, `ActivityData`, `TopAsset` pure data structures if complex logic needed.

- [x] **Application Layer**:
    - [x] Create `app/application/dtos/analytics_dtos.py`.
        - [x] `StatItemDTO`: `{ label: str, value: str, trend: str, icon: str, highlight?: bool }`
        - [x] `ChartPointDTO`: `{ date: str, value: int }`
        - [x] `TopAssetDTO`: `{ id: str, name: str, created: str, platform: str, type: str, score: int, img?: str }`
    - [x] Create `app/application/services/analytics_service.py`.
        - [x] Implement `get_stats(user_id)`: Aggregate counts + mock metrics calculation.
        - [x] Implement `get_charts(user_id, days=30)`: SQL aggregation + date filling.
        - [x] Implement `get_top_assets(user_id, limit=5)`: Fetch recent assets + mock scores.

- [x] **Infrastructure Layer**:
    - [x] Create `AnalyticsRepository` in `app/infrastructure/repositories/analytics_repository.py`.
        - [x] `count_projects(user_id)`: COUNT query on ProductPackageModel.
        - [x] `count_assets(user_id)`: COUNT query on VideoAssetModel.
        - [x] `get_daily_activity(user_id, days)`: GROUP BY date aggregation.
        - [x] `get_recent_assets(user_id, limit)`: Fetch top N recent assets.

- [x] **Interface Layer**:
    - [x] Create `app/interface/routes/insights.py`.
        - [x] `GET /api/v1/insights/stats` - Returns `List[StatItemDTO]`
        - [x] `GET /api/v1/insights/charts?days=30` - Returns `List[ChartPointDTO]`
        - [x] `GET /api/v1/insights/top-assets?limit=5` - Returns `List[TopAssetDTO]`
    - [x] Register router in `app/interface/routes/__init__.py` and `main.py`.

- [x] **Testing**:
    - [x] Create `tests/test_analytics_api.py`.
    - [x] `test_get_stats_success`: 验证返回 4 个 KPI 项，每项包含 label/value/trend/icon
    - [x] `test_get_stats_unauthorized`: 验证无 token 返回 401
    - [x] `test_get_charts_returns_30_days`: 验证返回 30 个数据点
    - [x] `test_get_charts_date_format`: 验证日期格式为 YYYY-MM-DD
    - [x] `test_get_charts_fills_missing_dates`: 验证空日期填充 0
    - [x] `test_get_top_assets_max_5`: 验证最多返回 5 条记录
    - [x] `test_get_top_assets_structure`: 验证包含 id/name/created/platform/type/score 字段

## Dev Notes

### Architecture Patterns

-   **Hybrid Data Source**: This story requires mixing **Real DB Aggregations** (COUNT, GROUP BY) with **Mock Business Logic**. Keep the separation clear.
    -   *Good*: `AnalyticsService` calls `repo.count_projects()` then adds `mock_views = random()`.
    -   *Bad*: Hardcoding everything.
-   **Analytics Repository**: Use `sqlalchemy.func` for efficient aggregation.
    -   `select(func.count(ProductPackageModel.id)).where(ProductPackageModel.user_id == user_id)`
    -   `select(func.date(created_at), func.count()).group_by(...)`
-   **DTO Conventions**: Pydantic v2 `alias_generator=to_camel` is MANDATORY.

### Mock Data Calculation (V1)

```python
import random
from datetime import datetime, timedelta

def calculate_mock_stats(total_projects: int, total_assets: int) -> list[dict]:
    """计算 Mock 统计数据"""
    # Total Views: 项目数 * 随机浏览量
    total_views = total_projects * random.randint(100, 500)
    if total_views >= 1_000_000:
        views_str = f"{total_views / 1_000_000:.1f}M"
    elif total_views >= 1_000:
        views_str = f"{total_views // 1_000}K"
    else:
        views_str = str(total_views)

    return [
        {
            "label": "Total Views",
            "value": views_str,
            "trend": f"+{random.randint(8, 15)}%",
            "icon": "visibility",
            "highlight": True,
        },
        {
            "label": "Click-Through Rate",
            "value": f"{round(random.uniform(3.0, 5.0), 1)}%",
            "trend": f"+{round(random.uniform(0.2, 0.8), 1)}%",
            "icon": "ads_click",
        },
        {
            "label": "Conversion Rate",
            "value": f"{round(random.uniform(1.5, 3.0), 1)}%",
            "trend": f"+{round(random.uniform(0.05, 0.2), 1)}%",
            "icon": "shopping_cart",
        },
        {
            "label": "AI Efficiency Gain",
            "value": f"{total_projects * random.randint(5, 15)}hrs Saved",
            "trend": f"ROI +{random.randint(150, 250)}%",
            "icon": "auto_awesome",
        },
    ]
```

### Chart Date Filling Strategy

确保 `/charts` API 返回连续 N 天数据：

```python
def fill_missing_dates(data: list[dict], days: int = 30) -> list[dict]:
    """确保返回连续N天的数据，缺失日期用 0 填充"""
    today = datetime.utcnow().date()
    date_map = {item['date']: item['value'] for item in data}
    result = []
    for i in range(days - 1, -1, -1):
        date = (today - timedelta(days=i)).isoformat()
        result.append({
            'date': date,
            'value': date_map.get(date, 0)
        })
    return result
```

### Asset Type Mapping

```python
TYPE_MAP = {
    'image': 'Product Image',
    'video': 'Ad Video',
    'text': 'Marketing Copy',
}
```

### Icon Mappings

```python
STAT_ICONS = {
    "views": "visibility",
    "ctr": "ads_click",
    "conversion": "shopping_cart",
    "efficiency": "auto_awesome",
}
```

### Project Structure Alignment

```
backend/app/
├── application/
│   ├── dtos/
│   │   └── analytics_dtos.py     # 新建
│   └── services/
│       └── analytics_service.py  # 新建
├── infrastructure/
│   └── repositories/
│       └── analytics_repository.py  # 新建
└── interface/
    └── routes/
        └── insights.py           # 新建
```

### DTO Definitions

```python
from pydantic import BaseModel, Field, ConfigDict
from pydantic.alias_generators import to_camel
from typing import Optional, List

class StatItemDTO(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    label: str
    value: str
    trend: str
    icon: str
    highlight: Optional[bool] = None

class ChartPointDTO(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    date: str  # YYYY-MM-DD format
    value: int

class TopAssetDTO(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    id: str
    name: str
    created: str
    platform: str
    type: str
    score: int
    img: Optional[str] = None
```

### References

-   [Epic 6 Requirements](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/epic-6-user-dashboard.md)
-   [Architecture Decision - Clean Architecture](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md)
-   [Story 6.1 - Project Management API](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/6-1-project-management-api.md) (Repository pattern reference)
-   [Story 6.2 - Asset Gallery API](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/6-2-asset-gallery-api.md) (DTO pattern reference)

## Dev Agent Record

### Agent Model Used

Claude (claude-3-5-sonnet)

### Debug Log References

N/A - Implementation completed without blocking issues.

### Completion Notes List

- **2026-02-14**: Story 6-4 Analytics Service implementation completed
  - Implemented hybrid data approach: real DB aggregations + mock metrics
  - Created 3 API endpoints: `/stats`, `/charts`, `/top-assets`
  - All 20 tests passing including authentication, validation, and response format tests
  - Followed existing repository and service patterns from Stories 6-1 and 6-2
  - DTOs use camelCase aliases for frontend compatibility

### File List

**New Files:**
- `backend/app/application/dtos/analytics_dtos.py` - DTOs for analytics responses
- `backend/app/application/services/analytics_service.py` - Analytics business logic
- `backend/app/infrastructure/repositories/analytics_repository.py` - Analytics data access
- `backend/app/interface/routes/insights.py` - API routes for insights endpoints
- `backend/tests/test_analytics_api.py` - Comprehensive test suite (20 tests)

**Modified Files:**
- `backend/app/interface/routes/__init__.py` - Added insights_router export
- `backend/app/main.py` - Registered insights_router with FastAPI app

## Change Log

- 2026-02-14: Story implementation completed
  - All tasks/subtasks completed with passing tests (20 tests)
  - Status updated to "review"
  - File List updated with all new and modified files
  - Dev Agent Record updated with completion notes

- 2026-02-13: Story updated based on review feedback
  - Updated AC1: Changed `/stats` response from object to array format matching frontend
  - Added explicit DTO definitions (StatItemDTO, ChartPointDTO, TopAssetDTO)
  - Added mock data calculation logic with specific formulas
  - Added chart date filling strategy
  - Added asset type and icon mappings
  - Refined test cases with specific assertions
