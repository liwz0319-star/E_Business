# DeepAgents 电商内容生产系统 - 决策完整实施计划（交接版）

版本：v1.0（决策锁定）  
日期：2026-02-10  
目标读者：后续实施 Agent / 工程师

---

## 1. 文档定位与完成定义

本文件是后续实现阶段的唯一执行规范，目标是让实施方不再做架构级决策，只执行。

完成定义（Definition of Done）：
1. 后端新增 `/api/v1/product-packages/*` 全链路可用，旧 `/copywriting/*` 与 `/images/*` 无回归。
2. 单次请求可产出文案、图片、视频（视频失败自动走 Slideshow Fallback）。
3. 过程状态可通过 REST + WebSocket 查询，支持 HITL 审批与重生成。
4. 产物与状态同时落到 DB（真相源）与工作区文件系统（上下文/审计）。
5. 测试矩阵通过（单元、集成、E2E、关键非功能项）。

---

## 2. 基于仓库的客观现状（2026-02-10）

已存在能力：
1. 路由与工作流
- 文案路由：`backend/app/interface/routes/copywriting.py`
- 图片路由：`backend/app/interface/routes/images.py`
- 现有 Agent：`backend/app/application/agents/copywriting_agent.py`、`backend/app/application/agents/image_agent.py`

2. 实时事件
- Socket 管理：`backend/app/interface/ws/socket_manager.py`
- 已有事件：`agent:thought`、`agent:tool_call`、`agent:result`、`agent:error`

3. 数据层
- `VideoAssetModel` 已存在：`backend/app/infrastructure/database/models.py`
- `ProductPackageModel` 已定义在模型中，但尚未有对应 Alembic 迁移
- 现有迁移仅到 `002_create_video_assets_table.py`

4. 前端
- 已有登录、文案流式展示、WS 订阅：`App.tsx`、`services/copywriting.ts`、`services/webSocket.ts`

当前明确缺口：
1. 无统一编排器（DeepOrchestrator）。
2. 无产品包 API/DTO。
3. 无视频 Agent 与视频路由编排。
4. 无工作区文件系统工具层。
5. 无 HITL 审批闭环。
6. 现有 `ProductPackageRepository` 为同步 Session，与项目 AsyncSession 主路径不一致。

---

## 3. 本版对上轮问题的修正结论

1. 决策完整性修正
- 补齐并锁定：公共 API/DTO、状态机、数据模型、测试门禁、里程碑、假设默认值、发布回滚。

2. 语义错误修正
- 图片子流程中持久化实体从错误的 `VideoAsset` 语义修正为“图片资产写入 `video_assets` 表，`asset_type='image'`”。

3. 路径一致性修正
- 保留并扩展现有 `backend/app/application/agents/image_agent.py`，不再使用 `image_generation_agent.py` 命名。
- `backend/app/interface/routes/product_packages.py` 标注为“新建”，不是“更新”。

4. 工具分层修正
- 将视觉分析从 `TextTools` 移出，独立为 `VisionTools`，避免职责混淆。

---

## 4. 范围与非范围（锁定）

In Scope（本次必须完成）：
1. DeepOrchestrator + 5 个子 Agent（分析/文案/图片/视频/QA）。
2. 产品包 API、DTO、WS 扩展事件。
3. 混合状态（DB + 工作区文件系统）。
4. 视频优先 + fallback。
5. HITL 审批、重生成（copy/images/video/all）。
6. 前端最小可用闭环页面与结果展示。

Out of Scope（本次不做）：
1. 多租户计费系统。
2. 运营 BI 看板与复杂报表。
3. 批量 CSV 任务大规模调度（只保留接口预留，不在本次实现）。

---

## 5. 目标架构与模块边界（锁定）

### 5.1 编排层

主编排器：`DeepOrchestrator`  
路径：`backend/app/application/orchestration/deep_orchestrator.py`

职责：
1. 创建工作区与产品包主记录。
2. 按状态机调度子 Agent。
3. 维护进度、失败重试、fallback。
4. 触发 HITL 节点。
5. 输出最终聚合结果。

