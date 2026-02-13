# Epic 6: User Dashboard & Asset Management

## Goal
Implement the backend infrastructure to support the "User Dashboard" modules: **Recent Projects**, **Gallery**, **Insights**, and **Settings**. These modules provide the management layer on top of the core AI generation capabilities.

## Scope

### 1. Project Management (Recent Projects)
- **Frontend Ref**: `components/Projects.tsx`
- **Goal**: Enable users to view, search, filter, and manage their generation projects (`ProductPackages`).
- **Requirements**:
  - List projects with pagination, sorting (Date), and filtering (Status, Type).
  - Search projects by title/keyword.
  - Delete and Duplicate project actions.
  - **Model Update**: Ensure `ProductPackageModel` has necessary fields (Title, Thumbnail URL derivation).

### 2. Asset Gallery (Gallery)
- **Frontend Ref**: `components/Gallery.tsx`
- **Goal**: specific view for individual assets (Images, Videos, Copywriting) independent of their project.
- **Requirements**:
  - Unified Query API for `VideoAsset` (Images/Videos) and `Copywriting` (Text).
  - Filter by Asset Type (Image, Video, Text).
  - Search by Prompt/Content.
  - Pagination and Infinite Scroll support.

### 3. Analytics & Insights (Insights)
- **Frontend Ref**: `components/Insights.tsx`
- **Goal**: Provide data visualization for usage and performance (Mock/Real hybrid).
- **Requirements**:
  - **Metrics**: Total Views, CTR, Conversion (Mock/Placeholder architecture for now).
  - **Charts**: Time-series data for activity.
  - **Top Assets**: Aggregation query.

### 4. User Settings (Settings)
- **Frontend Ref**: `components/Settings.tsx`
- **Goal**: Persist user preferences.
- **Requirements**:
  - Store "AI Preferences" (Language, Tone, Aspect Ratio).
  - Store "Integration Status" (Shopify, Amazon, TikTok).
  - API to GET and PATCH user profile/settings.

## Implementation Plan

### Story 6.1: Project Management API
- [ ] **Database**: Verify `ProductPackageModel` indexes for sorting/filtering.
- [ ] **API**: `GET /api/v1/projects` (List/Search/Filter).
- [ ] **API**: `DELETE /api/v1/projects/{id}`.
- [ ] **API**: `POST /api/v1/projects/{id}/duplicate`.

### Story 6.2: Asset Gallery API
- [ ] **Database**: Ensure `VideoAssetModel` has `user_id` index.
- [ ] **Database**: Create `CopywritingAssetModel` or defined storage strategy for text assets to be queryable.
- [ ] **API**: `GET /api/v1/assets` (Unified list with type filter).

### Story 6.3: User Settings & Profile
- [ ] **Database**: Create `UserSettingsModel` (One-to-One with User).
- [ ] **API**: `GET /api/v1/user/settings`.
- [ ] **API**: `PATCH /api/v1/user/settings`.


### Story 6.4: Analytics Service (Basic)
- [ ] **Database**: Create `AnalyticsEventModel` (optional for V1, maybe just stub endpoints).
- [ ] **API**: `GET /api/v1/insights/stats`.
- [ ] **API**: `GET /api/v1/insights/charts`.

## Part 2: Frontend Integration

### Story 6.5: Integrate Projects Page
- [ ] **Frontend**: Create `services/projectService.ts` (API Client).
- [ ] **Frontend**: Update `components/Projects.tsx` to fetch real data using `useQuery` or `useEffect`.
- [ ] **Frontend**: Wire up Delete/Duplicate actions to API.

### Story 6.6: Integrate Gallery Page
- [ ] **Frontend**: Create `services/assetService.ts` (API Client).
- [ ] **Frontend**: Update `components/Gallery.tsx` to fetch real assets.
- [ ] **Frontend**: Implement "Load More" (Infinite Scroll) logic.

### Story 6.7: Integrate Settings & Insights
- [ ] **Frontend**: Create `services/userService.ts` (Settings API).
- [ ] **Frontend**: Update `components/Settings.tsx` to load/save real preferences.
- [ ] **Frontend**: Update `components/Insights.tsx` to fetch stats from backend.

## Dependencies
- Epic 1 (Auth) - Required for User context.
- Epic 2/3 (Generation) - Source of data (Projects/Assets).
