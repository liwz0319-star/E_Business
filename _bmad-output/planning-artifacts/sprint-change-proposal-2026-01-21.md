# Sprint 变更提案

**日期:** 2026-01-21
**状态:** 待批准
**范围:** Minor (次要) - 开发团队直接实施

---

## 1. 问题摘要

### 触发事件
Story 1.1 (Backend Project Initialization) 在 Scrum Master 审核阶段发现任务声明已完成但实际配置缺失。

### 问题陈述
> Story 1.1 声称所有任务已完成并标记为 "review" 状态，但审核发现：
> 1. Alembic 依赖已添加但未初始化配置
> 2. 验证未覆盖 Docker/DB/Redis 全链路
> 3. 缺少必要的配置模板 (.env.example, config.py)
> 4. 缺少启动文档 (README.md)

### 发现背景
- **发现时机:** Scrum Master 执行 Story 质量审核
- **Story 状态:** review (待审核通过)
- **影响范围:** 仅 Story 1.1，不影响其他 Story

### 证据
| 证据项 | 详情 |
|--------|------|
| pyproject.toml 包含 alembic | 第30行 |
| 文件清单缺少 alembic.ini | 文件清单空缺 |
| 验证仅提及健康检查 | 完成记录第78行 |
| 缺少 .env.example 和 README | 文件清单空缺 |

---

## 2. 影响分析

### Epic 影响

| Epic | 影响 | 详情 |
|------|------|------|
| **Epic 1** | 🟡 直接影响 | Story 1.1 需要补充任务 |
| Epic 2 | ✅ 无影响 | 无依赖关系 |
| Epic 3 | ✅ 无影响 | 无依赖关系 |
| Epic 4 | ✅ 无影响 | 无依赖关系 |
| Epic 5 | ✅ 无影响 | Story 1.2 会处理 DB |

**结论:** 仅 Epic 1 Story 1.1 受影响，其他 Epic 可继续进行。

### Story 影响

| Story | 影响 | 操作 |
|-------|------|------|
| **Story 1.1** | 🔴 需修改 | 补充 3 个任务，扩展验证 |
| Story 1.2+ | ✅ 无影响 | 可按计划进行 |

### 工件冲突分析

| 工件 | 冲突 | 所需操作 |
|------|------|----------|
| PRD | N/A | 未找到文档，需求无变更 |
| Architecture | ✅ 无冲突 | 无需更新 |
| UI/UX | N/A | 后端 Story 不适用 |
| 测试策略 | 🟡 需扩展 | 添加 DB/Redis 测试 |
| 文档 | 🟡 需添加 | 创建 README |

### 技术影响

| 领域 | 影响 |
|------|------|
| 代码 | 补充配置文件 |
| 基础设施 | 无变化 |
| 部署 | 无影响 |

---

## 3. 推荐方案

### 选择: 选项 1 - 直接调整 ✏️

**决策理由:**

| 评估维度 | 评分 | 说明 |
|----------|------|------|
| **工作量** | 🟢 低 | < 4 小时 |
| **风险** | 🟢 低 | 无架构变更 |
| **时间影响** | 🟢 <1天 | 快速解决 |
| **团队士气** | 🟢 正面 | 保持势头 |
| **可维护性** | 🟢 高 | 补充遗漏 |

**替代方案比较:**
- ❌ **选项 2 (回滚)**: 无已完成工作需回滚，不适用
- ❌ **选项 3 (MVP 重审)**: 不影响 MVP，不必要

**建议:** 直接补充遗漏任务到 Story 1.1，无需回滚或重审范围。

---

## 4. 详细变更提案

### 变更 #1: 修复验收标准 AC 1

**Story:** 1.1
**Section:** Acceptance Criteria

**OLD:**
```gherkin
**Given** a clean git branch
**When** I run the initialization commands
**Then** a `backend` directory is created with `app`, `tests` folders
```

**NEW:**
```gherkin
**Given** a clean git branch
**When** I execute `poetry install` and `docker-compose up -d --build`
**Then** a `backend` directory is created with `app`, `tests` folders
```

**理由:** 将模糊的 "initialization commands" 替换为具体命令，使 AC 可测试。

---

### 变更 #2: 添加 Alembic 初始化任务