### 5.2 子 Agent 列表

1. `ProductAnalysisSubagent`（新建）  
`backend/app/application/agents/product_analysis_agent.py`
2. `CopywritingSubagent`（封装复用现有 CopywritingAgent）  
`backend/app/application/agents/subagents.py`
3. `ImageSubagent`（封装复用现有 ImageAgent）  
`backend/app/application/agents/subagents.py`
4. `VideoSubagent`（新建）  
`backend/app/application/agents/video_generation_agent.py`
5. `QASubagent`（新建）  
`backend/app/application/agents/qa_agent.py`

### 5.3 状态机（锁定）

`status` 枚举：
- `pending`、`running`、`approval_required`、`completed`、`failed`、`cancelled`

`stage` 枚举：
- `init`、`analysis`、`copywriting`、`image_generation`、`video_generation`、`qa_review`、`approval`、`done`

合法流转：
1. `pending/init -> running/analysis`
2. `running/analysis -> running/copywriting`
3. `running/copywriting -> running/image_generation`
4. `running/image_generation -> running/video_generation`
5. `running/video_generation -> running/qa_review`
6. `running/qa_review -> approval_required/approval`（默认）
7. `approval_required/approval -> completed/done`（审批通过）
8. 任意运行阶段可到 `failed/<当前stage>`
9. 任意未完成阶段可到 `cancelled/<当前stage>`

### 5.4 工作区结构（锁定）

根目录：`backend/projects/{workflow_id}/`

```
backend/projects/{workflow_id}/
├── input/
│   ├── image_source.json
│   └── context.txt
├── workspace/
│   ├── context.md
│   ├── campaign_plan.md
│   ├── analysis_report.md
│   ├── qa_report.md
│   └── reflection.md
├── artifacts/
│   ├── copy/
│   │   ├── product_page_v1.md
│   │   ├── social_post_v1.md
│   │   └── ad_short_v1.md
│   ├── images/
│   │   ├── hero.png
│   │   ├── lifestyle.png
│   │   └── detail.png
│   └── video/
│       ├── ad.mp4
│       └── fallback.mp4
└── logs/
    └── execution.jsonl
```

清理策略：
- `completed` 或 `failed` 后保留 7 天，再归档/清理。

---

## 6. 公共 API / DTO 规范（锁定）

后端新建路由：`backend/app/interface/routes/product_packages.py`  
路由前缀：`/api/v1/product-packages`  
鉴权：全部接口必须 `Depends(get_current_user)`。

### 6.1 REST 接口

1. `POST /generate`
- 作用：启动产品包生成工作流
- 返回：`202 Accepted`

2. `GET /status/{workflow_id}`
- 作用：查询工作流状态与阶段
- 返回：`200 OK`

3. `GET /{package_id}`
- 作用：获取聚合结果详情
- 返回：`200 OK`

4. `POST /{package_id}/regenerate`
- 作用：局部或全量重生成
- 返回：`202 Accepted`

5. `POST /{package_id}/approve`
- 作用：HITL 审批通过/拒绝
- 返回：`200 OK`

### 6.2 DTO（Pydantic，字段锁定）

新增文件：`backend/app/application/dtos/product_packages.py`

