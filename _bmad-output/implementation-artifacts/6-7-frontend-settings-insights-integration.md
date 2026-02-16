# Story 6.7: Frontend Settings & Insights Integration

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **User**,
I want **the Settings page to persist my preferences and the Insights page to display real performance data from the backend**,
so that **I can customize my AI experience and track the impact of my generated content.**

## Acceptance Criteria

### Settings Integration (Story 6-3 Backend)

1. **SettingsService API Client**:
    *   Create `services/settingsService.ts` with typed API methods.
    *   **GET /api/v1/user/settings**: Fetch user's AI preferences and integration status.
    *   **PATCH /api/v1/user/settings**: Update user settings (partial update supported).
    *   Use `localStorage.getItem('token')` for auth (consistent with `authService.ts`).

2. **Settings.tsx Real Data Integration**:
    *   Fetch settings on component mount with `useEffect`.
    *   Replace hardcoded state (`language`, `tone`, `aspectRatio`, `integrations`) with API data.
    *   Map backend response fields to frontend state:
        - `aiPreferences.language` → language dropdown
        - `aiPreferences.tone` → tone dropdown
        - `aiPreferences.aspectRatio` → aspect ratio radio buttons
        - `integrations.shopify/amazon/tiktok` → toggle switches
    *   Implement loading state (spinner/skeleton).
    *   Implement error handling with user-friendly toast/alert.

3. **Save Functionality**:
    *   Wire "Save Changes" button to call `settingsService.updateSettings()`.
    *   Send only changed fields (partial update).
    *   Show success/error toast after save attempt.
    *   Map frontend values to backend enum format:
        - Language: `"English (US)"` → `"en-US"`, etc.
        - Tone: `"Luxury & Sophisticated"` → `"luxury"`, etc.
        - Aspect Ratio: `"square"` → `"1:1"`, `"landscape"` → `"16:9"`, `"portrait"` → `"9:16"`

4. **Integration Toggles**:
    *   Toggle switches update local state immediately (optimistic UI).
    *   "Save Changes" persists all pending changes to backend.
    *   Connected status badges reflect `integrations.{platform}.connected` from API.

### Insights Integration (Story 6-4 Backend)

5. **InsightsService API Client**:
    *   Create `services/insightsService.ts` with typed API methods.
    *   **GET /api/v1/insights/stats**: Fetch KPI stat items array.
    *   **GET /api/v1/insights/charts?days=30**: Fetch time-series data for activity chart.
    *   **GET /api/v1/insights/top-assets?limit=5**: Fetch top performing assets.
    *   Use `localStorage.getItem('token')` for auth.

6. **Insights.tsx Real Data Integration**:
    *   Fetch stats, charts, and top-assets on component mount.
    *   Replace hardcoded `topAssets` array with API data.
    *   Replace hardcoded KPI stats array with API data.
    *   Implement loading state (skeleton cards during fetch).
    *   Implement error handling with retry option.

7. **Time Range Filtering**:
    *   Connect "Last 30 Days" dropdown to `days` query parameter.
    *   Options: 7, 14, 30, 60, 90 days.
    *   Re-fetch all data when time range changes.

8. **Data Mapping**:
    *   Stats: Map `StatItemDTO[]` directly to stats cards (label, value, trend, icon).
    *   Charts: Map `ChartPointDTO[]` to SVG chart (render real data points).
    *   Top Assets: Map `TopAssetDTO[]` to table rows with correct platform/type styling.

## Tasks / Subtasks

### Part A: Settings Integration

- [ ] **Shared Infrastructure** (New)
  - [ ] Create `services/apiClient.ts`:
    - [ ] Export `apiClient` axios instance with `baseURL` pointing to `/api/v1`.
    - [ ] Move auth interceptor (Token injection) from `authService.ts` to here.
    - [ ] Handle 401 errors globally (optional, nice to have).
  - [ ] Refactor `authService.ts` to use `apiClient`.

