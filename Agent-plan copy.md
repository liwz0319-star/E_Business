# DeepAgents 电商内容生成系统 - 实施计划 (SOTA版)

## 1. 摘要 (Executive Summary)

基于 **DeepAgents** 架构与 **Agent-native** 原则，构建下一代电商多 Agent 协作系统。该系统由 `DeepOrchestrator` 主导，协调多个专家子 Agent（分析、文案、视觉、视频、QA），实现 "一次上传，自动生成全套营销资产" 的目标。

**核心差异化特性**：
-   **混合状态管理 (Hybrid State)**: 数据库作为业务真相源 (Source of Truth)，文件系统作为执行上下文 (Context) 和中间工件存储。
-   **DeepAgents 编排**: 采用分层规划与执行模式，由 PM (Orchestrator) 制定 Plan，专家 Agent 执行，QA Agent 审核。
-   **视频优先与降级 (Video-First with Fallback)**: 优先使用 MCP 视频生成工具，失败时自动降级为图文转场视频 (Slideshow)。
-   **人机回环 (HITL)**: 关键节点引入人工审批 (Approval)，确保生成质量。
-   **原子化工具 (Atomic Tools)**: 低耦合的基础能力封装，支持灵活组合。

## 2. 现状与目标 (Current vs Target)

| 特性 | 现状 (Current) | 目标 (Target - DeepAgents) |
| :--- | :--- | :--- |
| **架构模式** | 独立 Agent (Copy, Image) | **DeepAgents 编排** (PM + Subagents) |
| **状态管理** | 仅数据库 | **混合模式** (DB + FileSystem Workspace) |
| **协作方式** | 串行/手动 | **并行协作 + 共享工作区** |
| **视频能力** | 无 | **MCP 视频生成 + 自动降级** |
| **质量控制** | 无 | **QA Agent + HITL (人工审批)** |

## 3. 系统架构 (System Architecture)

### 3.1 核心组件图

```mermaid
graph TD
    User[用户] --> API[API Gateway]
    API --> DO[DeepOrchestrator (PM)]
    
    subgraph "Execution Layer (Subagents)"
        DO --> PA[ProductAnalysisSubagent]
        DO --> CW[CopywritingSubagent]
        DO --> IG[ImageSubagent]
        DO --> VG[VideoSubagent]
        DO --> QA[QASubagent]
    end
    
    subgraph "Infrastructure"
        DB[(PostgreSQL)]
        FS[FileSystem Workspace]
        MCP[MCP Constellation]
    end
    
    PA & CW & IG & VG & QA --> FS
    PA & CW & IG & VG --> DB
    IG & VG --> MCP
```

### 3.2 混合状态管理 (Hybrid State)

1.  **数据库 (PostgreSQL)**:
    -   **业务实体**: `ProductPackages`, `VideoAssets`, `Users`.
    -   **用途**: 持久化存储、前端查询、结构化检索。

2.  **文件系统工作区 (FileSystem Workspace)**:
    -   **路径**: `projects/{workflow_id}/` (Agent 的 "大脑")
    -   **结构**:
        ```
        projects/{workflow_id}/
        ├── input/                  # 原始输入
        │   ├── image.jpg
        │   └── context.txt
        ├── workspace/              # 协作区
        │   ├── context.md          # 任务上下文
        │   ├── campaign_plan.md    # 执行计划
        │   └── reflection.md       # Agent反思日志
        └── artifacts/              # 交付物
            ├── copy/               # 文案md
            ├── images/             # 生成图片
            ├── video/              # 生成视频
            └── report/             # QA报告
        ```

## 4. Agent 角色与工作流 (Roles & Workflows)

### 4.1 DeepOrchestrator (Product Manager)
-   **职责**: 接收需求，读取 `input/`，制定 `campaign_plan.md`，分发任务。
-   **LangGraph 工作流**:
    ```
    receive_request -> create_workspace -> plan_task -> 
    delegate(product_analysis) -> delegate(copywriting) -> 
    delegate(image_generation) -> delegate(video_generation) -> 
    delegate(qa_review) -> await_approval
    ```

### 4.2 ProductAnalysisSubagent (Vision Expert)
-   **职责**: 深度分析产品图片。
-   **工作流**:
    ```
    read_image(input/image.jpg) -> analyze_image(vision_api) -> 
    extract_features(keywords, style) -> write_file(workspace/analysis_report.md)
    ```

### 4.3 CopywritingSubagent (Creative Writer)
-   **职责**: 撰写多平台文案。
-   **工作流**:
    ```
    read_file(workspace/campaign_plan.md) -> read_file(workspace/analysis_report.md) ->
    generate_text(product_page) -> generate_text(social_posts) -> 
    write_file(artifacts/copy/*.md)
    ```

### 4.4 ImageSubagent (Visual Designer)
-   **职责**: 生成多场景产品图。
-   **工作流**:
    ```
    read_plan() -> optimize_prompts() -> 
    parallel_generate([hero, lifestyle, detail]) -> 
    save_assets(artifacts/images/) -> record_db(VideoAsset)
    ```