```python
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field, HttpUrl, model_validator

class ProductPackageOptions(BaseModel):
    copy_variants: int = Field(default=2, ge=1, le=5)
    image_variants: int = Field(default=3, ge=1, le=8)
    video_duration_sec: int = Field(default=15, ge=6, le=60)
    require_approval: bool = True
    force_fallback_video: bool = False

class ProductPackageRequest(BaseModel):
    image_url: HttpUrl | None = None
    image_asset_id: UUID | None = None
    background: str = Field(..., min_length=1, max_length=4000)
    options: ProductPackageOptions = ProductPackageOptions()

    @model_validator(mode='after')
    def check_image_source(self):
        if bool(self.image_url) == bool(self.image_asset_id):
            raise ValueError('Exactly one of image_url or image_asset_id is required')
        return self

class ProductPackageGenerateResponse(BaseModel):
    package_id: UUID
    workflow_id: str
    status: str
    stage: str

class ProductPackageStatusResponse(BaseModel):
    package_id: UUID
    workflow_id: str
    status: str
    stage: str
    progress_percentage: int = Field(ge=0, le=100)
    current_step: str
    artifacts: dict
    error: str | None = None

class ProductPackageResponse(BaseModel):
    package_id: UUID
    workflow_id: str
    status: str
    stage: str
    analysis: dict
    copywriting_versions: list[dict]
    images: list[dict]
    video: dict | None
    qa_report: dict | None

class RegenerateRequest(BaseModel):
    target: Literal['copywriting', 'images', 'video', 'all']
    reason: str | None = Field(default=None, max_length=500)

class ApproveRequest(BaseModel):
    decision: Literal['approve', 'reject']
    comment: str | None = Field(default=None, max_length=500)
```

### 6.3 错误码（锁定）

统一错误码：
1. `PKG_VALIDATION_ERROR`：请求参数非法。
2. `PKG_NOT_FOUND`：package/workflow 不存在。
3. `PKG_STATUS_CONFLICT`：状态不允许当前操作。
4. `PKG_APPROVAL_REQUIRED`：请求结果前需先审批。
5. `PKG_PROVIDER_FAILED`：外部生成器失败。
6. `PKG_INTERNAL_ERROR`：未分类内部错误。

---

## 7. WebSocket 事件协议（锁定）

兼容保留旧事件：
- `agent:thought`、`agent:tool_call`、`agent:result`、`agent:error`

新增事件：
1. `agent:progress`
```json
{
  "type": "progress",
  "workflowId": "wf-xxx",
  "data": {
    "stage": "image_generation",
    "percentage": 55,
    "current_step": "generate_lifestyle_image"
  },
  "timestamp": "2026-02-10T12:00:00Z"
}
```

2. `agent:artifact`
```json
{
  "type": "artifact",
  "workflowId": "wf-xxx",
  "data": {
    "artifact_type": "image",
    "artifact_id": "uuid-or-int",
    "url": "https://...",
    "label": "hero"
  },
  "timestamp": "2026-02-10T12:00:01Z"
}
```

3. `agent:approval_required`
```json
{
  "type": "approval_required",
  "workflowId": "wf-xxx",
  "data": {
    "package_id": "uuid",
    "reason": "qa_score_below_threshold",
    "qa_score": 0.74
  },
  "timestamp": "2026-02-10T12:00:02Z"
}
```

后端改动文件：`backend/app/interface/ws/socket_manager.py`  
前端改动文件：`services/webSocket.ts`

---

## 8. 数据模型与迁移规范（锁定）

### 8.1 ProductPackageModel 最终字段（锁定）

更新文件：`backend/app/infrastructure/database/models.py`

字段规范：
1. `id: UUID`（PK）
2. `workflow_id: String(64)`（unique + index）
3. `status: String(50)`（默认 `pending`）
4. `stage: String(50)`（默认 `init`）
5. `progress: JSON`（默认 `{ "percentage":0, "current_step":"init" }`）
6. `input_data: JSON nullable`
7. `analysis_data: JSON nullable`
8. `artifacts: JSON`（默认 `{}`）
9. `approval_status: String(50)`（默认 `pending`）
10. `qa_report: JSON nullable`
11. `user_id: UUID`（index，非空）
12. `error_message: Text nullable`
13. `created_at: DateTime`
14. `updated_at: DateTime`
15. `completed_at: DateTime nullable`

关键修正：
- `user_id` 统一为 UUID，和 `auth` 体系保持一致。

### 8.2 仓储层统一异步（锁定）

更新文件：`backend/app/infrastructure/repositories/product_package_repository.py`

必须改为 `AsyncSession` + async 方法：
1. `async create(...)`
2. `async get_by_workflow_id(...)`
3. `async get_by_id(...)`
4. `async update_status(...)`
5. `async add_artifact(...)`
6. `async update_approval(...)`

