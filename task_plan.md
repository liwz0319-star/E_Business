# Task Plan: 修复异步任务中API key环境变量加载失败问题
## Goal
修复E2E测试中发现的"DeepSeek API key is required"错误，使前端WebSocket异步工作流能够正常加载环境变量并成功执行文案生成。

## Current Phase
Phase 3

## Phases

### Phase 1: 深度调研与根本原因分析 ✅
- [x] 理解问题现象和背景
- [x] 探索配置加载机制（config.py）
- [x] 探索异步任务执行流程（copywriting_agent.py）
- [x] 探索WebSocket通信机制
- [x] 确定根本原因：环境加载脆弱性
- **Status:** complete

### Phase 2: 设计解决方案 ✅
- [x] 分析Gemini的深度调研结果
- [x] 确认main.py的启动验证已完成
- [x] 设计config.py的多级路径修复方案
- [x] 设计运行时错误改进方案
- [x] 更新plan2.md文档
- **Status:** complete

### Phase 3: 实施核心修复 ✅
- [x] 修复config.py的env_file搜索路径
- [x] 验证修复后的配置加载
- [x] **Phase 6: 修复全局settings缓存问题**
  - [x] 修改deepseek.py使用动态get_settings()
  - [x] 修改copywriting_agent.py的3处settings使用
  - [x] 修改socket_manager.py使用动态get_settings()
  - [x] 创建验证脚本并测试通过
- **Status:** complete

### Phase 4: 测试与验证 ✅
- [x] 清理环境并重启后端
- [x] 验证启动日志显示配置已加载
- [x] 修复Windows控制台编码问题
- [x] 确认后端服务正常运行
- [ ] 运行完整E2E测试（需要前端配合）
- **Status:** complete (核心验证通过，E2E测试待前端)

### Phase 5: 交付与文档 ✅
- [x] 更新plan2.md的最终状态
- [x] 更新所有计划文件
- [x] 提供验证报告给用户
- **Status:** complete

## Key Questions
1. ✅ 为什么直接API调用成功但WebSocket工作流失败？
   - 答：环境加载脆弱性，单一`.env`路径在不同执行上下文中不可靠

2. ✅ main.py的启动验证是否已经实现？
   - 答：是，已经在第28-60行实现

3. ⚠️ config.py的修复能否解决问题？
   - 答：需要测试验证，但理论上应该能解决

## Decisions Made
| Decision | Rationale |
|----------|-----------|
| 采用多级路径策略 | 大大提高在不同环境下找到配置文件的成功率 |
| 保留所有fallback路径 | 确保向后兼容性 |
| 启动时强制验证 | Fail Fast原则，避免服务在错误状态下运行 |
| 分步实施 | 先修复核心问题（config.py），再增强错误处理 |

## Errors Encountered
| Error | Attempt | Resolution |
|-------|---------|------------|
| "DeepSeek API key is required" in async tasks | 1 | 确认根本原因：env_file路径不包含backend/.env |
| 同上 | 2 | 设计多级路径解决方案 |

## Notes
- 核心修复只涉及一个文件：`backend/app/core/config.py`
- main.py的启动验证已完成，无需修改
- 修复后必须重启后端并观察启动日志
- E2E测试是最终验证标准
