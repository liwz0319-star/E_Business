# Agent 设计文档结构 (建议)

在主页设计像 "Agent" 这样复杂的功能时，制定一个结构化的设计文档至关重要。以下是一个推荐的模板，用于应对当前的“只构思，不修改”阶段。

## 1. 功能概述 (Feature Overview)
- **目标 (Goal)**: 这个 Agent 的主要目的是什么？（例如：导航助手、任务自动化、内容推荐）
- **人设 (Persona)**: Agent 的名称、语气和个性。
- **范围 (Scope)**: 它能做什么？它的 *V1 版本限制*是什么（不能做什么）？

## 2. 用户体验设计 (User Experience Design)
### 2.1 入口 (Entry Point)
- **位置 (Location)**: Agent 在主页的什么位置？（悬浮按钮、侧边栏、集成聊天框？）
- **触发方式 (Trigger)**: 点击、语音、自动弹出？
- **视觉状态 (Visual State)**: 
    - *闲置状态 (Idle)*: 不活动时是什么样子？
    - *活跃状态 (Active)*: 界面如何展开或变化？

### 2.2 交互流程 (Interaction Flow)
- **输入 (Input)**: 文本、语音、预定义快捷操作？
- **反馈 (Feedback)**: 加载状态、正在输入提示。
- **输出 (Output)**: 文本气泡、富媒体卡片、导航跳转、执行动作。

## 3. 技术架构 (Technical Architecture)
### 3.1 前端组件 (Frontend Components)
- `AgentContainer`: 主容器。
- `ChatInterface`: 消息列表和输入区域。
- `AgentAvatar`: 视觉形象（静态/动态）。
- `ActionCards`: Agent 建议的特殊 UI 元素（例如：“分析此数据”、“进入设置”）。

### 3.2 状态管理 (State Management)
- **本地状态 (Local State)**: `isOpen`（开启状态）、`isTyping`（输入中）、`inputText`（输入文本）。
- **会话状态 (Session State)**: 消息历史 (`Array<Message>`)。
- **上下文 (Context)**: Agent 知道什么？（当前页面、用户资料、最近操作）。

## 4. 智能逻辑 (Agent Logic & Intelligence)
### 4.1 集成方式 (Integration)
- **服务 (Service)**: 如何连接 LLM？（例如：扩展 `GeminiService`）。
- **系统提示词 (System Prompt)**: 定义 Agent 行为的关键指令。
- **工具 (Tools)**: 它具备通过哪些能力？（例如：`navigate(route)` 路由跳转、`fetchData()` 获取数据）。

## 5. 视觉草图 (Mockups & Visuals)
- [在此处放置 Mermaid 图表或线框图占位符]

## 6. 实施阶段 (Implementation Phases)
- **第一阶段 (Phase 1)**: 基础 UI 和对话循环。
- **第二阶段 (Phase 2)**: 上下文感知 (Context Awareness)。
- **第三阶段 (Phase 3)**: 动作执行 (Action Execution)。
