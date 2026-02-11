# 架构设计：多 Agent 电商内容生成系统

## 1. 目标描述 (Goal Description)
设计一个稳健的、"Agent-native"（Agent 原生）的多 Agent 系统，用于自动生成电商内容。
**输入**：产品图片，背景描述/文案。
**输出**：产品描述（文案），产品图片（生活照/棚拍），产品视频（广告）。

**核心理念**：
1.  **Agent-native**: Agent 使用共享的文件系统工作区作为其主要接口和记忆。
2.  **DeepAgents 模式**: 使用分层规划器（产品经理）配合专业子 Agent。
3.  **透明性**: 所有 Agent 的状态和中间产物（Artifacts）在文件系统中可见。

## 用户审查 (User Review Required)
> [!IMPORTANT]
> 本设计引入了基于文件系统的状态管理方法 (Agent-native)。这与传统的以数据库为中心的架构不同。请确认是否符合预期。

## 2. 系统架构 (System Architecture)

### 2.1 Agent 层级 (The Team)
我们将模拟一个创意工作室的团队结构：

1.  **产品经理 (Product Manager - Root Agent / Orchestrator)**
    *   **角色**: 分析输入，创建 `campaign_plan.md`（营销计划），并将任务分配给专家。
    *   **能力**: `read_brief`（读取简报）, `write_plan`（撰写计划）, `delegate_task`（分配任务）, `review_output`（审查产出）。
    *   **框架**: LangGraph + DeepAgents (Planner Node)。

2.  **文案 (Copywriter - Sub-agent)**
    *   **角色**: 撰写营销文案、SEO 描述和视频脚本。
    *   **输入**: `campaign_plan.md`, `brief.md`。
    *   **输出**: `copy/description.md`, `copy/scripts.md`。
    *   **工具**: `search_trends` (可选), `write_file`。

3.  **视觉设计师 (Visual Designer - Sub-agent)**
    *   **角色**: 生成和编辑产品图片。
    *   **输入**: `copy/description.md`, 原始产品图片。
    *   **输出**: `marketing_images/*.png`。
    *   **工具**: `image_generation_tool` (MCP), `image_editing_tool`。

4.  **视频制作人 (Video Producer - Sub-agent)**
    *   **角色**: 将素材汇编成短视频广告。
    *   **输入**: `copy/scripts.md`, `marketing_images/*.png`。
    *   **输出**: `videos/ad_campaign.mp4`。
    *   **工具**: `video_generation_tool` (MCP)。

### 2.2 共享工作区结构 (File System)
Agent 在特定项目目录下协作。

```
projects/{projectId}/
├── input/
│   ├── raw_product_image.jpg
│   └── context.txt (用户原始输入)
├── workspace/ (共享记忆)
│   ├── context.md          # "Context.md" 模式的实现 (当前状态, 指导方针)
│   ├── campaign_plan.md    # PM 创建的总计划
│   ├── status.json         # 供 UI 轮询的机器可读状态
│   └── conversation_log.md # Agent 交互调试日志
├── artifacts/ (交付物)
│   ├── copy/
│   │   ├── product_page.md
│   │   └── social_posts.md
│   ├── images/
│   │   ├── lifestyle_01.png
│   │   └── studio_01.png
│   └── videos/
│       └── promo_reel.mp4
```

### 2.3 工作流 (The Logical Loop)

1.  **初始化**:
    *   用户创建项目 -> 后端初始化目录结构。
    *   后端创建包含初始需求的 `workspace/context.md`。

2.  **规划阶段 (PM Agent)**:
    *   PM 读取 `input/` 和 `workspace/context.md`。
    *   PM 生成 `workspace/campaign_plan.md`，概述切入点、目标受众和所需素材。
    *   PM 更新 `context.md` 状态为 "PLANNING_COMPLETE"。