### 4.5 VideoSubagent (Video Producer)
-   **职责**: 制作广告视频 (Video First + Fallback)。
-   **工作流**:
    ```
    try:
        generate_video_mcp(prompt, image) -> save(artifacts/video/ad.mp4)
    except:
        compose_slideshow(images, text) -> save(artifacts/video/fallback.mp4)
    finally:
        record_db(VideoAsset)
    ```

## 5. 原子化工具规范 (Atomic Tool Specification)

所有工具均设计为无状态、原子操作。

### 5.1 FileSystemTools (基础)
-   `read_file(path: str) -> str`: 读取工作区文件
-   `write_file(path: str, content: str) -> bool`: 写入工作区文件
-   `list_dir(path: str) -> list`: 列出文件

### 5.2 TextTools (文本)
-   `generate_text(prompt: str, context: str) -> str`: 调用 LLM 生成文本
-   `extract_keywords(text: str) -> list[str]`: 提取关键词
-   `analyze_image_vision(image_path: str) -> dict`: 调用 Vision API 分析图片

### 5.3 ImageTools (图片)
-   `generate_image(prompt: str, size: str) -> ImageArtifact`: 调用 DALL-E/Midjourney
-   `create_variation(image_path: str) -> ImageArtifact`: 生成变体
-   `save_asset(artifact: Any, user_id: str) -> str`: 保存到 MinIO 并返回 URL

### 5.4 VideoTools (视频)
-   `generate_video(prompt: str, image_path: str) -> VideoArtifact`: 调用 Runway/Sora
-   `create_slideshow(images: list[str], duration: int) -> VideoArtifact`: FFmpeg 合成转场视频

## 6. 详细实施路线图 (Detailed Implementation Steps)

### Phase 1: 核心链路与基础架构 (Core Loop) - 2周

#### Step 1.1: 搭建混合状态基础设施
-   **文件**:
    -   `backend/app/application/tools/filesystem_tools.py` (新建)
    -   `backend/app/application/orchestration/backends.py` (新建: FileSystemBackend)
    -   `backend/app/infrastructure/database/models.py` (更新: ProductPackageModel)
-   **任务**:
    -   实现工作区管理器，负责为每个 `workflow_id` 创建目录结构。
    -   实现 `ProductPackageModel` 及其 Migration。

#### Step 1.2: 实现原子工具层
-   **文件**:
    -   `backend/app/application/tools/text_tools.py` (新建)
    -   `backend/app/application/tools/image_tools.py` (更新)
    -   `backend/app/application/tools/video_tools.py` (新建)
-   **任务**:
    -   封装 `TextTools` 和 `VideoTools` (包含 FFmpeg Fallback 逻辑)。
    -   注册所有工具到 `ToolRegistry`。

#### Step 1.3: 实现 DeepOrchestrator 与 Subagents
-   **文件**:
    -   `backend/app/application/orchestration/deep_orchestrator.py` (新建)
    -   `backend/app/application/agents/product_analysis_agent.py` (新建)
    -   `backend/app/application/agents/subagents.py` (新建: BaseSubagent)
-   **任务**:
    -   实现 PM 的 Plan 制定逻辑 (`campaign_plan.md` 模板)。
    -   实现 Analysis 和 Copywriting Subagents。

#### Step 1.4: 串联 Image 与 Video 生成
-   **文件**:
    -   `backend/app/application/agents/image_generation_agent.py` (更新)
    -   `backend/app/application/agents/video_generation_agent.py` (新建)
-   **任务**:
    -   Image Agent 对接文件系统输入。
    -   Video Agent 实现自动降级逻辑。

### Phase 2: 增强与质控 (Enhancement) - 2周

#### Step 2.1: 实现 QA 与人工审批 (HITL)
-   **文件**:
    -   `backend/app/application/agents/qa_agent.py` (新建)
    -   `backend/app/interface/routes/product_packages.py` (更新: /approve)
-   **任务**:
    -   实现 QA Agent 检查工件完整性。
    -   后端 API 支持挂起任务等待 `/approve`。

#### Step 2.2: 前端工作区集成
-   **文件**:
    -   `services/productPackageService.ts` (新建)
    -   `components/ProductPackageGenerator.tsx` (新建)
-   **任务**:
    -   WebSocket 实时推送文件变更事件。
    -   UI 展示 `Thinking Process` (即文件读写日志)。

### Phase 3: 规模化 (Scale) - 2周
-   **Step 3.1**: 批量任务处理 (CSV Upload -> Queue -> Orchestrator).
-   **Step 3.2**: 成本与性能优化 (Prompt Caching, Parallel Generation).

## 7. 风险管理 (Risk Management)

| 风险 | 缓解措施 |
| :--- | :--- |
| **视频生成失败率高** | 强制实现 Slideshow Fallback (FFmpeg)，确保100%有产出。 |
| **文件系统同步延迟** | 使用 WebSocket 事件驱动更新，而非轮询文件系统。 |
| **Agent 协作死循环** | LangGraph 设置 `recursion_limit`，PM 强制终止异常。 |
| **存储空间膨胀** | 设置 TTL 策略，定期归档/清理旧的 Workspace 文件。 |