### 8.3 Alembic 迁移（锁定）

新建：`backend/app/alembic/versions/003_sync_product_packages_schema.py`

迁移策略：
1. 若 `product_packages` 表不存在，则创建完整表与索引。
2. 若已存在，则执行 schema 对齐：
- 确保 `user_id` 类型为 UUID（必要时新增临时列迁移数据后替换）
- 补齐缺失字段：`error_message`
- 补齐索引：`workflow_id` 唯一索引、`user_id` 普通索引

---

## 9. 原子工具规范（Atomic Tool Specification，锁定）

新增目录：`backend/app/application/tools/`

### 9.1 FileSystemTools

文件：`filesystem_tools.py`

```python
class FileSystemTools:
    def create_workspace(self, workflow_id: str) -> str: ...
    def ensure_dir(self, path: str) -> None: ...
    def read_file(self, path: str) -> str: ...
    def write_file(self, path: str, content: str) -> None: ...
    def write_json(self, path: str, payload: dict) -> None: ...
    def list_dir(self, path: str, recursive: bool = False) -> list[str]: ...
    def exists(self, path: str) -> bool: ...
```

约束：
1. 仅允许读写 `backend/projects/{workflow_id}/` 下路径。
2. 非法路径（越界）抛 `ValueError`。

### 9.2 TextTools

文件：`text_tools.py`

```python
class TextTools:
    async def generate_text(
        self,
        prompt: str,
        context: str | None = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ) -> str: ...

    def extract_keywords(self, text: str, top_k: int = 10) -> list[str]: ...
```

### 9.3 VisionTools（从 TextTools 拆分）

文件：`vision_tools.py`

```python
class VisionTools:
    async def analyze_product_image(self, image_path: str) -> dict: ...
```

输出最小结构：
```json
{
  "category": "...",
  "style": "...",
  "materials": ["..."],
  "key_features": ["..."],
  "suggested_scenes": ["hero", "lifestyle", "detail"]
}
```

### 9.4 ImageTools

文件：`image_tools.py`

```python
class ImageTools:
    async def generate_image(self, prompt: str, width: int, height: int) -> dict: ...
    async def create_variation(self, image_path: str, prompt: str | None = None) -> dict: ...
    async def save_asset(self, artifact: dict, user_id: str, workflow_id: str) -> dict: ...
```

约束：
- `save_asset` 最终必须写入 `video_assets`，并将 `asset_type='image'`。

### 9.5 VideoTools

文件：`video_tools.py`

```python
class VideoTools:
    async def generate_video(
        self,
        prompt: str,
        image_paths: list[str],
        duration_sec: int,
    ) -> dict: ...

    async def create_slideshow(
        self,
        images: list[str],
        captions: list[str],
        duration_sec: int,
    ) -> dict: ...

    async def save_asset(self, artifact: dict, user_id: str, workflow_id: str) -> dict: ...
```

策略锁定：
1. 先尝试 `generate_video`。
2. 异常或超时（30 秒）立即 fallback 到 `create_slideshow`。
3. 无论主路径或 fallback，最终都写入 `video_assets`，并标注 `asset_type='video'`。

### 9.6 StorageTools

文件：`storage_tools.py`

```python
class StorageTools:
    async def create_package(self, data: dict) -> dict: ...
    async def update_package_status(
        self,
        package_id: str,
        status: str,
        stage: str,
        progress: dict,
        error_message: str | None = None,
    ) -> dict: ...
    async def link_asset(self, package_id: str, artifact_type: str, artifact_id: str) -> dict: ...
```

---

## 10. Agent 工作流伪代码（锁定）

### 10.1 DeepOrchestrator

