# Story 6.3: User Settings & Profile

Status: review

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **User**,
I want **to view and update my AI preferences and integration settings**,
so that **I can personalize my content generation experience and manage platform integrations.**

## Acceptance Criteria

1.  **Database Schema Extension**:
    *   A new `user_settings` table exists with One-to-One relationship to `users` table.
    *   Table stores AI preferences (language, tone, aspect_ratio) and integration status (shopify, amazon, tiktok).
    *   Settings are automatically created when a new user registers (or lazy-created on first access).

2.  **API Endpoint - Get Settings (`GET /api/v1/user/settings`)**:
    *   Returns the current user's settings including AI preferences and integration status.
    *   Returns default settings if user has no existing settings record.
    *   Response format matches Frontend `Settings.tsx` expectations.

3.  **API Endpoint - Update Settings (`PATCH /api/v1/user/settings`)**:
    *   Allows partial updates to AI preferences and/or integration status.
    *   Only updates fields that are explicitly provided in the request body.
    *   Returns the updated settings object.
    *   Validates input: language must be valid locale, aspect_ratio must be valid ratio string.

4.  **Security**:
    *   All endpoints require JWT authentication.
    *   Users can only access their own settings (enforced via `get_current_user` dependency).

5.  **Error Handling**:
    *   Returns 401 Unauthorized if not authenticated.
    *   Returns 422 Unprocessable Entity for validation errors.

## Frontend Field Mapping (Settings.tsx)

The API response MUST include all fields expected by `Settings.tsx`:

| Frontend Field | Type | Source/Logic | Notes |
|----------------|------|--------------|-------|
| `aiPreferences.language` | string | `language` column | e.g., "zh-CN", "en-US" |
| `aiPreferences.tone` | string | `tone` column | e.g., "professional", "casual", "playful" |
| `aiPreferences.aspectRatio` | string | `aspect_ratio` column | e.g., "1:1", "16:9", "9:16" |
| `integrations.shopify` | object | `shopify_config` JSON | {connected: bool, storeName?: string} |
| `integrations.amazon` | object | `amazon_config` JSON | {connected: bool, region?: string} |
| `integrations.tiktok` | object | `tiktok_config` JSON | {connected: bool, accountName?: string} |

### Default Settings

```python
DEFAULT_SETTINGS = {
    "language": "en-US",
    "tone": "professional",
    "aspect_ratio": "1:1",
    "shopify_config": {"connected": False},
    "amazon_config": {"connected": False},
    "tiktok_config": {"connected": False},
}
```

### Valid Values

```python
VALID_LANGUAGES = ["en-US", "zh-CN", "zh-TW", "ja-JP", "ko-KR"]
VALID_TONES = ["professional", "casual", "playful", "luxury", "minimal"]
VALID_ASPECT_RATIOS = ["1:1", "4:3", "3:4", "16:9", "9:16"]
```

### DTO Response Example

```json
{
  "aiPreferences": {
    "language": "zh-CN",
    "tone": "professional",
    "aspectRatio": "1:1"
  },
  "integrations": {
    "shopify": {
      "connected": true,
      "storeName": "my-store.myshopify.com"
    },
    "amazon": {
      "connected": false
    },
    "tiktok": {
      "connected": false
    }
  },
  "updatedAt": "2026-02-13T10:30:00Z"
}
```

## Tasks / Subtasks

- [x] **Infrastructure Layer**: Create Database Schema
    - [x] Create `UserSettingsModel` in `app/infrastructure/database/models.py`.
    - [x] Fields: `id`, `user_id` (FK to users, unique), `language`, `tone`, `aspect_ratio`, `shopify_config` (JSON), `amazon_config` (JSON), `tiktok_config` (JSON), `created_at`, `updated_at`.
    - [x] Create Alembic migration script (`alembic revision --autogenerate -m "add_user_settings_table"`).
    - [x] Apply migration (`alembic upgrade head`).

