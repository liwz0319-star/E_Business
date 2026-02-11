# Agent-native 架构深度解析

本文档基于 Every.to 的 "Agent-native Architectures" 指南，为您梳理构建以 Agent 为核心的应用的关键架构原则与实践模式。

## 核心理念：不仅是调用，更是原住民
"Agent-native" 是一种全新的软件范式。在这个范式中，**Agent 不再仅仅是现有功能的“路由层”或“外挂”，而是拥有第一公民身份的核心执行者。**

### 五大设计原则 (Key Principles)

1.  **能力对等 (Parity)**
    *   **原则**: UI 能做的任何事，Agent 都必须能做。
    *   **标准**: 挑选任何一个 UI 操作，Agent 是否有对应的工具或工具组合能完成它？如果不能，那就是架构缺失。
    *   **意义**: 这是基石。如果 Agent 能力有缺失，用户体验就会断裂。

2.  **原子化工具 (Granularity)**
    *   **原则**: 工具应该是最基础的原子操作 (Primitive)，而不是像传统代码那样封装好的业务流。
    *   **反例**: `analyze_and_organize_files()` （包含了太多预设逻辑）。
    *   **正例**: `read_files()`, `analyze_content()`, `move_file()`。
    *   **意义**: 让 Agent 通过 Prompt 组合原子工具来应对多变的需求，而不是被死板的代码逻辑束缚。

3.  **可组合性 (Composability)**
    *   **原则**: 新功能 = 新的指令 (Prompt) + 现有的原子工具。
    *   **优势**: 你可以像搭积木一样，通过写 Prompt 来“开发”新功能，而无需修改后端代码或发版。

4.  **涌现能力 (Emergent Capability)**
    *   **原则**: 仅仅提供基础能力，Agent 会组合出开发者未曾设想的用法。
    *   **实践**: 观察用户让 Agent 做了什么你没想到的事 (Latent Demand Discovery)，然后将这些高频模式固化为新的工具或 Prompt。

5.  **持续进化 (Improvement over time)**
    *   **积累**: Agent 通过上下文记忆 (Context) 随着使用时间的推移变得更聪明、更懂用户。
    *   **迭代**: 开发者优化 Prompt，用户也可以自定义 Prompt，系统在不改代码的情况下持续变强。

---

## 架构落地模式 (Implementation Patterns)

### 1. 共享工作区 (Shared Workspace) & 文件作为通用接口
这是该架构中最核心的实现模式。
*   **单一事实来源**: 不要把 Agent 的“记忆”藏在向量数据库的黑盒里。让 Agent 和用户操作同一个文件系统。
*   **实体目录结构**: 为每个业务实体创建目录，例如 `Projects/{projectId}/`。
*   **Context.md 模式**: 在根目录或项目目录维护一个 `context.md`。
    *   记录“我是谁”、“当前状态”、“用户偏好”、“最近发生了什么”。
    *   Agent 每次启动先读此文件，操作完更新此文件。这就构成了**可移植的工作记忆**。

### 2. 执行模式 (Execution Patterns)
*   **明确的完成信号 (Completion Signals)**: Agent 必须显式调用 `complete_task()` 工具来宣告任务结束，绝不能靠“不再调用工具”来隐式推断。
*   **动态能力发现 (Dynamic Capability Discovery)**:
    *   面对复杂的外部 API（如 HealthKit），不要硬编码 50 个工具。
    *   提供 `list_capabilities()` 让 Agent 自己去发现能干什么，再按需调用。

### 3. 数据与状态
*   **Markdown/JSON 优先**: 相比数据库，文件更适合 LLM 阅读和人类审查。
*   **CRUD 完整性**: 对每个实体，必须确保 Agent 拥有增删改查的全套能力，缺一不可。

---

## 常见的反模式 (Anti-Patterns) —— 避坑指南

1.  **Agent 作为路由器 (Agent as Router)**: 只用 Agent 分析意图，然后调用写死的代码流程。这是大材小用，失去了灵活性。
2.  **工作流式工具 (Workflow-shaped Tools)**: 工具里包含了业务判断（例如“如果是紧急邮件则通知”）。**判断逻辑应在 Prompt 里，工具只负责执行**。
3.  **快乐路径编程 (Happy Path Coding)**: 传统开发中，代码处理所有边缘情况。Agent-native 架构中，代码只提供基础能力，由 Agent 的智能来处理边缘和意外情况。
4.  **上下文饥饿 (Context Starvation)**: 不告诉 Agent 当前有什么文件、用户是谁，就指望它干活。必须在 System Prompt 中注入充足的上下文。

总结：Agent-native 架构的核心是从**“编写其行为”**转向**“赋予其能力”**。