```python
async def run(request, user_id):
    workflow_id = new_uuid()
    workspace = fs.create_workspace(workflow_id)

    package = await storage.create_package({
        "workflow_id": workflow_id,
        "user_id": user_id,
        "status": "running",
        "stage": "analysis",
        "input_data": request,
    })

    emit_progress(workflow_id, "analysis", 10, "start_analysis")
    analysis = await analysis_agent.run(request, workspace)
    await storage.update_package_status(package.id, "running", "copywriting", {"percentage": 25, "current_step": "copywriting"})

    copy_assets = await copy_agent.run(analysis, request, workspace)
    emit_artifact(copy_assets)

    await storage.update_package_status(package.id, "running", "image_generation", {"percentage": 45, "current_step": "image_generation"})
    image_assets = await image_agent.run(analysis, request, workspace)
    emit_artifact(image_assets)

    await storage.update_package_status(package.id, "running", "video_generation", {"percentage": 65, "current_step": "video_generation"})
    video_asset = await video_agent.run(analysis, image_assets, request, workspace)  # 内含 fallback
    emit_artifact(video_asset)

    await storage.update_package_status(package.id, "running", "qa_review", {"percentage": 85, "current_step": "qa_review"})
    qa_report = await qa_agent.run(analysis, copy_assets, image_assets, video_asset, workspace)

    if request.options.require_approval:
        await storage.update_package_status(package.id, "approval_required", "approval", {"percentage": 95, "current_step": "waiting_approval"})
        emit_approval_required(...)
        return

    await finalize_completed(package.id, workflow_id)
```

### 10.2 ProductAnalysisSubagent

```python
async def run(request, workspace):
    source_image = resolve_input_image(request)
    result = await vision_tools.analyze_product_image(source_image)
    fs.write_file(f"{workspace}/workspace/analysis_report.md", render_markdown(result))
    return result
```

### 10.3 CopywritingSubagent

```python
async def run(analysis, request, workspace):
    plan = await text_tools.generate_text(prompt=build_campaign_plan_prompt(...))
    fs.write_file("workspace/campaign_plan.md", plan)

    outputs = []
    for channel in ["product_page", "social_post", "ad_short"]:
        text = await text_tools.generate_text(prompt=build_copy_prompt(channel, analysis, request.background))
        path = save_copy_file(channel, text)
        outputs.append({"channel": channel, "path": path, "content": text})
    return outputs
```

### 10.4 ImageSubagent

```python
async def run(analysis, request, workspace):
    scenes = ["hero", "lifestyle", "detail"]
    results = []
    for scene in scenes:
        prompt = build_image_prompt(scene, analysis, request.background)
        artifact = await image_tools.generate_image(prompt, width=1024, height=1024)
        saved = await image_tools.save_asset(artifact, user_id=request.user_id, workflow_id=request.workflow_id)
        results.append({"scene": scene, **saved})
    return results
```

### 10.5 VideoSubagent

```python
async def run(analysis, image_assets, request, workspace):
    prompt = build_video_prompt(analysis, request.background)
    try:
        artifact = await video_tools.generate_video(prompt, image_paths=extract_paths(image_assets), duration_sec=request.options.video_duration_sec)
        artifact["is_fallback"] = False
    except Exception:
        artifact = await video_tools.create_slideshow(images=extract_paths(image_assets), captions=build_slides_text(...), duration_sec=request.options.video_duration_sec)
        artifact["is_fallback"] = True

    saved = await video_tools.save_asset(artifact, user_id=request.user_id, workflow_id=request.workflow_id)
    return saved
```

### 10.6 QASubagent

```python
async def run(analysis, copy_assets, image_assets, video_asset, workspace):
    checks = run_quality_checks(...)
    score = compute_score(checks)
    report = {"score": score, "issues": checks.issues, "suggestions": checks.suggestions}
    fs.write_json("workspace/qa_report.md", report)
    return report
```

---

## 11. 详细实施步骤（决策级）

### Phase 1（后端核心链路，2 周）

#### Step 1.1 数据层对齐

文件：
- 更新 `backend/app/infrastructure/database/models.py`
- 新建 `backend/app/alembic/versions/003_sync_product_packages_schema.py`
- 更新 `backend/app/infrastructure/repositories/product_package_repository.py`

