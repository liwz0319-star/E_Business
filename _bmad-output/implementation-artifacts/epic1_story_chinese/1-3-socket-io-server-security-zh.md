# Story 1.3: Socket.io 服务器与安全

状态: done

<!-- 注意: 验证是可选的。在开发故事之前运行 validate-create-story 进行质量检查。 -->

## 故事

作为一名开发人员，
我想要建立一个安全的 Socket.io 连接，
以便我可以将实时事件流式传输到前端。

## 验收标准

1. **给定** 一个运行中的 API 服务器
   **当** 客户端使用握手认证中的有效 JWT 连接到 `/ws` 时
   **那么** 连接被接受并且 Socket ID 被记录

2. **给定** 一个运行中的 API 服务器
   **当** 客户端在没有令牌的情况下连接到 `/ws` 时
   **那么** 连接被拒绝 (401)

3. **并且** 服务器支持前端域名的 CORS

## 任务 / 子任务

- [x] 创建 Socket.io 目录结构 (AC: 1, 2, 3)
  - [x] 创建 `backend/app/interface/ws/` 目录
  - [x] 创建 `backend/app/interface/ws/__init__.py`
  - [x] 创建 `backend/app/interface/ws/socket_manager.py` 用于 Socket.io 管理器

- [x] 安装 Socket.io 依赖 (AC: 1, 2, 3)
  - [x] 添加 `python-socketio[asyncio]` 到 `backend/pyproject.toml`
  - [x] 添加 `aiohttp` 到 `backend/pyproject.toml` (异步客户端/服务器稳定性所需)
  - [x] 运行 `poetry lock` 和 `poetry install` (或重新构建 Docker)

- [x] 创建 Socket.io 管理器 (AC: 1)
  - [x] 在 `socket_manager.py` 中创建 `SocketManager` 类
  - [x] 初始化带 `/ws` 路径的异步 Socket.io 服务器
  - [x] 使用环境变量配置 CORS
  - [x] 实现事件发送方法 (agent:thought, agent:tool_call, agent:result, agent:error)

- [x] 实现 JWT 认证中间件 (AC: 1, 2)
  - [x] 创建连接处理器，从握手认证中验证 JWT
  - [x] 重用 Story 1-2 中的 `get_current_user` 依赖逻辑
  - [x] 对无效/缺失的令牌返回 401 错误
  - [x] 记录带 Socket ID 和用户 ID 的成功连接

- [x] 定义事件载荷结构 (AC: 1)
  - [x] 在 `app/interface/ws/schemas.py` 中创建事件载荷的 Pydantic 模型
  - [x] 定义 `AgentThoughtEvent`, `AgentToolCallEvent`, `AgentResultEvent`, `AgentErrorEvent`
  - [x] 包含字段: type, workflowId, data, timestamp

- [x] 集成 Socket.io 到 FastAPI (AC: 1, 2, 3)
  - [x] 在 `main.py` 中将 Socket.io 服务器挂载到 FastAPI 应用
  - [x] 确保 Socket.io 使用与 FastAPI 相同的 ASGI 应用
  - [x] 为 Socket.io 配置异步模式