- [x] **Domain Layer**: Create Entities and Interfaces
    - [x] Create `UserSettings` domain entity in `app/domain/entities/user_settings.py`.
    - [x] Create `IUserSettingsRepository` interface in `app/domain/interfaces/user_settings_repository.py`.

- [x] **Infrastructure Layer**: Implement Repository
    - [x] Create `UserSettingsRepository` implementing `IUserSettingsRepository`.
    - [x] Implement `get_by_user_id(user_id)` - returns settings or None.
    - [x] Implement `get_or_create(user_id)` - returns existing or creates with defaults.
    - [x] Implement `update(user_id, updates)` - partial update with merge.
    - [x] Add unit tests for repository methods.

- [x] **Application Layer**: Create DTOs and Service
    - [x] Create `UserSettingsDTOs` in `app/application/dtos/user_settings_dtos.py`.
    - [x] Create `AIPreferencesDTO`, `IntegrationConfigDTO`, `UserSettingsResponseDTO`.
    - [x] Create `UpdateUserSettingsRequestDTO` for PATCH body.
    - [x] Create `UserSettingsService` with `get_settings` and `update_settings` use cases.
    - [x] Implement field mapping logic (snake_case to camelCase nesting).

- [x] **Interface Layer**: Create API Endpoints
    - [x] Create `app/interface/routes/user_settings.py` (following existing route patterns).
    - [x] Implement `GET /api/v1/user/settings` with auth dependency.
    - [x] Implement `PATCH /api/v1/user/settings` with validation.
    - [x] Register router in `app/interface/routes/__init__.py` and `main.py`.

- [x] **Testing**:
    - [x] Create `tests/test_user_settings_repository.py` for repository tests.
    - [x] Create `tests/test_user_settings_service.py` for service tests.
    - [x] Create `tests/test_user_settings_api.py` for API integration tests.
    - [x] Test get default settings (lazy creation).
    - [x] Test partial updates (only provided fields updated).
    - [x] Test validation (invalid language/tone/aspect_ratio rejected).

## Dev Notes

### Architecture Compliance

**Follow Pragmatic Clean Architecture**:
- `domain/`: UserSettings entity, IUserSettingsRepository interface (pure Python)
- `application/`: Use cases, DTOs with Pydantic v2
- `infrastructure/`: SQLAlchemy model and repository implementation
- `interface/`: FastAPI routes with dependencies

### Database Schema

**UserSettingsModel**:
```python
class UserSettingsModel(Base):
    __tablename__ = "user_settings"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )
    language: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="en-US",
    )
    tone: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="professional",
    )
    aspect_ratio: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        default="1:1",
    )
    shopify_config: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {"connected": False},
    )
    amazon_config: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {"connected": False},
    )
    tiktok_config: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {"connected": False},
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.utcnow(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
        nullable=False,
    )
```

### API Specifications

**GET /api/v1/user/settings**
- Auth: Required (Bearer Token)
- Response (camelCase):
```json
{
  "aiPreferences": {
    "language": "zh-CN",
    "tone": "professional",
    "aspectRatio": "1:1"
  },
  "integrations": {
    "shopify": {"connected": false},
    "amazon": {"connected": false},
    "tiktok": {"connected": false}
  },
  "updatedAt": "2026-02-13T10:30:00Z"
}
```

**PATCH /api/v1/user/settings**
- Auth: Required (Bearer Token)
- Request (partial update):
```json
{
  "aiPreferences": {
    "language": "zh-CN",
    "tone": "playful"
  }
}
```
- Response: 200 OK with updated full settings object.

### Naming Conventions

**CRITICAL - JSON Response camelCase with Nested Objects**:
```python
from pydantic import ConfigDict, Field
from pydantic.alias_generators import to_camel

class AIPreferencesDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    language: str
    tone: str
    aspect_ratio: str = Field(alias="aspectRatio")  # Explicit for clarity

class UserSettingsResponseDTO(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    ai_preferences: AIPreferencesDTO = Field(alias="aiPreferences")
    integrations: IntegrationsDTO
    updated_at: datetime = Field(alias="updatedAt")
```