- [ ] **Settings Service Layer** (AC 1)
  - [ ] Create `services/settingsService.ts`.
  - [ ] Define TypeScript interfaces matching backend DTOs:
    - `AIPreferences`: `{ language: string, tone: string, aspectRatio: string }`
    - `IntegrationConfig`: `{ connected: boolean, storeName?: string, region?: string, accountName?: string }`
    - `UserSettings`: `{ aiPreferences: AIPreferences, integrations: { shopify, amazon, tiktok }, updatedAt: string }`
    - `UpdateSettingsRequest`: Partial nested structure for PATCH
  - [ ] Implement `getSettings(): Promise<UserSettings>`.
  - [ ] Implement `updateSettings(data: UpdateSettingsRequest): Promise<UserSettings>`.
  - [ ] Add auth token injection (reuse pattern from `authService.ts`).
  - [ ] Export singleton instance.

- [ ] **Settings Component Updates** (AC 2, 3, 4)
  - [ ] Import `settingsService` in `Settings.tsx`.
  - [ ] Add state: `settings`, `loading`, `error`, `hasChanges`.
  - [ ] Add `useEffect` to fetch settings on mount.
  - [ ] Implement field mapping helpers:
    - [ ] `mapBackendLanguageToFrontend(code: string): string`
    - [ ] `mapFrontendLanguageToBackend(label: string): string`
    - [ ] `mapBackendToneToFrontend(code: string): string`
    - [ ] `mapFrontendToneToBackend(label: string): string`
    - [ ] `mapBackendAspectRatioToFrontend(code: string): string`
    - [ ] `mapFrontendAspectRatioToBackend(id: string): string`
  - [ ] Replace hardcoded state with API data.
  - [ ] Track changes in local state (compare with original API data).
  - [ ] Wire "Save Changes" button to `settingsService.updateSettings()`.
  - [ ] Wire "Cancel" button to reset local state to original.
  - [ ] Add success/error toast notifications.
  - [ ] Add loading spinner during initial fetch.

### Part B: Insights Integration

- [ ] **Insights Service Layer** (AC 5)
  - [ ] Create `services/insightsService.ts`.
  - [ ] Define TypeScript interfaces matching backend DTOs:
    - `StatItem`: `{ label: string, value: string, trend: string, icon: string, highlight?: boolean }`
    - `ChartPoint`: `{ date: string, value: number }`
    - `TopAsset`: `{ id: string, name: string, created: string, platform: string, type: string, score: number, img?: string }`
    - `InsightsQueryParams`: `{ days?: number }`
  - [ ] Implement `getStats(): Promise<StatItem[]>`.
  - [ ] Implement `getCharts(days: number): Promise<ChartPoint[]>`.
  - [ ] Implement `getTopAssets(limit: number): Promise<TopAsset[]>`.
  - [ ] Add auth token injection (reuse pattern).
  - [ ] Export singleton instance.

- [ ] **Insights Component Updates** (AC 6, 7, 8)
  - [ ] Import `insightsService` in `Insights.tsx`.
  - [ ] Add state: `stats`, `chartData`, `topAssets`, `loading`, `error`, `timeRange`.
  - [ ] Create `fetchInsightsData(days: number)` function to fetch all three endpoints.
  - [ ] Add `useEffect` to fetch data on mount (default 30 days).
  - [ ] Replace hardcoded KPI stats array with API `stats` state.
  - [ ] Replace hardcoded `topAssets` with API `topAssets` state.
  - [ ] Update SVG chart to render real `chartData` (optional: use recharts library).
  - [ ] Wire time range dropdown to update `timeRange` state and re-fetch.
  - [ ] Add loading skeletons during fetch.
  - [ ] Add error state with retry button.
  - [ ] Ensure `id` type is `string` (UUID from backend, not number).

### Part C: Testing

- [ ] **Unit Tests** (All ACs)
  - [ ] Test `settingsService.getSettings()` with mock response.
  - [ ] Test `settingsService.updateSettings()` with mock request/response.
  - [ ] Test `insightsService.getStats()` with mock response.
  - [ ] Test `insightsService.getCharts()` with mock response.
  - [ ] Test `insightsService.getTopAssets()` with mock response.
  - [ ] Test field mapping helpers (language, tone, aspect ratio).

- [ ] **Component Tests** (All ACs)
  - [ ] Test Settings loading state renders skeleton.
  - [ ] Test Settings error state displays error message.
  - [ ] Test Settings save success shows success toast.
  - [ ] Test Insights loading state renders skeletons.
  - [ ] Test Insights time range change triggers re-fetch.