- [x] 实现 CORS 配置 (AC: 3)
  - [x] 从环境变量读取 `CORS_ORIGINS` (默认: http://localhost:3000,http://localhost:8000)
  - [x] 配置 Socket.io CORS 允许的源
  - [x] 启用凭证支持

- [x] 添加日志 (AC: 1)
  - [x] 记录连接事件 (连接/断开)
  - [x] 记录认证失败
  - [x] 记录用于调试的 Socket ID

- [x] 单元测试 (AC: 1, 2, 3)
  - [x] 测试 Socket.io 管理器初始化
  - [x] 测试连接时的 JWT 认证 (Mock)
  - [x] 测试无有效令牌时的连接拒绝 (Mock)
  - [x] 测试事件发送方法

- [x] 集成测试 (AC: 1, 2, 3)
  - [x] 测试带有效 JWT 的端到端 Socket.io 连接
  - [x] 测试带无效/缺失令牌的连接拒绝
  - [x] 测试连接时的 CORS 头

## 开发笔记

- **架构合规性**:
  - 遵循 **Pragmatic Clean Architecture**:
    - `interface/ws/`: Socket.io 事件处理器和管理器
    - 领域层定义事件载荷接口 (实体)
    - 基础设施层提供 Socket.io 实现
  - **Socket.io 协议** (来自 architecture.md):
    - 使用 `python-socketio` (asyncio 模式)
    - **禁止**: 原始 `websockets` 库
    - 连接路径: `/ws`
    - 必须与现有的 FastAPI ASGI 应用集成

- **Socket.io 事件名称** (来自 architecture.md):
  - `agent:thought`: 来自 DeepSeek 的中间推理步骤
  - `agent:tool_call`: 当代理调用工具时 (例如, "Generating Image...")
  - `agent:result`: 最终输出载荷
  - `agent:error`: 错误详情

- **事件载荷结构** (来自 architecture.md):
  ```json
  {
    "type": "thought",
    "workflowId": "uuid",
    "data": { "content": "..." },
    "timestamp": "ISO8601"
  }
  ```

- **JWT 认证集成** (来自 Story 1-2):
  - 重用 `app/core/security.py` 中现有的 `get_current_user` 依赖逻辑
  - 令牌算法: HS256
  - 握手认证必须在 `auth` 参数中包含有效 JWT
  - 认证失败返回 401
  - 使用现有的 `decode_token()` 函数解码令牌

- **CORS 配置** (来自 Story 1-1):
  - 默认源: `http://localhost:3000,http://localhost:8000`
  - 环境变量: `CORS_ORIGINS` (逗号分隔)
  - 允许凭证: true
  - 允许所有方法和头

- **来自以前故事的代码模式**:
  - 文件和函数使用 snake_case (Story 1-1, 1-2)
  - 类名使用 PascalCase (Story 1-1, 1-2)
  - 使用 Pydantic 模型进行数据验证 (Story 1-1, 1-2)
  - 使用结构化日志 (Story 1-1)
  - 所有 I/O 操作使用 Async/await 模式 (Story 1-1, 1-2)

- **依赖项** (来自 Story 1-1):
  - `python-socketio[asyncio]` - 已在 pyproject.toml 中
  - `aiohttp` - 异步 Socket.io 客户端所需
  - `fastapi` - 用于 ASGI 集成
  - `pydantic` - 用于事件载荷验证

- **项目结构**:
  ```
  backend/app/
  ├── interface/
  │   └── ws/
  │       ├── __init__.py
  │       ├── socket_manager.py    # SocketIO 管理器类
  │       └── schemas.py            # 事件载荷 Pydantic 模型
  ├── core/
  │   └── security.py              # JWT 函数 (重用自 Story 1-2)
  └── main.py                      # FastAPI 应用 (在此处挂载 Socket.io)
  ```

- **技术约束**:
  - Python 3.11+
  - FastAPI ASGI 应用
  - SQLAlchemy (async) 用于任何 DB 操作
  - PostgreSQL + pgvector (来自 Story 1-1)

### 项目结构笔记

- **清晰对齐**: `interface/ws/` 目录遵循 Story 1-1 中定义的 Pragmatic Clean Architecture
- **集成点**: Socket.io 必须在 `main.py` 中挂载到与 FastAPI 相同的 ASGI 应用
- **安全层**: JWT 认证逻辑集中在 `app/core/security.py` (来自 Story 1-2)

### 参考资料

- [Epic 1 Story 1.3](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/epics.md#Story-1.3:-Socket.io-Server-&-Security)
- [Architecture - Socket.io Protocol](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md#Communication-Patterns)
- [Architecture - Project Structure](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md#Complete-Project-Directory-Structure)
- [Story 1.1 - Backend Initialization](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/1-1-backend-project-initialization.md)
- [Story 1.2 - Database & Auth](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/1-2-database-auth-setup.md)
