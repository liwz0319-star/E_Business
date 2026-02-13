# Story 6-1 代码审查记录与修复交接

- 审查对象: `_bmad-output/implementation-artifacts/6-1-project-management-api.md`
- 审查方式: 仅审查 Story 6-1 直接相关代码与测试，忽略其他故事改动
- 审查时间: 2026-02-13
- 当前结论: `Changes Requested`（存在 HIGH/MEDIUM 问题，暂不建议合并）

## 1) 关键问题清单（按优先级）

### HIGH-1: AC2 未完整实现（删除项目未级联删除关联资产）
- 要求证据:
  - `_bmad-output/implementation-artifacts/6-1-project-management-api.md:21`
  - `_bmad-output/implementation-artifacts/6-1-project-management-api.md:168`
- 代码现状:
  - `backend/app/infrastructure/repositories/project_repository.py:97`
  - `backend/app/infrastructure/repositories/project_repository.py:108`
- 说明: 当前只删除 `product_packages` 记录，未看到对关联资产（如 `video_assets`）的清理逻辑。

### HIGH-2: Alembic 迁移链存在重复建索引风险（静态推断）
- 证据:
  - `backend/app/alembic/versions/003_sync_product_packages_schema.py:49`
  - `backend/app/alembic/versions/003_sync_product_packages_schema.py:50`
  - `backend/app/alembic/versions/198a46ecb467_add_name_to_productpackage.py:33`
  - `backend/app/alembic/versions/004_add_product_packages_indexes.py:33`
- 说明: 多个 migration 对同名索引重复创建，完整升级链可能失败（需通过真实升级验证）。

### HIGH-3: Story 勾选与实现不一致（Use Case 单测缺失）
- 要求证据:
  - `_bmad-output/implementation-artifacts/6-1-project-management-api.md:84`
- 现状: `backend/tests` 中未检索到 `ListProjectsUseCase/DeleteProjectUseCase/...` 的直接单测。

### MEDIUM-1: 测试并非全绿，与“29 tests all passing”不一致
- Story 声明证据:
  - `_bmad-output/implementation-artifacts/6-1-project-management-api.md`（Completion Notes）
- 实测命令:
  - `cd backend && poetry run pytest -q tests/test_project_repository.py tests/test_projects_api.py`
- 实测结果:
  - `1 failed, 28 passed`
  - 失败点: `backend/tests/test_projects_api.py:85`（期望 401，实际 403）

### MEDIUM-2: Story File List 与工作区事实不一致
- Story 证据:
  - `_bmad-output/implementation-artifacts/6-1-project-management-api.md:391`
  - `_bmad-output/implementation-artifacts/6-1-project-management-api.md:395`
- 现状: `git status --porcelain` 显示多个 6-1 文件为 `??`（未跟踪），与“已存在/已验证”描述不一致。

### LOW-1: DTO 可变默认值
- 证据:
  - `backend/app/application/dtos/project_dtos.py:58`
- 说明: `artifacts: dict = {}` 建议改为 `Field(default_factory=dict)`。

### LOW-2: total 统计查询存在可优化点
- 证据:
  - `backend/app/infrastructure/repositories/project_repository.py:74`
- 说明: `count(subquery)` 复用了带排序查询，可在大数据量下产生额外开销。

## 2) 修复交接（由其他 Agent 执行）

> 本文件仅记录审查结论与交接，不在本轮直接修复代码。

### 推荐接手 Agent
- 主修复: `dev` agent
- 状态与故事同步: `sm` agent（更新 story 状态、任务勾选与 sprint-status）

### 交接执行顺序
1. 先修复 HIGH（AC 与迁移链风险）
2. 再修复 MEDIUM（测试全绿、文档一致性）
3. 最后处理 LOW（代码质量优化）

## 3) 可执行修复任务清单（给接手 Agent）

- [ ] 实现并验证项目删除时的关联资产删除策略（按 `workflow_id` 或明确业务关联键）
- [ ] 清理重复索引 migration（保证从 `002 -> 005` 全链可升级）
- [ ] 为 `project_management.py` 增补 use case 单测（覆盖 AC1-4）
- [ ] 统一未认证访问语义（401/403）并修正对应测试
- [ ] 修正 Story File List 与 git 事实不一致项
- [ ] 将 DTO 可变默认值改为 `default_factory`
- [ ] 优化项目列表总数查询

## 4) 验收标准

- [ ] Story 6-1 的 AC1-AC5 全部可证明实现
- [ ] 6-1 相关测试全通过（至少 repository + API + use case）
- [ ] Alembic 全链升级成功且无重复索引异常
- [ ] Story 文档中的 File List、Completion Notes 与 git 事实一致

## 5) 建议验证命令

```bash
cd backend
poetry run pytest -q tests/test_project_repository.py tests/test_projects_api.py
poetry run pytest -q tests -k "project_management or projects"
poetry run alembic upgrade head
```

---

记录人: `dev` agent（审查记录）
处理策略: 后续修复交由其他 agent 执行
