# Story 6-3 代码审查记录与修复交接

## 范围
- 审查对象: Story 6-3（User Settings & Profile）
- 审查文件:
  - `backend/app/infrastructure/repositories/user_settings_repository.py`
  - `backend/app/application/services/user_settings_service.py`
  - `backend/app/application/dtos/user_settings_dtos.py`
  - `backend/app/interface/routes/user_settings.py`
  - `backend/tests/test_user_settings_repository.py`
  - `backend/tests/test_user_settings_service.py`
  - `backend/tests/test_user_settings_api.py`

## 测试基线（审查时）
- 命令:
  - `cd backend && poetry run pytest -q tests/test_user_settings_model.py tests/test_user_settings_repository.py tests/test_user_settings_service.py tests/test_user_settings_api.py`
- 结果:
  - `36 passed, 1 warning`

## 发现（按严重度）

### 1. 高风险: `get_or_create` 并发竞态可能导致 500 ✅ 已修复
- 位置:
  - `backend/app/infrastructure/repositories/user_settings_repository.py:92`
  - `backend/app/infrastructure/repositories/user_settings_repository.py:121`
- 问题:
  - 逻辑为"先查后建"，首次并发访问同一用户时，后到请求可能撞唯一约束失败。
  - 路由层将异常包装为 500，影响稳定性。
- 影响:
  - AC2（首次访问返回默认设置）在并发下不稳定。
- **修复方案**:
  - 新增 `_create_with_race_handling` 方法，捕获 `IntegrityError` 后回查并返回已存在记录
  - 添加 `from sqlalchemy.exc import IntegrityError` import

### 2. 中风险: 空 PATCH 也触发更新，偏离"仅更新显式字段" ✅ 已修复
- 位置:
  - `backend/app/application/services/user_settings_service.py:72`
  - `backend/app/application/services/user_settings_service.py:108`
  - `backend/app/infrastructure/repositories/user_settings_repository.py:193`
- 问题:
  - 请求体 `{}` 仍会走 `update`，并刷新 `updated_at`。
- 影响:
  - 与 AC3 "Only updates fields that are explicitly provided" 不一致。
- **修复方案**:
  - service 层在 `updates` 为空时直接返回当前 settings（no-op），不进入 update

### 3. 中风险: integration 局部更新被 `connected` 必填约束阻断 ✅ 已修复
- 位置:
  - `backend/app/application/dtos/user_settings_dtos.py:70`
- 问题:
  - `IntegrationConfigDTO.connected` 为必填，导致仅更新 `storeName/region/accountName` 时返回 422。
- 影响:
  - 与 partial update 语义不完全一致。
- **修复方案**:
  - 将 `IntegrationConfigDTO.connected` 设为 `Optional[bool]`，默认 None
  - service 层使用 `exclude_none=True` 确保仅更新提供的字段

### 4. 低风险: 关键回归测试缺口 ✅ 已补充
- 位置:
  - `backend/tests/test_user_settings_repository.py:103`
  - `backend/tests/test_user_settings_api.py:159`
  - `backend/tests/test_user_settings_api.py:229`
- 缺口:
  - ~~缺少并发首次创建（唯一约束冲突回退）测试~~
  - ~~缺少空 PATCH 行为测试~~
  - ~~缺少仅 integration 扩展字段更新测试~~
- **补充测试**:
  - `TestUserSettingsRepositoryConcurrency` - 并发处理和幂等性测试
  - `test_update_integration_extension_fields_only` - 仅更新扩展字段
  - `test_update_settings_empty_patch_no_op` - 空 PATCH 不触发更新
  - `test_update_settings_empty_nested_objects_no_op` - 空嵌套对象不触发更新
  - `test_update_settings_integration_extension_fields_only` - API 层扩展字段更新

## 修复后测试结果
- 命令:
  - `cd backend && poetry run pytest -q tests/test_user_settings_model.py tests/test_user_settings_repository.py tests/test_user_settings_service.py tests/test_user_settings_api.py`
- 结果:
  - `44 passed, 1 warning` (从 36 个测试增加到 44 个)

## 修复状态: ✅ 全部完成
- [x] 修复 repository 并发首次创建的唯一约束冲突处理
- [x] 修复空 PATCH no-op 行为（不触发写入）
- [x] 调整 integration 请求 DTO，支持仅扩展字段更新
- [x] 补齐并发/空 PATCH/integration 局部更新测试