## Dev Notes

### Architecture Compliance

**Follow Existing Service Patterns**:
- Reuse axios configuration from `authService.ts` (uses `localStorage.getItem('token')`).
- API base URL: Use `import.meta.env.VITE_API_URL` or fallback to `http://localhost:8000/api/v1`.
- Create separate service files for Settings and Insights (single responsibility).

### Backend API Contracts

#### Settings API (from Story 6-3)

**GET /api/v1/user/settings**
- Auth: Required (Bearer Token)
- Response (camelCase):
```json
{
  "aiPreferences": {
    "language": "en-US",
    "tone": "professional",
    "aspectRatio": "1:1"
  },
  "integrations": {
    "shopify": { "connected": true, "storeName": "my-store.myshopify.com" },
    "amazon": { "connected": false },
    "tiktok": { "connected": false }
  },
  "updatedAt": "2026-02-13T10:30:00Z"
}
```

**PATCH /api/v1/user/settings**
- Auth: Required (Bearer Token)
- Request (partial update, snake_case internally but camelCase from frontend):
```json
{
  "aiPreferences": {
    "language": "zh-CN",
    "tone": "playful"
  }
}
```
- Response: 200 OK with updated full settings object.

#### Insights API (from Story 6-4)

**GET /api/v1/insights/stats**
- Auth: Required (Bearer Token)
- Response:
```json
[
  { "label": "Total Views", "value": "1.2M", "trend": "+12%", "icon": "visibility" },
  { "label": "Click-Through Rate", "value": "3.8%", "trend": "+0.5%", "icon": "ads_click" },
  { "label": "Conversion Rate", "value": "2.1%", "trend": "+0.1%", "icon": "shopping_cart" },
  { "label": "AI Efficiency Gain", "value": "40hrs Saved", "trend": "ROI +200%", "icon": "auto_awesome", "highlight": true }
]
```

**GET /api/v1/insights/charts?days=30**
- Auth: Required (Bearer Token)
- Query: `days` (int, default: 30, min: 7, max: 90)
- Response:
```json
[
  { "date": "2026-02-01", "value": 12 },
  { "date": "2026-02-02", "value": 8 },
  ...
]
```

**GET /api/v1/insights/top-assets?limit=5**
- Auth: Required (Bearer Token)
- Query: `limit` (int, default: 5, max: 10)
- Response:
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

### Value Mappings

**Language Mapping**:
| Frontend Label | Backend Code |
|----------------|--------------|
| English (US) | en-US |
| English (UK) | en-GB |
| Spanish | es-ES |
| French | fr-FR |
| German | de-DE |
| Chinese (Simplified) | zh-CN |
| Chinese (Traditional) | zh-TW |
| Japanese | ja-JP |
| Korean | ko-KR |

**Tone Mapping**:
| Frontend Label | Backend Code |
|----------------|--------------|
| Luxury & Sophisticated | luxury |
| Professional & Trustworthy | professional |
| Friendly & Approachable | casual |
| Witty & Playful | playful |
| Minimalist | minimal |

**Aspect Ratio Mapping**:
| Frontend ID | Backend Code |
|-------------|--------------|
| square | 1:1 |
| landscape | 16:9 |
| portrait | 9:16 |

### TypeScript Interface Definitions

```typescript
// services/settingsService.ts

export interface AIPreferences {
  language: string;
  tone: string;
  aspectRatio: string;
}

export interface IntegrationConfig {
  connected: boolean;
  storeName?: string;
  region?: string;
  accountName?: string;
}

export interface UserSettings {
  aiPreferences: AIPreferences;
  integrations: {
    shopify: IntegrationConfig;
    amazon: IntegrationConfig;
    tiktok: IntegrationConfig;
  };
  updatedAt: string;
}

export interface UpdateSettingsRequest {
  aiPreferences?: Partial<AIPreferences>;
  integrations?: {
    shopify?: Partial<IntegrationConfig>;
    amazon?: Partial<IntegrationConfig>;
    tiktok?: Partial<IntegrationConfig>;
  };
}

// services/insightsService.ts

export interface StatItem {
  label: string;
  value: string;
  trend: string;
  icon: string;
  highlight?: boolean;
}

export interface ChartPoint {
  date: string;
  value: number;
}

export interface TopAsset {
  id: string;
  name: string;
  created: string;
  platform: string;
  type: string;
  score: number;
  img?: string;
}

export interface InsightsQueryParams {
  days?: number;
  limit?: number;
}
```

