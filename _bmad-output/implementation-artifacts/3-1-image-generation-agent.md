3-1# Story 3.1: Image Generation Agent

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a 用户,
I want 通过文字描述生成产品图像,
so that 我可以可视化我的产品概念.

## Acceptance Criteria

1. **给定** 产品的文字描述
2. **当** `ImageAgent` 被调用时
3. **则** 系统使用 DeepSeek 优化提示词
4. **并且** 通过 MCP 调用 `ImageGenerator`
5. **并且** 返回生成图像的 URL
6. **并且** 图像元数据持久化到 `video_assets` 表

## Tasks / Subtasks

- [x] Task 1: 实现 ImageAgent 工作流 (AC: 1, 2, 3)
  - [x] Subtask 1.1: 创建 `app/application/agents/image_agent.py` 定义 LangGraph 工作流
  - [x] Subtask 1.2: 实现提示词优化节点（调用 DeepSeek）
  - [x] Subtask 1.3: 实现图像生成节点（调用 MCP ImageGenerator）
  - [x] Subtask 1.4: 添加状态定义和转换逻辑
- [x] Task 2: 定义 Domain 层接口和实体 (AC: 4, 6)
  - [x] Subtask 2.1: 在 `app/domain/interfaces/` 定义 `IImageGenerator` 接口
  - [x] Subtask 2.2: 在 `app/domain/entities/` 创建 `ImageArtifact` 实体
  - [x] Subtask 2.3: 在 `app/domain/entities/` 创建 `ImageGenerationRequest` 实体
- [x] Task 3: 实现 MCP 集成（临时 Mock，等待 Story 3.2） (AC: 4)
  - [x] Subtask 3.1: 创建 `app/infrastructure/mcp/image_client.py` Mock 实现
  - [x] Subtask 3.2: 实现基本的请求/响应解析
- [x] Task 4: 数据持久化 (AC: 6)
  - [x] Subtask 4.1: 创建 SQLAlchemy `VideoAsset` 模型及数据库迁移脚本（需新建表）
  - [x] Subtask 4.2: 实现 Repository 层方法用于保存图像记录
- [x] Task 5: API 端点 (AC: 1, 5)
  - [x] Subtask 5.1: 创建 `POST /api/v1/images/generate` 端点
  - [x] Subtask 5.2: 实现 Socket.io 事件流（agent:thought, agent:tool_call, agent:result）
- [x] Task 6: 测试 (AC: 全部)
  - [x] Subtask 6.1: 编写 Agent 工作流的单元测试
  - [x] Subtask 6.2: 编写 API 端点的集成测试
  - [x] Subtask 6.3: Mock MCP 响应的测试用例

## Dev Notes

### 架构模式与约束

**Pragmatic Clean Architecture 合规性：**
- `Domain` 层定义 `IImageGenerator` 接口和 `ImageArtifact` 实体
- `Application/Agents` 层实现 LangGraph 工作流，依赖 Domain 接口
- `Infrastructure/MCP` 层实现具体的 MCP 客户端
- `Interface/API` 层提供 REST 端点和 Socket.io 事件处理

**依赖注入模式：**
- Agent 通过构造函数/配置接收 `IImageGenerator` 实例
- 使用 ProviderFactory（已在 Epic 1 中实现）创建生成器实例

**LangGraph 状态管理：**
```python
from typing import TypedDict

class ImageAgentState(TypedDict):
    prompt: str              # 用户原始提示词
    optimized_prompt: str    # DeepSeek 优化后的提示词
    image_url: str           # 生成的图像 URL
    asset_id: int            # 持久化的资产 ID
    error: str | None        # 错误信息
```

### 源码组件与文件位置

**新增文件：**
```
backend/
├── app/
│   ├── application/
│   │   └── agents/
│   │       └── image_agent.py           # NEW: ImageAgent LangGraph 工作流
│   ├── domain/
│   │   ├── interfaces/
│   │   │   └── image_generator.py       # NEW: IImageGenerator 接口
│   │   └── entities/
│   │       ├── image_artifact.py        # NEW: ImageArtifact 实体
│   │       └── image_request.py         # NEW: ImageGenerationRequest 实体
│   ├── infrastructure/
│   │   └── mcp/
│   │       └── image_client.py          # NEW: MCP Image 客户端（Mock）
│   └── interface/
│       └── routes/
│           └── images.py                # NEW: 图像生成 API 端点 (Socket.io 事件在 socket_manager.py 中处理)
```

**需要修改的现有文件：**
```
backend/
├── app/
│   ├── infrastructure/
│   │   └── database/
│   │       └── models.py            # UPDATE: 添加 VideoAsset 模型
│   └── core/
│       └── config.py                    # UPDATE: 添加图像生成配置
```

