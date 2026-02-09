# Story 3.2: MCP Client for Image Tools

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a 开发者,
I want 通过 MCP 调用图像生成工具,
So that 我可以在不更改 Agent 逻辑的情况下切换提供商.

## Acceptance Criteria

1. **给定** 一个运行中的 MCP Server (或 Mock)
2. **当** `MCPImageGenerator` 通过 `ImageAgent` 被调用时
3. **则** 它根据 MCP `tools/call` 协议格式化请求（包含 prompt, width, height 参数）
4. **并且** 发送给配置的工具服务器，并在 60 秒内获得响应或返回超时错误
5. **并且** 将结果解析回标准的 `ImageArtifact` 领域实体
    - 如果 MCP 返回图片 URL，直接映射
    - 如果 MCP 返回 Base64 数据，自动上传到 MinIO 并转换为 URL
    - 确保 `provider` 字段正确标识为 'mcp'

## Tasks / Subtasks

- [ ] Task 1: 基础设施准备 (AC: 1, 5)
  - [ ] Subtask 1.1: 创建 `app/infrastructure/mcp/base_client.py` 基础客户端（支持 HTTP 和 Stdio 通信）
  - [ ] Subtask 1.2: 创建 `app/infrastructure/storage/minio_client.py`，实现 Base64 图片上传到 MinIO 的功能
  - [ ] Subtask 1.3: 创建 `app/infrastructure/mcp/mcp_image_generator.py`，实现 `IImageGenerator` 接口

- [ ] Task 2: 实现 MCP 协议与配置 (AC: 3, 4)
  - [ ] Subtask 2.1: 实现工具调用格式化 (符合 MCP 规范)
  - [ ] Subtask 2.2: 在 `app/core/config.py` 中添加以下配置项:
    - `mcp_image_server_url`: MCP Server URL
    - `mcp_image_use_stdio`: 是否使用 Stdio 模式
    - `mcp_image_timeout`: 请求超时时间
    - `mcp_image_model`: 默认图像生成模型
    - `image_generator_provider`: 生成器提供商选择（"mock" 或 "mcp"）
  - [ ] Subtask 2.3: 实现错误处理和超时机制（网络错误、超时、协议错误、工具不存在）
  - [ ] Subtask 2.4: 在 `app/core/factory.py` 中注册 `mcp` 类型的 ImageGenerator

- [ ] Task 3: 响应解析与领域映射 (AC: 5)
  - [ ] Subtask 3.1: 解析 MCP 工具响应，识别 URL 或 Base64 数据
  - [ ] Subtask 3.2: 集成 `MinIOClient` 处理 Base64 数据上传
  - [ ] Subtask 3.3: 将最终 URL 映射到 `ImageArtifact` 领域实体

- [ ] Task 4: 集成与测试 (AC: All)
  - [ ] Subtask 4.1: 编写 `MCPImageGenerator` 的单元测试 (Mock MCP Server & MinIO)
  - [ ] Subtask 4.2: 更新 `ImageAgent` 集成 - 使用依赖注入模式:
    - 更新 `ImageAgent.__init__` 接受 `image_generator` 参数
    - 实现 `_get_default_generator` 使用 `ProviderFactory.get_provider()`
    - 移除硬编码的 `MockMCPImageGenerator`
  - [ ] Subtask 4.3: 编写网络异常和协议错误的集成测试
  - [ ] Subtask 4.4: 通过 API 端点完整测试图像生成工作流（端到端测试）

## Dev Notes

### 架构模式与约束

**Pragmatic Clean Architecture 合规性：**
- **Infrastructure**: 实现位于 `app/infrastructure/mcp/` 和 `app/infrastructure/storage/`
- **Interface**: 实现 `app/domain/interfaces/image_generator.py` (IImageGenerator)
- **Factory**: 使用 `app/core/factory.py` (ProviderFactory) 管理生成器实例
- **Config**: 由 `app/core/config.py` 驱动
- **依赖注入**: `ImageAgent` 通过构造函数接收生成器，或使用 Factory 提供的默认实现

### MCP 特定说明

#### Base64 图片处理
MCP 协议可能通过 `content` 字段返回 Base64 编码的图片数据。
由于 `VideoAssetRepository` 和 `ImageArtifact` 均要求 `url` 字段，必须先将 Base64 上传到对象存储（MinIO）。

**处理逻辑：**
1. 检查 `content[0].data` 是否以 `http` 开头
2. 如果是 URL -> 直接使用
3. 如果是 Base64 -> 调用 `MinIOClient.upload_base64_image()` -> 获取 URL -> 使用

#### MCP 协议格式规范

**MCP 请求格式** (tools/call):
```json
{
  "jsonrpc": "2.0",
  "id": "request-uuid",
  "method": "tools/call",
  "params": {
    "name": "generate_image",
    "arguments": {
      "prompt": "优化后的提示词",
      "width": 512,
      "height": 512,
      "model": "stable-diffusion-xl",
      "num_inference_steps": 50,
      "guidance_scale": 7.5
    }
  }
}
```

**MCP 响应格式** (成功):
```json
{
  "jsonrpc": "2.0",
  "id": "request-uuid",
  "result": {
    "content": [
      {
        "type": "image",
        "data": "base64_encoded_image_or_url",
        "mimeType": "image/png"
      }
    ],
    "metadata": {
      "width": 512,
      "height": 512,
      "model": "stable-diffusion-xl",
      "provider": "mcp"
    }
  }
}
```

### 依赖关系
- **前置依赖**: Story 3.1 定义了接口和实体。本 Story 实现具体的 MCP 策略。
- **MinIO**: 需要 MinIO 服务可用（Docker 容器已在 Story 1.1 中配置）。

**环境变量示例:**
```bash
# MCP Image Generation Configuration
MCP_IMAGE_SERVER_URL=http://localhost:3000  # MCP Server HTTP URL
MCP_IMAGE_USE_STDIO=false                   # 使用 Stdio 模式（默认 False）
MCP_IMAGE_TIMEOUT=60                        # 请求超时（秒）
MCP_IMAGE_MODEL=stable-diffusion-xl         # 默认模型
IMAGE_GENERATOR_PROVIDER=mcp                # 生成器提供商（mock/mcp）
```

### Project Structure Notes

**你需要创建/修改的文件：**
```
backend/
├── app/
│   ├── infrastructure/
│   │   ├── mcp/
│   │   │   ├── __init__.py              # UPDATE: 导出 MCPImageGenerator
│   │   │   ├── image_client.py          # EXISTING: MockMCPImageGenerator (保留用于测试/mock模式)
│   │   │   ├── base_client.py           # NEW: MCP 基础客户端
│   │   │   └── mcp_image_generator.py   # NEW: 真实 MCP 图片生成器实现
│   │   └── storage/
│   │       └── minio_client.py          # NEW: MinIO 客户端 (处理 Base64 上传)
│   ├── application/
│   │   └── agents/
│   │       └── image_agent.py           # UPDATE: 使用依赖注入和 ProviderFactory
│   └── core/
│       ├── config.py                    # UPDATE: 添加配置项
│       └── factory.py                   # UPDATE: 注册 mcp 生成器
├── tests/
│   ├── infrastructure/
│   │   └── mcp/
│   │   │   └── test_mcp_image_generator.py  # NEW: MCP 客户端单元测试
│   └── application/
│       └── agents/
│           └── test_image_agent.py      # UPDATE: 添加集成测试
```
