# Story 6.5: Frontend Projects Integration

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **User**,
I want **the Projects page to display my real projects from the backend with functional actions (Delete, Duplicate, Edit)**,
so that **I can effectively manage my AI-generated content projects.**

## Acceptance Criteria

1. **ProjectService API Client**:
    *   Create `services/projectService.ts` with typed API methods (MUST use `localStorage.getItem('token')` for auth).
    *   **GET /api/v1/projects**: Fetch paginated project list with query params (`page`, `limit`, `sortBy`, `sortOrder`, `status`, `search`).
    *   **DELETE /api/v1/projects/{id}**: Delete a project (returns 204).
    *   **POST /api/v1/projects/{id}/duplicate**: Duplicate a project (returns new project).
    *   **PATCH /api/v1/projects/{id}**: Rename a project.

2. **Projects.tsx Real Data Integration**:
    *   Replace hardcoded `todayProjects`, `yesterdayProjects`, `lastWeekProjects` arrays with API data.
    *   Use `useEffect` to fetch projects on component mount.
    *   Implement loading state (spinner/skeleton).
    *   Implement error handling with user-friendly toast/alert.
    *   Group projects by date (Today, Yesterday, Last Week, Older) using `createdAt` field.
    *   **Pagination UI**: Implement a "Load More" button at the bottom of the list when more pages are available.

3. **Action Buttons Wired to API**:
    *   **Delete**: Call `projectService.deleteProject(id)`, show confirmation dialog, refresh list on success.
    *   **Duplicate**: Call `projectService.duplicateProject(id)`, refresh list on success, show success toast.
    *   **Edit/Rename**: Open modal or inline edit, call `projectService.updateProject(id, { name })`, refresh list.

4. **Search Integration**:
    *   Connect search input to API `search` query parameter with debounce (300ms).
    *   Update URL params for shareable search state (optional but recommended).

5. **Empty State & Error Handling**:
    *   Show "No projects found" when API returns empty array.
    *   Show error message when API fails (network error, 401, 500).

## Tasks / Subtasks

- [ ] **API Service Layer** (AC 1)
  - [ ] Create `services/projectService.ts`.
  - [ ] Define TypeScript interfaces matching backend DTOs (`ProjectListItem`, `ProjectListResponse`, `ProjectUpdateRequest`).
  - [ ] Implement `getProjects(params)` with query string building.
  - [ ] Implement `deleteProject(id)`.
  - [ ] Implement `duplicateProject(id)`.
  - [ ] Implement `updateProject(id, data)`.
  - [ ] Add auth token injection (reuse pattern from `authService.ts`).
  - [ ] Export singleton instance.

- [ ] **Projects Component Updates** (AC 2, 4, 5)
  - [ ] Import `projectService` in `Projects.tsx`.
  - [ ] Add state: `projects` (accumulated list), `loading`, `error`, `page`, `hasMore`.
  - [ ] Add `useEffect` to fetch projects on mount (reset list).
  - [ ] Implement `loadMore()` function to fetch next page and append to `projects`.
  - [ ] Implement date grouping helper (`groupProjectsByDate(projects)`).
  - [ ] Replace mock data with API data.
  - [ ] Remove legacy client-side `.filter()` logic (search is server-side now).
  - [ ] Add loading spinner/skeleton during fetch.
  - [ ] Add error display component.
  - [ ] Implement search debounce with `useMemo` or `useCallback`.
  - [ ] Add "Load More" button at bottom (visible only if `hasMore` is true).

- [ ] **Action Handlers** (AC 3)
  - [ ] Update `handleAction` for 'Delete':
    - [ ] Show confirmation dialog (window.confirm or custom modal).
    - [ ] Call `projectService.deleteProject(id)`.
    - [ ] Refresh list on success.
    - [ ] Show success/error toast.
  - [ ] Update `handleAction` for 'Duplicate':
    - [ ] Call `projectService.duplicateProject(id)`.
    - [ ] Refresh list on success.
    - [ ] Show success toast.
  - [ ] Update `handleAction` for 'Edit':
    - [ ] Show inline edit or modal for name change.
    - [ ] Call `projectService.updateProject(id, { name })`.
    - [ ] Refresh list on success.

- [ ] **Testing** (AC 1-5)
  - [ ] Unit tests for `projectService.ts` (mock axios).
  - [ ] Component test for loading state.
  - [ ] Component test for error state.
  - [ ] Component test for delete confirmation flow.
  - [ ] Integration test for search debounce.