3.  **执行阶段 (并行/串行)**:
    *   **步骤 1: 文案**: PM 分配给 **Copywriter**。
        *   Copywriter 读取计划，在 `artifacts/copy/` 中生成文本。
    *   **步骤 2: 视觉**: PM 分配给 **Visual Designer**。
        *   Designer 读取计划和文案，在 `artifacts/images/` 中生成图片。
    *   **步骤 3: 视频**: PM 分配给 **Video Producer**。
        *   Producer 使用图片和脚本生成 `artifacts/videos/`。

4.  **审查与交付**:
    *   PM 审查文件是否存在。
    *   PM 在 `status.json` 中将项目标记为 "COMPLETED"。
    *   前端 (响应 WebSocket/轮询) 更新 UI。

## 3. 技术栈适配 (DeepAgents + LangChain)

*   **后端**: Python (`backend/app`)。
*   **编排**: LangGraph。
    *   状态 Schema: `AgentState` (messages, next_step, file_system_context)。
*   **工具**:
    *   **FileSystemTools**: `ReadFile`, `WriteFile`, `ListDir` (标准 DeepAgents 集合)。
    *   **GenerativeTools**: `GenerateImage` (DALL-E/Midjourney via MCP), `GenerateVideo` (Runway/Sora via MCP)。
*   **前端**: 现有 React App。
    *   **集成**: 更新 `ThinkingLog` 以可视化 `read_file`/`write_file` 活动。

## 4. 实施步骤 (Plan)

### 第一阶段：基础设施 (Infrastructure)
1.  设置带有文件系统工具的 `DeepAgent` 基类。
2.  实现 `SharedWorkspaceManager` 以处理目录创建。

### 第二阶段：Agent 开发 (Agents)
1.  实现 **Copywriter** (仅文本)。
2.  实现 **Designer** (集成图像生成)。
3.  实现 **Producer** (集成视频生成)。
4.  实现 **PM** (编排逻辑)。

### 第三阶段：集成 (Integration)
1.  将 Agent 连接到 `main.py` API 端点。
2.  通过 WebSocket 连接前端，以流式传输文件系统更新（例如，“Agent PM 正在编写 campaign_plan.md...”）。

## 5. 详细 Agent 设计 (Prompt Engineering)

### 5.1 产品经理 (PM)
**System Prompt:**
```markdown
你是电商创意工作室的首席产品经理。
你的目标是协调完成全套产品发布包的制作。

**你的能力:**
- `read_file(path)`: 审查简报、计划和产出。
- `write_file(path, content)`: 创建总计划并更新状态。
- `delegate_task(agent_name, instructions)`: 将工作移交给专家。

**工作流:**
1.  读取 `input/context.txt` 和 `input/` 中的任何图片。
2.  创建一个详细的 `workspace/campaign_plan.md`。必须包含：
    -   目标受众与品牌调性。
    -   关键卖点。
    -   视觉方向 (Moodboard 描述)。
    -   所需素材清单。
3.  委托 `Copywriter` 根据计划创建文本素材。
4.  委托 `Designer` 根据计划*和*文案创建图片。
5.  委托 `VideoProducer` 使用新图片和脚本创建视频。
6.  审查 `artifacts/` 中的所有产出。如有缺失，重新委托。
7.  更新 `workspace/status.json` 为 "COMPLETED"。
```

### 5.2 文案 Agent (Copywriter)
**System Prompt:**
```markdown
你是一名资深文案，专精于高转化率的电商文本。
你的目标是撰写引人注目的产品描述和脚本。

**你的上下文:**
- 你在 `projects/{id}/` 中工作。
- 阅读 `workspace/campaign_plan.md` 获取指导。

**指令:**
1.  使用 `read_file` 读取计划。
2.  使用 `write_file` 在 `artifacts/copy/product_page.md` 撰写 Markdown 格式的产品页描述。
    -   包含：标题、特性、优势、SEO 关键词。
3.  使用 `write_file` 在 `artifacts/copy/video_script.md` 撰写 15 秒视频脚本。
    -   格式: [场景] [音频/文本] [视觉提示]。
4.  完成后向 PM 汇报。
```

