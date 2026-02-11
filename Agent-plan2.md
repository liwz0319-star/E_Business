# SOTA 终版方案：DeepAgents 主导的电商多 Agent 内容生产系统

## 1. 摘要
在现有系统（已完成前端与登录、已上线 `CopywritingAgent` + `ImageAgent` + WebSocket 实时流）基础上，采用 **DeepAgents 主导编排**，落地“一次上传图片+背景文案，产出文案+上架组图+广告视频”的端到端生产线。  
核心策略：**混合状态存储**（数据库为业务真相源，文件工作区为执行上下文与审计工件）+ **MCP 视频优先，失败自动降级**（图文转场视频）。

## 2. 现状与差距（基于代码库客观事实）
1. 已有能力：
- 后端已有 LangGraph 工作流 Agent：`backend/app/application/agents/copywriting_agent.py`、`backend/app/application/agents/image_agent.py`
- 已有鉴权与 WebSocket 事件流：`backend/app/interface/routes/auth.py`、`backend/app/interface/ws/socket_manager.py`
- 前端已接入登录与文本流式思考：`App.tsx`、`services/copywriting.ts`、`services/webSocket.ts`
- 数据库已有 `video_assets` 表：`backend/app/infrastructure/database/models.py`
2. 关键缺口：
- 无统一多 Agent 编排器（目前是两个独立流程）
- 无“产品包”聚合实体（缺 `product_packages` 与状态机）
- 无视频 Agent 与视频路由
- 无工作区文件系统（campaign plan、中间工件、可追溯日志）
- 无 HITL（高风险/高成本动作人工审批）
- 无批量、重生成、A/B、成本治理闭环

## 3. 目标架构（最终形态）
1. 编排层：
- 新增 `DeepOrchestrator`（DeepAgents 主 Agent）
- 子 Agent：`ProductAnalysisSubagent`、`CopywritingSubagent`、`ImageSubagent`、`VideoSubagent`、`QAReviewSubagent`
2. 工具层（原子化）：
- `text.generate`, `text.extract_keywords`, `vision.analyze_product`
- `image.generate`, `image.variation`, `image.save_asset`
- `video.generate`, `video.slideshow_fallback`, `video.save_asset`
- `storage.create_package`, `storage.update_package_status`, `storage.link_asset`
3. 存储层（混合）：
- 数据库：业务主记录、状态、资产索引、审计事件
- 文件工作区：`/workspace/{workflow_id}/` 保存 context、计划、prompt、中间稿、质检报告
4. 执行可靠性：
- Checkpointer + thread_id（可暂停可恢复）
- 节点幂等键与重试策略
- 失败补偿与降级路径（特别是视频）

## 4. 公共 API / 接口 / 类型（决策已锁定）
1. 新增后端路由 `backend/app/interface/routes/product_packages.py`
- `POST /api/v1/product-packages/generate`
- `GET /api/v1/product-packages/status/{workflow_id}`
- `GET /api/v1/product-packages/{package_id}`
- `POST /api/v1/product-packages/{package_id}/regenerate`
- `POST /api/v1/product-packages/{package_id}/approve`（HITL 审批）
2. 新增 DTO
- `ProductPackageRequest { image_url|image_asset_id, background, options }`
- `ProductPackageStatusResponse { workflow_id, status, stage, progress, artifacts, error }`
- `ProductPackageResponse { package_id, analysis, copywriting_versions, images, video, qa_report }`
3. WebSocket 事件扩展（保持兼容现有 `agent:*`）
- 新增 `agent:progress`（0-100 + stage）
- 新增 `agent:artifact`（任一工件生成完成）
- 新增 `agent:approval_required`（HITL）
4. 前端服务与组件
- 新增 `services/productPackageService.ts`
- 新增 `components/ProductPackageGenerator.tsx`
- 新增 `components/PackageResultDisplay.tsx`
- 在 `App.tsx` 中新增“产品包”生成入口并复用已有登录与 WS 通道

## 5. 后端实施蓝图（可直接开工）
1. 基础设施层
- `backend/pyproject.toml` 增加 `deepagents` 依赖
- 新增 `backend/app/application/orchestration/deep_orchestrator.py`
- 新增 `backend/app/application/orchestration/backends.py`（State/Filesystem/Composite backend）
- 新增 `backend/app/application/orchestration/hitl.py`
2. 领域与数据层
- 新增 `ProductPackageModel` 与迁移脚本（关联 `video_assets`）
- 新增 `ProductPackageRepository`
- 新增 `OrchestratorState`、`PackageStatus`、`GenerationPolicy`
3. Agent 与工具层
- 新增 `product_analysis_agent.py`、`video_generation_agent.py`
- 扩展 `image_agent.py` 支持多场景批量生成
- 新增 `application/tools/*` 原子工具注册表
4. 路由与事件层
- 新增 `product_packages.py` 路由
- 扩展 `socket_manager.py` 发送 stage/progress/artifact/approval 事件
5. 兼容策略
- 保留现有 `/copywriting/*` 与 `/images/*`，避免前端回归
- 新路径走统一 orchestrator，老路径逐步内部复用新工具层

## 6. 质量门禁与测试方案
1. 单元测试
- Orchestrator 状态转移、幂等、重试、降级
- 工具层输入校验与异常映射
- Video fallback 合成逻辑
2. 集成测试
- `generate -> status -> result` 全链路
- MCP 视频失败后自动 fallback 成功
- HITL 审批通过/拒绝两条链路
3. E2E 测试
- 登录后上传图片 + 输入背景文案 -> 完整产出
- WS 实时步骤展示与最终结果一致性
- 重生成单模块（仅文案/仅图/仅视频）
4. 非功能测试
- 并发压测（10/30/50 workflow）
- 成本与时延采样（P50/P95）
- 恢复测试（中断后 thread_id 恢复）

## 7. 分阶段交付（建议 3 个里程碑）
1. M1（2 周）
- 单产品包端到端：分析 + 1 版文案 + 3 图 + 视频fallback
- API/WS 打通，可在前端闭环体验
2. M2（2 周）
- MCP 视频优先接入 + 容灾 + HITL 审批 + 重生成
- 质量评估器与 QA 报告
3. M3（2 周）
- A/B 多版本、批量任务、成本治理、运营看板
- 线上可观测性（trace、错误画像、成功率）

## 8. 假设与默认值（已锁定）
1. 编排内核：`DeepAgents主导`
2. 视频策略：`MCP视频优先 + 自动降级`
3. 状态策略：`混合模式（DB 真相源 + 文件工作区）`
4. 兼容策略：保留当前 copywriting/images API，不做破坏性替换
5. 供应商策略：文本继续 DeepSeek；图像复用现有 MCP/Mock；视频抽象为 provider adapter，首版可切换

## 9. 参考依据（MCP 文档）
- Deep Agents Overview: https://docs.langchain.com/oss/python/deepagents/overview
- Deep Agents Customization: https://docs.langchain.com/oss/python/deepagents/customization
- Deep Agents Harness: https://docs.langchain.com/oss/python/deepagents/harness
- Deep Agents Subagents: https://docs.langchain.com/oss/python/deepagents/subagents
- Deep Agents Backends: https://docs.langchain.com/oss/python/deepagents/backends
- Human-in-the-loop: https://docs.langchain.com/oss/python/deepagents/human-in-the-loop
- LangGraph Durable Execution: https://docs.langchain.com/oss/python/langgraph/durable-execution
