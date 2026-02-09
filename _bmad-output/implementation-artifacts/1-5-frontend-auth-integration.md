# Story 1.5: Frontend Authentication Integration

Status: done # 2026-02-05 所有CRITICAL/MEDIUM问题已修复

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a **user**,
I want **to be able to sign up and log in via the web interface**,
so that **I can securely access the application features**.

## Acceptance Criteria

1. **Given** a new user on the Signup page
   **When** they enter valid email and password and submit
   **Then** a `POST /api/v1/auth/signup` request is sent
   **And** on success (201), the user is redirected to the Login page (or auto-logged in)
   **And** on failure, an error message is displayed

2. **Given** a registered user on the Login page
   **When** they enter valid credentials and submit
   **Then** a `POST /api/v1/auth/login` request is sent
   **And** on success (200), the received JWT token is stored securely (localStorage)
   **And** the user is redirected to the Dashboard/Home
   **And** on failure (401), an "Invalid credentials" error is displayed

3. **Given** an authenticated user
   **When** they refresh the page
   **Then** they remain logged in (token persistence)

4. **Given** an authenticated user
   **When** they click "Logout"
   **Then** the token is removed
   **And** they are redirected to the Login page

## Tasks / Subtasks

- [x] **Task 1: Implement Frontend AuthService** (AC: 1, 2, 3, 4) - ✅ **已完成**
  - [x] Create `services/authService.ts` - 已存在于项目根目录
  - [x] Define types: `User`, `LoginRequest`, `RegisterRequest`, `AuthResponse` - 已定义
  - [x] Implement `login`, `register`, `logout`, `getCurrentUser` methods - 已实现
  - [x] Implement token storage helper (localStorage) - 已实现

- [x] **Task 2: Integrate Signup Page** (AC: 1) - ✅ **已完成**
  - [x] Update `components/Signup.tsx` to use `authService.register`
  - [x] Add loading state handling
  - [x] Add error message display
  - [x] Implement navigation on success
  - [x] 密码强度实时验证 (8字符+大小写+数字)

- [x] **Task 3: Integrate Login Page** (AC: 2) - ✅ **已完成**
  - [x] Update `components/Login.tsx` to use `authService.login`
  - [x] Add loading state handling
  - [x] Add error message display
  - [x] Implement navigation on success

- [x] **Task 4: App-level Auth State** (AC: 3, 4) - ✅ **已完成**
  - [x] Update `App.tsx` to check for token on mount
  - [x] Implement redirects if unauthenticated (for protected routes)
  - [x] Connect Logout button in Sidebar

## Review Follow-ups (AI)

**代码审查日期**: 2026-02-05
**审查发现**: 8个问题 (3 CRITICAL, 3 MEDIUM, 2 LOW)
**详细报告**: `_bmad-output/implementation-artifacts/plan3.md`
**修复日期**: 2026-02-05

- [x] **[CRITICAL][P0]** Token过期验证缺失 - `services/authService.ts:66-78` - ✅ 已添加JWT过期时间检查
- [x] **[CRITICAL][P0]** Terms Checkbox未验证 - `components/Signup.tsx` - ✅ 已添加termsAccepted状态验证
- [x] **[CRITICAL][P0]** fullName字段收集但不使用 - `components/Signup.tsx` - ✅ 已移除
- [x] **[MEDIUM][P1]** API URL硬编码 - `services/authService.ts:4-7` - ✅ 使用import.meta.env.VITE_API_URL
- [x] **[MEDIUM][P1]** 缺少请求拦截器 - `services/authService.ts:9-20` - ✅ 已添加apiClient拦截器
- [x] **[MEDIUM][P1]** 错误处理不统一 - ✅ 创建`utils/errorHandler.ts`统一处理
- [ ] **[LOW][P2]** localStorage XSS风险 - 记录为技术债务，未来考虑httpOnly cookies
- [ ] **[LOW][P2]** 缺少测试文件 - 待后续Sprint添加


## Dev Notes

- **API Endpoint**: Base URL is `http://localhost:8000/api/v1` (based on `backend/app/main.py`)
- **API Contracts**:
  - Login: `POST /auth/login` -> `{ access_token, token_type }` (后端返回蛇形命名)
  - Register: `POST /auth/signup` -> `{ message, user }`
- **Token Storage**: Use `localStorage` for simplicity (as per current plan), but consider `httpOnly` cookies for future security enhancements.
- **Library**: Use `axios` for HTTP requests if not already present, or native `fetch`.

### 重要实现说明

#### 密码强度验证
前端必须实现与后端一致的密码验证规则：
- 最少8个字符
- 至少一个大写字母
- 至少一个小写字母
- 至少一个数字
- 在提交前验证，提供实时反馈

#### 命名转换注意
后端API返回蛇形命名（snake_case），前端使用驼峰命名（camelCase）：
- 后端: `access_token`, `token_type`
- 前端: `accessToken`, `tokenType`
- 确保authService正确处理此转换

#### 完整错误处理策略
需要处理以下错误场景：
| 错误类型 | HTTP状态 | 用户消息 |
|---------|---------|---------|
| 无效凭据 | 401 | "Invalid credentials" / "邮箱或密码错误" |
| 用户已存在 | 400 | "User already exists" / "该邮箱已注册" |
| 密码强度不足 | 422 | "Password too weak" / "密码强度不足" |
| 网络错误 | - | "Network error, please try again" |
| 服务器错误 | 500 | "Server error, please try again later" |

#### 安全警告 ⚠️
使用localStorage存储JWT令牌存在XSS攻击风险：
- 当前实现使用localStorage是为了简单性
- 未来应考虑迁移到httpOnly cookies
- 确保所有用户输入都经过适当转义以防止XSS
- 令牌应设置合理的过期时间

## Architecture Compliance:
   - **Frontend Structure**: Keep services in `services/` directory. Keep components in `components/`.
   - **Types**: Define interfaces for all API payloads.

### Project Structure Notes

- `services/authService.ts` should be the single source of truth for auth API calls.
- `components/Login.tsx` and `components/Signup.tsx` are currently static; this story makes them dynamic.

### References

- [Source: backend/app/interface/routes/auth.py] - Backend API implementation details
- [Source: components/Login.tsx] - Existing Login UI
- [Source: components/Signup.tsx] - Existing Signup UI
- [Source: _bmad-output/implementation-artifacts/1-2-database-auth-setup.md] - Auth API Story

## Dev Agent Record

### Agent Model Used
Gemini (Antigravity)

### Debug Log References
- axios依赖未安装，通过 `npm install axios` 修复

### Completion Notes List
- 2026-02-05: 完成所有前端认证集成任务
- Signup.tsx: 添加authService集成、密码强度验证、loading/error状态
- Login.tsx: 添加authService集成、loading/error状态、错误消息UI
- App.tsx: 添加token持久化检查、handleLogout函数
- Sidebar.tsx: 添加Logout按钮和onLogout prop

### File List
- `services/authService.ts` - AuthService核心服务 (Task 1, 早前已完成)
- `components/Signup.tsx` - 注册页面集成 (Task 2)
- `components/Login.tsx` - 登录页面集成 (Task 3)
- `App.tsx` - App级别认证状态 (Task 4)
- `components/Sidebar.tsx` - 添加Logout按钮 (Task 4)
- `package.json` - 添加axios依赖