### Service Implementation Pattern

**1. Shared Client (`services/apiClient.ts`)**:
```typescript
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

**2. Settings Service (`services/settingsService.ts`)**:
```typescript
import { apiClient } from './apiClient';

// ... interfaces ...

class SettingsService {
  async getSettings(): Promise<UserSettings> {
    const response = await apiClient.get<UserSettings>('/user/settings');
    return response.data;
  }

  async updateSettings(data: UpdateSettingsRequest): Promise<UserSettings> {
    const response = await apiClient.patch<UserSettings>('/user/settings', data);
    return response.data;
  }
}

export const settingsService = new SettingsService();
```

**3. Insights Service (`services/insightsService.ts`)**:
```typescript
import { apiClient } from './apiClient';

// ... interfaces ...

class InsightsService {
  async getStats(): Promise<StatItem[]> {
    const response = await apiClient.get<StatItem[]>('/insights/stats');
    return response.data;
  }

  async getCharts(days: number = 30): Promise<ChartPoint[]> {
    const response = await apiClient.get<ChartPoint[]>(`/insights/charts?days=${days}`);
    return response.data;
  }

  async getTopAssets(limit: number = 5): Promise<TopAsset[]> {
    const response = await apiClient.get<TopAsset[]>(`/insights/top-assets?limit=${limit}`);
    return response.data;
  }
}

export const insightsService = new InsightsService();
```

### Token Key Consistency

> [!IMPORTANT]
> **Use 'token'**: `authService.ts` uses `localStorage.getItem('token')`. This is the single source of truth.
> Ensure both `settingsService.ts` and `insightsService.ts` consistently use `localStorage.getItem('token')`.

### Project Structure Notes

**New Files to Create**:
```
services/
├── settingsService.ts      # API client for user settings
└── insightsService.ts      # API client for insights/analytics
```

**Files to Modify**:
```
components/
├── Settings.tsx            # Integrate real API data and save functionality
└── Insights.tsx            # Integrate real API data for stats, charts, assets
```

### Testing Standards

**Unit Tests**:
- Service methods: Mock axios responses, verify correct endpoints and auth headers
- Mapping helpers: Test all language/tone/aspect ratio conversions

**Component Tests**:
- Loading states: Verify skeleton/spinner renders during fetch
- Error states: Verify error message displays on API failure
- Success states: Verify toast notifications appear on save

### Dependencies

**Epic 1 (Auth)**: Completed
- User model and JWT authentication exist
- `get_current_user` dependency available
- Token stored as `'token'` in localStorage

**Epic 6 Stories 6-3 & 6-4**: Completed
- Backend APIs for settings and analytics are implemented and tested
- API contracts are documented in respective story files

### References

- [Story 6.3 - User Settings & Profile](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/6-3-user-settings-profile.md) - Backend API contracts
- [Story 6.4 - Analytics Service](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/6-4-analytics-service.md) - Backend API contracts
- [authService.ts](file:///f:/AAA Work/AIproject/E_Business/services/authService.ts) - Auth pattern reference
- [Settings.tsx](file:///f:/AAA Work/AIproject/E_Business/components/Settings.tsx) - Current component (mock data)
- [Insights.tsx](file:///f:/AAA Work/AIproject/E_Business/components/Insights.tsx) - Current component (mock data)
- [Architecture - Naming Conventions](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md#Naming-Patterns)

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2026-02-16: Story created by SM (Bob) in YOLO mode
  - Analyzed backend API contracts from Stories 6-3 and 6-4
  - Analyzed existing frontend components (Settings.tsx, Insights.tsx)
  - Analyzed existing service patterns (authService.ts)
  - Created comprehensive implementation guide with TypeScript interfaces and value mappings
  - Defined field mapping helpers for language, tone, and aspect ratio conversions