### Get or Create Pattern

**Lazy Settings Creation**:
```python
async def get_or_create(self, user_id: UUID) -> UserSettingsModel:
    settings = await self.get_by_user_id(user_id)
    if settings is None:
        # Create with defaults
        settings = UserSettingsModel(
            user_id=user_id,
            **DEFAULT_SETTINGS
        )
        self.session.add(settings)
        await self.session.commit()
        await self.session.refresh(settings)
    return settings
```

### Partial Update Logic

**Merge Update Pattern**:
```python
async def update(
    self,
    user_id: UUID,
    updates: dict
) -> UserSettingsModel:
    settings = await self.get_or_create(user_id)

    # Handle nested AI preferences
    if "ai_preferences" in updates:
        prefs = updates["ai_preferences"]
        if "language" in prefs:
            settings.language = prefs["language"]
        if "tone" in prefs:
            settings.tone = prefs["tone"]
        if "aspect_ratio" in prefs:
            settings.aspect_ratio = prefs["aspect_ratio"]

    # Handle nested integrations
    if "integrations" in updates:
        integrations = updates["integrations"]
        if "shopify" in integrations:
            settings.shopify_config = {
                **settings.shopify_config,
                **integrations["shopify"]
            }
        # ... similar for amazon and tiktok

    await self.session.commit()
    await self.session.refresh(settings)
    return settings
```

### Validation Logic

**Pydantic Validators**:
```python
from pydantic import field_validator

class UpdateAIPreferencesDTO(BaseModel):
    language: str | None = None
    tone: str | None = None
    aspect_ratio: str | None = None

    @field_validator("language")
    @classmethod
    def validate_language(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_LANGUAGES:
            raise ValueError(f"Invalid language. Must be one of: {VALID_LANGUAGES}")
        return v

    @field_validator("tone")
    @classmethod
    def validate_tone(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_TONES:
            raise ValueError(f"Invalid tone. Must be one of: {VALID_TONES}")
        return v

    @field_validator("aspect_ratio")
    @classmethod
    def validate_aspect_ratio(cls, v: str | None) -> str | None:
        if v is not None and v not in VALID_ASPECT_RATIOS:
            raise ValueError(f"Invalid aspect ratio. Must be one of: {VALID_ASPECT_RATIOS}")
        return v
```

### Source Tree Components to Touch

- `backend/app/infrastructure/database/models.py` - Add UserSettingsModel
- `backend/app/alembic/versions/` - New migration script
- `backend/app/domain/entities/user_settings.py` - New file
- `backend/app/domain/interfaces/user_settings_repository.py` - New file
- `backend/app/infrastructure/repositories/user_settings_repository.py` - New file
- `backend/app/application/dtos/user_settings_dtos.py` - New file
- `backend/app/application/services/user_settings_service.py` - New file
- `backend/app/interface/routes/user_settings.py` - New file
- `backend/app/interface/routes/__init__.py` - Register router
- `backend/app/main.py` - Include router

### Testing Standards

**Unit Tests**:
- Repository: Test get_or_create, partial updates
- Service: Test validation, default merging
- DTOs: Test camelCase alias generation

**Integration Tests**:
- Use test database with auth user
- Test: GET settings (default), PATCH partial update, validation errors
- Coverage Target: 85%+ for new code

### Dependencies

**Epic 1 (Auth)**: Completed
- User model and JWT authentication exist
- `get_current_user` dependency available in `app/interface/dependencies/auth.py`
- User entity available in `app/domain/entities/user.py`

**Epic 6 Stories 6-1 & 6-2**: Completed (for patterns reference)
- Repository pattern established
- DTO camelCase conventions established
- Test patterns established

### Project Structure Notes