**Story:** 1.1
**Section:** Tasks / Subtasks
**插入位置:** "Docker Setup" 之后

**新增任务:**
```markdown
- [ ] Initialize Alembic for Database Migrations (AC 1, 2)
  - [ ] Run `alembic init alembic` in backend directory
  - [ ] Configure `alembic.ini` with database connection URL
  - [ ] Create `backend/app/alembic/env.py` with async SQLAlchemy setup
  - [ ] Create initial migration template
```

**理由:** alembic 依赖已声明但未配置，Story 1.2 依赖此配置。

---

### 变更 #3: 添加配置文件模板任务

**Story:** 1.1
**Section:** Tasks / Subtasks
**插入位置:** "Health Check Endpoint" 之后

**新增任务:**
```markdown
- [ ] Create Configuration Templates (AC 1, 2)
  - [ ] Create `.env.example` with required environment variables:
    - `DATABASE_URL` (PostgreSQL connection)
    - `REDIS_URL` (Redis connection)
    - `SECRET_KEY` (JWT signing)
    - `DEEPSEEK_API_KEY` (AI provider)
  - [ ] Create `backend/app/core/config.py` using pydantic-settings
  - [ ] Document environment variable requirements in Dev Notes
```

**理由:** pydantic-settings 依赖已添加但未使用，其他开发者需要配置指引。

---

### 变更 #4: 添加启动文档任务

**Story:** 1.1
**Section:** Tasks / Subtasks
**插入位置:** "Create Configuration Templates" 之后

**新增任务:**
```markdown
- [ ] Create Project Documentation (AC 1)
  - [ ] Create `backend/README.md` with:
    - Project overview and tech stack
    - Prerequisites (Docker, Poetry)
    - Quick start commands
    - Development setup instructions
    - Environment variable configuration guide
    - Running tests
  - [ ] Add troubleshooting section for common issues
```

**理由:** 新开发者需要清晰的启动指引，减少上手时间。

---

### 变更 #5: 扩展验证覆盖

**Story:** 1.1
**Section:** Dev Agent Record → Completion Notes List

**OLD:**
```markdown
- Implemented standard FastAPI structure (Domain/App/Infra/Interface).
- Configured Poetry with required dependencies.
- Created Backend Dockerfile and root docker-compose.yml.
- Verified Health Check `GET /health` returns 200 OK via pytest.
```

**NEW:**
```markdown
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
```

**理由:** 确保全链路验证，为后续 Story 提供可靠基础。

---

### 变更 #6: 更新文件清单

**Story:** 1.1
**Section:** Dev Agent Record → File List

**新增文件:**
```markdown
- backend/alembic.ini
- backend/app/alembic/env.py
- backend/app/alembic/script.py.mako
- .env.example
- backend/app/core/config.py
- backend/README.md
- backend/tests/test_database.py
- backend/tests/test_redis.py
```

**理由:** 反映补充任务产生的所有文件。

---

## 5. 实施移交

### 变更范围分类
🟢 **Minor (次要)** - 可由开发团队直接实施

### 执行计划

| 角色 | 职责 | 交付物 |
|------|------|--------|
| **开发团队** | 实施 3 个补充任务 | Alembic 配置、配置模板、README |
| **Scrum Master** | 验证完成后重新审核 | 更新 Story 状态 |

### 实施顺序
1. 初始化 Alembic 配置
2. 创建配置文件模板
3. 编写 README 文档
4. 扩展测试验证
5. 更新 Story 状态

### 成功标准
- [ ] Alembic 可正常运行 `alembic revision --autogenerate`
- [ ] `.env.example` 包含所有必需的环境变量
- [ ] `config.py` 可正确加载环境变量
- [ ] README 指引可让新开发者启动项目
- [ ] 测试覆盖 DB/Redis 连接

### 时间估计
- **总工作量:** 2-4 小时
- **阻塞风险:** 无

---

## 6. 审批记录

| 角色 | 姓名 | 状态 | 日期 |
|------|------|------|------|
| Scrum Master | Bob | ✅ 已提交 | 2026-01-21 |
| 开发团队 | - | ⏳ 待批准 | - |
| 产品负责人 | - | ⏳ 知情 | - |

---

*本变更提案由 Correct Course 工作流生成*