### 5.3 设计师 Agent (Designer)
**System Prompt:**
```markdown
你是一名首席视觉设计师。
你的目标是使用 AI 生成工具创造令人惊叹的产品图像。

**你的上下文:**
- 阅读 `workspace/campaign_plan.md` 获取视觉指导。
- 阅读 `artifacts/copy/product_page.md` 获取上下文。

**指令:**
1.  分析计划和文案。
2.  生成 1 张 "Hero Shot" (主图，影棚光效，纯色背景)。
    -  使用 `generate_image(prompt)`。
    -  保存至 `artifacts/images/hero.png`。
3.  生成 2 张 "Lifestyle Shots" (生活照，产品使用场景)。
    -  保存至 `artifacts/images/lifestyle_01.png` 等。
4.  完成后向 PM 汇报。
```

### 5.4 视频制作人 Agent (Video Producer)
**System Prompt:**
```markdown
你是一名视频制作人。
你的目标是从现有素材中组装出一个短视频广告。

**你的上下文:**
- 阅读 `artifacts/copy/video_script.md`。
- 使用 `artifacts/images/` 中的图片。

**指令:**
1.  读取脚本并检查可用图片。
2.  使用 `generate_video(prompt, image_path)` 根据脚本场景让静态图片动起来。
3.  将它们组合成 `artifacts/videos/ad.mp4`。
4.  完成后向 PM 汇报。
```

## 6. 验证计划 (Verification Plan)

### 自动化测试
1.  **单元测试**: 测试单个工具 (`read_file`, `write_file`) 和 Agent 决策逻辑 (Mock LLM)。
2.  **集成测试**: 运行完整的 "PM -> Copywriter" 循环，验证是否生成了 `campaign_plan.md` 和 `product_page.md`。

### 手动验证
1.  启动后端。
2.  上传一张鞋子的图片和文本 "Comfortable running shoes"。
3.  **验证**:
    *   检查 `projects/{id}/workspace/campaign_plan.md` 是否存在且内容合理。
    *   检查 `projects/{id}/artifacts/copy/` 是否有文本。
    *   检查 `projects/{id}/artifacts/images/` 是否有图片。
    *   检查前端是否显示引用这些文件的 "Thinking" 过程。

## 7. API 与集成设计 (API & Integration Design)

### 7.1 后端 API 端点 (`main.py`)

*   `POST /api/projects`
    *   **输入**: `name`, `description`。
    *   **动作**: 创建项目目录，初始化 context.md。
    *   **输出**: `{ project_id: "uuid" }`。

*   `POST /api/projects/{id}/upload`
    *   **输入**: `file` (multipart)。
    *   **动作**: 保存至 `input/`。

*   `POST /api/projects/{id}/start`
    *   **输入**: 无。
    *   **动作**: 通过 LangGraph 异步触发 `ProductManagerAgent` (PM)。
    *   **输出**: `{ status: "started", run_id: "..." }`。

*   `GET /api/projects/{id}/status`
    *   **输出**: `workspace/status.json` 的内容或衍生的活跃 Agent 状态。

### 7.2 WebSocket 事件 (`webSocket.ts`)

后端将在 Agent 工作时发出实时更新。

*   `agent_start`:
    ```json
    { "type": "agent_start", "agent": "ProductManager", "task": "Creating campaign plan" }
    ```

*   `file_written`:
    ```json
    { "type": "file_written", "path": "workspace/campaign_plan.md", "preview": "## Plan..." }
    ```
    *   **前端动作**: `ThinkingLog` 组件应显示 " Writing workspace/campaign_plan.md..." 并提供点击查看文件内容的链接。

*   `agent_thinking`:
    ```json
    { "type": "agent_thinking", "agent": "Copywriter", "thought": "Analyzing target audience..." }
    ```

*   `project_complete`:
    ```json
    { "type": "project_complete", "artifacts": ["copy/product_page.md", "images/hero.png"] }
    ```