任务：
1. 对齐 `ProductPackageModel` 字段与类型（尤其 `user_id: UUID`）。
2. 产出可重复执行的 schema 同步迁移。
3. 仓储改成 AsyncSession。

DoD：
- 迁移在空库与已有库都可执行。
- 仓储单元测试通过。

#### Step 1.2 工具层落地

文件：
- 新建 `backend/app/application/tools/filesystem_tools.py`
- 新建 `backend/app/application/tools/text_tools.py`
- 新建 `backend/app/application/tools/vision_tools.py`
- 更新 `backend/app/application/tools/image_tools.py`
- 新建 `backend/app/application/tools/video_tools.py`
- 新建 `backend/app/application/tools/storage_tools.py`
- 新建 `backend/app/application/tools/tool_registry.py`

任务：
1. 完成原子工具实现与统一异常映射。
2. 对外暴露 `ToolRegistry` 注入接口。

DoD：
- 工具层单元测试全绿。

#### Step 1.3 编排器与子 Agent

文件：
- 新建 `backend/app/application/orchestration/deep_orchestrator.py`
- 新建 `backend/app/application/orchestration/backends.py`
- 新建 `backend/app/application/orchestration/hitl.py`
- 新建 `backend/app/application/agents/product_analysis_agent.py`
- 新建 `backend/app/application/agents/video_generation_agent.py`
- 新建 `backend/app/application/agents/qa_agent.py`
- 新建 `backend/app/application/agents/subagents.py`
- 更新 `backend/app/application/agents/image_agent.py`（仅做适配，不改文件名）

任务：
1. 实现状态机调度、幂等、重试、fallback。
2. 复用现有文案/图片能力，通过适配器接入。

DoD：
- `generate -> status` 链路可跑通。

#### Step 1.4 API 与事件层

文件：
- 新建 `backend/app/application/dtos/product_packages.py`
- 新建 `backend/app/interface/routes/product_packages.py`
- 更新 `backend/app/interface/routes/__init__.py`
- 更新 `backend/app/main.py`
- 更新 `backend/app/interface/ws/socket_manager.py`

任务：
1. 实现 5 个产品包接口。
2. 增加 3 个 WS 事件。

DoD：
- OpenAPI 文档可见新接口。
- WS 可收到 progress/artifact/approval_required。

### Phase 2（前端闭环，2 周）

#### Step 2.1 前端服务层

文件：
- 新建 `services/productPackageService.ts`
- 更新 `services/webSocket.ts`

任务：
1. 新增产品包 API 调用。
2. 扩展 WS 事件类型与订阅处理。

#### Step 2.2 前端组件层

文件：
- 新建 `components/ProductPackageGenerator.tsx`
- 新建 `components/PackageResultDisplay.tsx`
- 新建 `components/PackageProgressPanel.tsx`
- 更新 `App.tsx`

任务：
1. 增加“产品包生成”入口。
2. 展示过程进度与最终工件。
3. 支持审批与重生成操作。

DoD：
- 登录后可完整跑通一次产品包生成。

### Phase 3（增强与稳定，2 周）

#### Step 3.1 质量与可观测性

文件：
- 更新 `backend/app/core/config.py`
- 更新 `.env.example`

新增配置：
1. `ENABLE_PRODUCT_PACKAGE_FLOW=true`
2. `VIDEO_PROVIDER=mock`（可切换）
3. `VIDEO_TIMEOUT_SECONDS=30`
4. `WORKSPACE_TTL_DAYS=7`

#### Step 3.2 稳定性与成本治理

任务：
1. 增加关键阶段耗时、失败率日志。
2. 限制并发（默认每用户 3 个并行 workflow）。

---

## 12. 测试计划与用例（锁定）

### 12.1 后端单元测试

新增：
1. `backend/tests/application/tools/test_filesystem_tools.py`
2. `backend/tests/application/tools/test_text_tools.py`
3. `backend/tests/application/tools/test_vision_tools.py`
4. `backend/tests/application/tools/test_video_tools.py`
5. `backend/tests/application/orchestration/test_deep_orchestrator.py`

