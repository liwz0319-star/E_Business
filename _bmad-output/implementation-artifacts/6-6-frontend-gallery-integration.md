# Story 6.6: Integrate Gallery Page

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **User**,
I want **to view my generated assets in the Gallery page**,
so that **I can browse, filter, search, and manage all my creations in one place.**

## Acceptance Criteria

1.  **Real Data Integration**:
    *   The Gallery page fetches data from `GET /api/v1/assets`.
    *   It displays Images, Videos, and Copywriting assets using the `GalleryAssetDTO` structure.
    *   Mock data is completely removed.

2.  **Filtering & Search**:
    *   **Tab Switching**: Clicking "Product Images", "Ad Videos", or "Marketing Copy" tabs passes the correct `type` parameter (`image`, `video`, `text`) to the API.
    *   **"All" Tab**: When "All" is selected, no `type` parameter is sent, returning assets of all types.
    *   **Type Mapping**: Frontend maps UI categories to API types:
        - "All" → undefined (no type param)
        - "Product Images" → "image"
        - "Ad Videos" → "video"
        - "Marketing Copy" → "text"
    *   **Search**: Typing in the search bar sends the `q` parameter to the API. Debounce implemented (500ms).

3.  **Infinite Scroll / Pagination**:
    *   Initial load fetches the first 20 items.
    *   Scrolling to the bottom triggers fetching the next page (`page=2`, etc.).
    *   Loading skeletons/spinners are shown while fetching.
    *   "No more items" state handled gracefully.

4.  **Asset Management**:
    *   **Delete**:
        - Clicking delete on an asset shows a confirmation dialog.
        - Confirming calls `DELETE /api/v1/assets/{id}`.
        - Asset is removed from the UI (optimistic update or refetch).
    *   **Edit Title**: (Optional, if UI supports) Updating title calls `PATCH /api/v1/assets/{id}`.

5.  **Data Mapping**:
    *   Backend `GalleryAssetDTO` fields map correctly to Frontend UI components.
    *   `isVertical`, `isText`, `meta`, `tag` fields from API are used for layout/rendering.
    *   Text assets display their `content` preview; Image/Video assets use `url` for thumbnails.

6.  **Error Handling**:
    *   API errors display user-friendly error messages.
    *   Network failures show retry option.
    *   Authentication errors redirect to login.

7.  **Empty State**:
    *   First-time users (no assets) see a "Generate your first asset" CTA.
    *   Search with no results shows helpful message.

## Tasks / Subtasks

- [ ] **Frontend Types & Interfaces**:
    - [ ] Create `src/types/asset.ts`:
        - [ ] `GalleryAsset` interface (id: string, title, type, tag, meta, url, content, isVertical, isText, duration, createdAt)
        - [ ] `AssetListResponse` interface (items, total, page, limit, pages)
        - [ ] `AssetQueryParams` interface (type?, q?, page?, limit?)
    - [ ] Create `TAB_TO_API_TYPE` mapping constant in `utils/assetUtils.ts`

- [ ] **Frontend Service Layer**:
    - [ ] Create `services/assetService.ts`:
        - [ ] `getAssets(params: AssetQueryParams): Promise<AssetListResponse>`
        - [ ] `deleteAsset(id: string): Promise<void>`
        - [ ] `updateAsset(id: string, data: { title: string }): Promise<GalleryAsset>`
    - [ ] Use authService.getCurrentUserToken() for auth

- [ ] **Gallery Component Updates** (`components/Gallery.tsx`):
    - [ ] Remove hardcoded `ITEMS` mock data
    - [ ] Implement state management with TanStack Query or useEffect
    - [ ] Implement `handleFilterChange` with type mapping
    - [ ] Implement debounced `handleSearch` (500ms)
    - [ ] Implement `IntersectionObserver` for infinite scroll
    - [ ] Update key handling to use UUID `id` from API

- [ ] **Delete Feature**:
    - [ ] Add Delete button to Asset Card hover state
    - [ ] Create `ConfirmDeleteDialog` component
    - [ ] Implement delete mutation with optimistic update

- [ ] **Loading States**:
    - [ ] Create `AssetCardSkeleton` component
    - [ ] Show skeletons during initial load and pagination fetch
    - [ ] Implement "End of list" / "No more items" UI state

- [ ] **Error Handling & Notifications**:
    - [ ] Add try-catch blocks in assetService methods
    - [ ] Implement Toast notification on success/error
    - [ ] Handle 401 unauthorized (redirect to login)

- [ ] **Empty State UX**:
    - [ ] Add empty state component for first-time users
    - [ ] Show "Generate New" CTA when no assets exist
    - [ ] Improve "No results" state

- [ ] **Integration Testing**:
    - [ ] Verify Image assets load thumbnails
    - [ ] Verify Video assets load thumbnails/previews
    - [ ] Verify Text assets display content snippets
    - [ ] Verify "All" tab shows mixed content
    - [ ] Verify delete flow with confirmation
    - [ ] Verify infinite scroll pagination
    - [ ] Verify error handling flows

## Dev Notes

### Architecture Patterns (Frontend)

-   **Service Layer**: Encapsulate Axios calls in `services/`. Do not make API calls directly in components.
-   **State Management**: Use `TanStack Query` (React Query) if available, for caching and infinite scroll (`useInfiniteQuery`). If not available, use `useEffect` + local state array appending.
-   **DTO Matching**: Ensure `camelCase` consistency.
    -   Backend: `id`, `title`, `type`, `tag`, `meta`, `url`, `content`, `isVertical`, `isText`, `duration`, `createdAt`.
    -   Frontend Interface should match exactly.

### Authentication

Use existing `authService` for token management:
```typescript
import authService from './authService';

// In assetService
private getAuthToken(): string {
  const token = authService.getCurrentUserToken();
  if (!token) {
    throw new Error('Not authenticated');
  }
  return token;
}
```

**Token Storage Key**: `token` (consistent with authService.ts)

### Tab to API Type Mapping

| Frontend Tab | API `type` Param |
|--------------|------------------|
| All | (omit param) |
| Product Images | image |
| Ad Videos | video |
| Marketing Copy | text |

### API Reference (from Story 6.2)

-   `GET /api/v1/assets`
    -   Query: `type` (image|video|text), `q` (string), `page` (int), `limit` (int)
    -   Response: `{ items: GalleryAsset[], total: number, page: number, limit: number, pages: number }`

-   `DELETE /api/v1/assets/{id}`
    -   Response: `{ "message": "Asset deleted successfully" }`

-   `PATCH /api/v1/assets/{id}`
    -   Body: `{ "title": "New Title" }`
    -   Response: Updated `GalleryAsset`

### Key Implementation Notes

1.  **Debounce**: Use `lodash.debounce` or `useDeferredValue` for search input (500ms delay)
2.  **Infinite Scroll**: Use `IntersectionObserver` on a sentinel element at the bottom of the list
3.  **Delete UX**: Always show confirmation dialog before deleting
4.  **Optimistic Updates**: Remove asset from UI immediately on delete, rollback on error
5.  **ID Type**: Backend returns UUID strings, not numbers. Ensure frontend interfaces use `id: string`

### Codebase Components

-   `components/Gallery.tsx`: Main target.
-   `services/api.ts`: Base axios instance (ensure auth token is attached).

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List