**New Files to Create**:
```
backend/app/
├── domain/
│   ├── entities/
│   │   └── user_settings.py
│   └── interfaces/
│       └── user_settings_repository.py
├── infrastructure/
│   └── repositories/
│       └── user_settings_repository.py
├── application/
│   ├── dtos/
│   │   └── user_settings_dtos.py
│   └── services/
│       └── user_settings_service.py
└── interface/
    └── routes/
        └── user_settings.py
```

**Register New Route in main.py**:
```python
from app.interface.routes import user_settings
app.include_router(user_settings.router, prefix="/api/v1/user", tags=["user-settings"])
```

### References

- [Architecture Decision - Clean Architecture](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md#Project-Structure-&-Boundaries)
- [Architecture Decision - Naming Conventions](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md#Naming-Patterns)
- [Epic 6 Requirements](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/epic-6-user-dashboard.md)
- [Story 6.1 - Project Management API](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/6-1-project-management-api.md) (Reference for repository pattern)
- [Story 6.2 - Asset Gallery API](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/6-2-asset-gallery-api.md) (Reference for DTO patterns)

## Dev Agent Record

### Agent Model Used

Claude (claude-5-sonnet)

### Debug Log References

None - clean implementation following TDD methodology.

### Completion Notes List

**2026-02-14 Implementation Summary:**

All 5 acceptance criteria satisfied:
1. ✅ Database Schema Extension - `user_settings` table created with One-to-One relationship to `users`, storing AI preferences and integration status. Settings are lazy-created on first access.
2. ✅ GET /api/v1/user/settings - Returns current user's settings with default values if none exist. Response format matches Settings.tsx expectations with camelCase nested objects.
3. ✅ PATCH /api/v1/user/settings - Partial updates supported. Only provided fields are updated. Full validation of language, tone, and aspect_ratio values.
4. ✅ Security - All endpoints require JWT authentication via `get_current_user` dependency. Users can only access their own settings.
5. ✅ Error Handling - Returns 401 for unauthenticated requests, 422 for validation errors.

**Test Coverage:**
- 36 tests passing (5 model tests, 10 repository tests, 8 service tests, 13 API tests)
- All validation tests pass for invalid language/tone/aspect_ratio
- Partial update tests verify only provided fields are updated
- Lazy creation tests verify default settings on first access

**Architecture:**
- Followed Pragmatic Clean Architecture pattern
- Domain layer: UserSettings entity, IUserSettingsRepository interface (pure Python)
- Application layer: UserSettingsService with DTOs using Pydantic v2 with camelCase aliases
- Infrastructure layer: UserSettingsModel (SQLAlchemy), PostgresUserSettingsRepository
- Interface layer: FastAPI routes with JWT auth dependency

### File List

**New Files:**
- `backend/app/domain/entities/user_settings.py` - UserSettings domain entity
- `backend/app/domain/interfaces/user_settings_repository.py` - IUserSettingsRepository interface
- `backend/app/infrastructure/repositories/user_settings_repository.py` - PostgresUserSettingsRepository
- `backend/app/application/dtos/user_settings_dtos.py` - Request/Response DTOs with camelCase aliases
- `backend/app/application/services/user_settings_service.py` - UserSettingsService
- `backend/app/interface/routes/user_settings.py` - API endpoints
- `backend/app/alembic/versions/006_create_user_settings_table.py` - Database migration
- `backend/tests/test_user_settings_model.py` - Model tests (5 tests)
- `backend/tests/test_user_settings_repository.py` - Repository tests (10 tests)
- `backend/tests/test_user_settings_service.py` - Service tests (8 tests)
- `backend/tests/test_user_settings_api.py` - API integration tests (13 tests)

**Modified Files:**
- `backend/app/infrastructure/database/models.py` - Added UserSettingsModel
- `backend/app/interface/routes/__init__.py` - Added user_settings_router
- `backend/app/main.py` - Registered user_settings_router

## Change Log

- 2026-02-13: Story created by SM (Bob) - YOLO mode with comprehensive context analysis
- 2026-02-14: Implementation completed by Dev Agent (Amelia) - All 5 ACs satisfied, 36 tests passing