覆盖点：
1. 状态流转合法性。
2. 幂等与重试。
3. 视频 fallback。
4. 审批挂起与恢复。

### 12.2 后端集成测试

新增：
1. `backend/tests/interface/routes/test_product_packages.py`

场景：
1. `POST /generate` 参数校验。
2. `GET /status/{workflow_id}` 状态推进。
3. `POST /{id}/approve` approve/reject 分支。
4. `POST /{id}/regenerate` 各 target 分支。

### 12.3 E2E 测试

新增：
1. `backend/tests/e2e/test_product_package_workflow_e2e.py`

场景：
1. 正常路径：analysis -> copy -> images -> video -> qa -> approval -> completed。
2. 视频失败路径：自动 fallback 成功。
3. 中途取消路径：状态变为 cancelled。

### 12.4 前端测试

新增：
1. `services/productPackageService.test.ts`
2. `services/webSocket.product-package.test.ts`
3. `components/ProductPackageGenerator.test.tsx`
4. `components/PackageResultDisplay.test.tsx`

### 12.5 测试命令

1. `cd backend && poetry run pytest -q`
2. `npm run test:run`

---

## 13. 验收标准（必须全部满足）

1. 功能
- 单请求生成完整产品包（文案+图+视频）。
- 视频主路径失败时 fallback 成功，最终仍有视频产物。
- 审批通过可完成，审批拒绝可回到重生成流程。

2. 兼容
- `/api/v1/copywriting/*` 和 `/api/v1/images/*` 既有行为不变。
- 旧前端文案流不受影响。

3. 可观测
- 每个 workflow 在 DB 与工作区可追踪。
- WS 与 REST 状态一致。

4. 稳定
- 10 并发 workflow 下成功率 >= 95%。
- P95 完成时间（mock provider）<= 90 秒。

---

## 14. 发布与回滚（锁定）

发布策略：
1. 默认关闭 `ENABLE_PRODUCT_PACKAGE_FLOW`。
2. 灰度开启（开发 -> 测试 -> 生产）。

回滚策略：
1. 关闭 `ENABLE_PRODUCT_PACKAGE_FLOW` 即可停止新流量。
2. 保留旧路由，确保最小业务可用。
3. 不执行破坏性回滚迁移；数据保留。

---

## 15. 假设与默认值（锁定）

1. 编排内核：使用现有 `langgraph` 实现 DeepAgents 模式，不新增不确定第三方编排依赖。
2. 文本模型：继续 DeepSeek。
3. 图片生成：沿用现有 `ImageAgent` + provider factory。
4. 视频策略：视频优先，30 秒超时或异常即 fallback。
5. HITL：默认开启（`require_approval=true`）。
6. 产物数量默认：2 版文案、3 张图片、1 支 15s 视频。
7. 工作区 TTL：7 天。
8. 鉴权：全部产品包接口必须登录。

---

## 16. 交接执行顺序（给后续 Agent）

严格按顺序执行：
1. Step 1.1（数据层）
2. Step 1.2（工具层）
3. Step 1.3（编排层）
4. Step 1.4（API/WS）
5. Step 2.1（前端服务）
6. Step 2.2（前端页面）
7. Step 3.1/3.2（稳定性）

每步完成后必须提交：
1. 变更文件清单
2. 通过的测试命令与结果
3. 风险与剩余问题

---

## 17. 关键修订摘要（相对 Agent-plan.md）

1. 补全缺失的“API/DTO/测试门禁/验收/回滚/假设”决策章节。  
2. 修正路径与语义不一致：
- `image_generation_agent.py` -> 统一为现有 `image_agent.py` 扩展
- `product_packages.py` 定义为新建
- 图片资产记录语义统一为 `asset_type='image'`
3. 原子工具分层重构：新增 `VisionTools`，避免 `TextTools` 混入视觉职责。
4. 仓储层统一异步，消除 Sync/Async 混用风险。

> 以上条目均已锁定，不再留给实施方二次决策。