## Dev Notes

### Architecture Compliance

**Follow Existing Service Patterns**:
- Reuse axios configuration from `authService.ts` and `productPackageService.ts`.
- Token retrieval: `localStorage.getItem('token')` (note: authService uses 'token', productPackageService uses 'access_token' - need to verify which is correct).
- API base URL: Use `import.meta.env.VITE_API_URL` or `VITE_API_BASE`.

### Backend API Contracts (from Story 6-1)

**GET /api/v1/projects**
```
Query Parameters:
- page: int = 1
- limit: int = 20
- sortBy: str = "created_at" | "name" | "updated_at"
- sortOrder: str = "desc" | "asc"
- status: str | None = "pending" | "running" | "completed" | "failed"
- search: str | None

Response (camelCase):
{
  "items": [
    {
      "id": "uuid",
      "name": "My Product Copy",
      "workflowId": "workflow-uuid",
      "status": "completed",
      "stage": "copywriting",
      "thumbnailUrl": "https://minio.../image1.jpg",
      "createdAt": "2026-02-12T10:00:00Z"
    }
  ],
  "total": 42,
  "page": 1,
  "limit": 20,
  "pages": 3
}
```

**DELETE /api/v1/projects/{id}**
- Response: 204 No Content
- Error: 404 if not found, 403 if owned by another user

**POST /api/v1/projects/{id}/duplicate**
```
Response:
{
  "id": "new-uuid",
  "name": "My Product Copy (Copy)",
  "workflowId": "new-workflow-uuid",
  "status": "pending",
  "createdAt": "2026-02-12T11:00:00Z"
}
```

**PATCH /api/v1/projects/{id}**
```
Request:
{ "name": "New Project Name" }

Response: 200 OK with updated project object.
```

### TypeScript Interface Definitions

```typescript
// services/projectService.ts

export interface ProjectListItem {
  id: string;
  name: string;
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  stage: 'analysis' | 'copywriting' | 'image_generation' | 'video_generation';
  thumbnailUrl?: string;
  createdAt: string;
  updatedAt?: string;
}

export interface ProjectListResponse {
  items: ProjectListItem[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface ProjectListParams {
  page?: number;
  limit?: number;
  sortBy?: 'created_at' | 'name' | 'updated_at';
  sortOrder?: 'desc' | 'asc';
  status?: 'pending' | 'running' | 'completed' | 'failed';
  search?: string;
}

export interface ProjectUpdateRequest {
  name: string;
}

export interface ProjectDuplicateResponse {
  id: string;
  name: string;
  workflowId: string;
  status: string;
  createdAt: string;
}
```

### Service Implementation Pattern

```typescript
// services/projectService.ts

import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/projects`
  : 'http://localhost:8000/api/v1/projects';

class ProjectService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE;
  }

  private getAuthToken(): string {
    // CRITICAL: Use 'token' to match authService.ts. Do NOT use 'access_token'.
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No authentication token found');
    }
    return token;
  }

  private getConfig() {
    const token = this.getAuthToken();
    return {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    };
  }

  async getProjects(params: ProjectListParams = {}): Promise<ProjectListResponse> {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', String(params.page));
    if (params.limit) queryParams.append('limit', String(params.limit));
    if (params.sortBy) queryParams.append('sortBy', params.sortBy);
    if (params.sortOrder) queryParams.append('sortOrder', params.sortOrder);
    if (params.status) queryParams.append('status', params.status);
    if (params.search) queryParams.append('search', params.search);

    const response = await axios.get<ProjectListResponse>(
      `${this.baseUrl}?${queryParams.toString()}`,
      this.getConfig()
    );
    return response.data;
  }

  async deleteProject(id: string): Promise<void> {
    await axios.delete(`${this.baseUrl}/${id}`, this.getConfig());
  }

  async duplicateProject(id: string): Promise<ProjectDuplicateResponse> {
    const response = await axios.post<ProjectDuplicateResponse>(
      `${this.baseUrl}/${id}/duplicate`,
      {},
      this.getConfig()
    );
    return response.data;
  }

  async updateProject(id: string, data: ProjectUpdateRequest): Promise<ProjectListItem> {
    const response = await axios.patch<ProjectListItem>(
      `${this.baseUrl}/${id}`,
      data,
      this.getConfig()
    );
    return response.data;
  }
}

export const projectService = new ProjectService();
```

### Date Grouping Helper

```typescript
// utils/dateGrouping.ts or inline in Projects.tsx