### 测试标准

**测试框架：** pytest + pytest-asyncio

**覆盖率要求：**
- 单元测试覆盖率 >= 80%
- 关键路径（Agent 工作流）100% 覆盖

**测试模式参考 Epic 2：**
- 使用 `tests/fixtures/deepseek_mock.py` 模式创建 MCP Mock
- 测试文件结构：`tests/application/agents/test_image_agent.py`
- 集成测试使用 `tests.conftest.py` 中的数据库 fixtures

**关键测试场景：**
1. 提示词优化成功
2. 图像生成成功（Mock）
3. 持久化成功
4. Socket.io 事件正确发送
5. 错误处理（MCP 失败、DeepSeek 失败）

### Project Structure Notes

**对齐统一项目结构：**

1. **路径规范：**
   - Python 内部使用 `snake_case`（如 `image_agent.py`, `get_image_artifact`）
   - API JSON 响应使用 `camelCase`（如 `imageUrl`, `assetId`）

2. **Pydantic 模型配置：**
   ```python
   from pydantic import ConfigDict

   class ImageGenerationResponse(BaseModel):
       image_url: str
       asset_id: int

       model_config = ConfigDict(
           alias_generator=to_camel,
           populate_by_name=True
       )
   ```

3. **检测到的冲突/差异：**
   - 无冲突。Epic 3 是 Epic 2 的自然扩展，架构模式一致。

### 依赖关系

**前置依赖：**
- ✅ Epic 1: Backend 基础设施完成（Socket.io、数据库、配置）
- ✅ Epic 2: DeepSeek 客户端和 Agent 模式已建立

**并行动作：**
- Story 3.2 (MCP Client) 可以并行开发

**后续依赖：**
- Story 4.1 (Async Video Task Queue) 将复用本 Story 的持久化模式

### Socket.io 事件规范

**遵循架构文档的事件命名：**
```python
# 事件类型
"agent:thought"    # 提示词优化过程中的思考
"agent:tool_call"  # 调用图像生成工具
"agent:result"     # 最终图像结果
"agent:error"      # 错误信息

# Payload 结构
{
    "type": "thought",
    "workflowId": "uuid",
    "data": {"content": "正在优化提示词..."},
    "timestamp": "ISO8601"
}
```

### 临时 Mock 实现

**由于 Story 3.2 才实现真实 MCP 客户端，本 Story 使用 Mock：**

```python
# backend/app/infrastructure/mcp/image_client.py
class MockMCPImageGenerator:
    async def generate(self, prompt: str) -> ImageArtifact:
        # 返回测试图像 URL
        return ImageArtifact(
            url="https://via.placeholder.com/512",
            prompt=prompt,
            provider="mock"
        )
```

**Story 3.2 完成后，将替换为真实 MCP 实现。**

### References

- [Source: _bmad-output/planning-artifacts/epics.md#Epic-3](../planning-artifacts/epics.md)
- [Source: _bmad-output/planning-artifacts/architecture.md#Architecture-Decisions](../planning-artifacts/architecture.md)
- [Source: _bmad-output/implementation-artifacts/2-2-copywriting-agent-workflow.md](./2-2-copywriting-agent-workflow.md) - Agent 模式参考

## Dev Agent Record

### Agent Model Used

Claude Opus 4.5 (claude-opus-4-5-20251101)

### Debug Log References

无 - 故事创建阶段无调试日志。

### Completion Notes List

1. ✅ 从 epics.md 提取了 Epic 3 和 Story 3.1 的完整需求
2. ✅ 分析了 architecture.md 中的 Clean Architecture 约束
3. ✅ 参考 Epic 2 的 Agent 模式（CopywritingAgent）
4. ✅ 定义了与现有架构对齐的文件结构
5. ✅ 规划了临时 Mock 实现为 Story 3.2 做准备

### File List

**已创建：**
- `backend/app/application/agents/image_agent.py` ✅
- `backend/app/application/agents/prompts/image_prompts.py` ✅
- `backend/app/application/dtos/images.py` ✅
- `backend/app/domain/interfaces/image_generator.py` ✅
- `backend/app/domain/entities/image_artifact.py` ✅
- `backend/app/domain/entities/image_request.py` ✅
- `backend/app/infrastructure/mcp/image_client.py` ✅
- `backend/app/infrastructure/repositories/video_asset_repository.py` ✅
- `backend/app/interface/routes/images.py` ✅
- `backend/app/alembic/versions/002_create_video_assets_table.py` ✅
- `backend/tests/application/agents/test_image_agent.py` ✅
- `backend/tests/interface/test_images_api.py` ✅

**已修改：**
- `backend/app/infrastructure/database/models.py` ✅