type ProjectGroup = {
  title: string;
  items: ProjectListItem[];
};

function groupProjectsByDate(projects: ProjectListItem[]): ProjectGroup[] {
  const now = new Date();
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const yesterday = new Date(today);
  yesterday.setDate(yesterday.getDate() - 1);
  const lastWeek = new Date(today);
  lastWeek.setDate(lastWeek.getDate() - 7);

  const groups: Record<string, ProjectListItem[]> = {
    'Today': [],
    'Yesterday': [],
    'Last Week': [],
    'Older': [],
  };

  projects.forEach(project => {
    const createdAt = new Date(project.createdAt);
    if (createdAt >= today) {
      groups['Today'].push(project);
    } else if (createdAt >= yesterday) {
      groups['Yesterday'].push(project);
    } else if (createdAt >= lastWeek) {
      groups['Last Week'].push(project);
    } else {
      groups['Older'].push(project);
    }
  });

  return Object.entries(groups)
    .filter(([, items]) => items.length > 0)
    .map(([title, items]) => ({ title, items }));
}
```

### Search Debounce Hook

```typescript
// hooks/useDebounce.ts or inline

import { useState, useEffect } from 'react';

function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}

// Usage in Projects.tsx:
// const debouncedSearch = useDebounce(searchQuery, 300);
// useEffect(() => {
//   fetchProjects({ search: debouncedSearch });
// }, [debouncedSearch]);
```

### Action Handler Updates

```typescript
// Updated handleAction in Projects.tsx

const handleAction = async (e: React.MouseEvent, action: string, project: ProjectListItem) => {
  e.stopPropagation();

  switch (action) {
    case 'Delete':
      if (window.confirm(`Are you sure you want to delete "${project.name}"?`)) {
        try {
          await projectService.deleteProject(project.id);
          // Show success toast
          fetchProjects(); // Refresh list
        } catch (error) {
          // Show error toast
          console.error('Delete failed:', error);
        }
      }
      break;

    case 'Duplicate':
      try {
        await projectService.duplicateProject(project.id);
        // Show success toast
        fetchProjects();
      } catch (error) {
        // Show error toast
        console.error('Duplicate failed:', error);
      }
      break;

    case 'Edit':
      const newName = prompt('Enter new project name:', project.name);
      if (newName && newName !== project.name) {
        try {
          await projectService.updateProject(project.id, { name: newName });
          fetchProjects();
        } catch (error) {
          console.error('Update failed:', error);
        }
      }
      break;
  }
};
```

### Token Key Consistency Check

### Token Key Consistency Check

> [!IMPORTANT]
> **Use 'token'**: `authService.ts` uses `localStorage.getItem('token')`. This is the single source of truth.
> Do NOT use `access_token` (as seen in `productPackageService.ts` - that service needs correction).
> Ensure `projectService.ts` consistently uses `localStorage.getItem('token')`.

### Project Structure Notes

**New Files to Create**:
```
services/
└── projectService.ts     # API client for projects

hooks/
└── useDebounce.ts        # (optional) Reusable debounce hook
```

**Files to Modify**:
```
components/
└── Projects.tsx          # Integrate real API data and actions
```

### References

- [Story 6.1 - Project Management API](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/6-1-project-management-api.md) - Backend API contracts
- [Epic 6 Requirements](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/epic-6-user-dashboard.md)
- [authService.ts](file:///f:/AAA Work/AIproject/E_Business/services/authService.ts) - Auth pattern reference
- [productPackageService.ts](file:///f:/AAA Work/AIproject/E_Business/services/productPackageService.ts) - Service class pattern reference
- [Projects.tsx](file:///f:/AAA Work/AIproject/E_Business/components/Projects.tsx) - Current component (mock data)
- [Architecture - Naming Conventions](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md#Naming-Patterns)

## Dev Agent Record

### Agent Model Used

{{agent_model_name_version}}

### Debug Log References

### Completion Notes List

### File List

## Change Log

- 2026-02-14: Story created by SM (Bob) in YOLO mode
  - Analyzed backend API contracts from Story 6-1
  - Analyzed existing frontend patterns (authService, productPackageService)
  - Analyzed current Projects.tsx component structure
  - Created comprehensive implementation guide with TypeScript interfaces and code examples
- 2026-02-14: Story reviewed and updated by SM (Bob)
  - Enforced Token consistency ('token' key)
  - Added "Load More" pagination requirement
  - Cleaned up client-side search logic
