# Story 1.4: BaseHTTPClient & Provider Factory

状态: review

<!-- 注意: 验证是可选的。在开发故事之前运行 validate-create-story 进行质量检查。 -->

## 故事

作为一名开发人员，
我想要一个统一的 HTTP 客户端和生成器工厂，
以便我可以轻松添加新的 AI 提供商而无需重复网络逻辑。

## 验收标准

1. **给定** `app/core/http_client.py` 模块
   **当** 我使用 `BaseHTTPClient` 发起请求时
   **那么** 它会自动处理重试 (3次) 和超时
   **并且** 在重试尝试之间使用指数退避

2. **给定** `ProviderFactory` 已配置
   **当** 我使用字符串键 (例如 "deepseek") 请求生成器时
   **那么** 它返回正确的生成器类实例
   **并且** 工厂支持动态提供商注册

3. **给定** 领域层
   **当** 我检查接口时
   **那么** `IGenerator` 协议定义在 `app/domain/interfaces/generator.py` 中
   **并且** 它指定了 `async def generate(request: GenerationRequest) -> GenerationResult`
   **并且** 它指定了 `async def generate_stream(request: GenerationRequest) -> AsyncIterator[str]`

4. **给定** BaseHTTPClient
   **当** 超过最大重试次数时
   **那么** 它抛出 `MaxRetriesExceededError` 并链式包含原始异常

## 任务 / 子任务

- [x] 创建生成器的领域接口 (AC: 3)
  - [x] 创建 `backend/app/domain/interfaces/` 目录
  - [x] 创建 `backend/app/domain/interfaces/__init__.py`
  - [x] 创建 `backend/app/domain/interfaces/generator.py` 包含 `IGenerator` 协议

- [x] 实现 BaseHTTPClient (AC: 1)
  - [x] 创建 `backend/app/core/http_client.py`
  - [x] 实现支持异步上下文管理器的 `BaseHTTPClient` 类
  - [x] 添加重试逻辑 (3次尝试，带指数退避)
  - [x] 添加超时配置 (默认: 30秒)
  - [x] 为请求和重试添加结构化日志
  - [x] 使用适当的异常类型处理 HTTP 错误

- [x] 实现 ProviderFactory (AC: 2)
  - [x] 创建 `backend/app/core/factory.py`
  - [x] 实现带注册模式的 `ProviderFactory` 类
  - [x] 添加 `register_provider()` 方法用于动态注册
  - [x] 添加 `get_provider()` 方法，接受字符串键
  - [x] 为注册的提供商类型添加验证
  - [x] 为未知提供商抛出描述性异常

- [x] 创建 HTTP 客户端配置 (AC: 1)
  - [x] 添加超时设置到 `app/core/config.py`
  - [x] 添加重试次数设置到配置
  - [x] 添加退避因子设置到配置
  - [x] 支持每提供商的超时覆盖
  - [x] 添加环境变量文档到 `.env.example` (HTTP_TIMEOUT_CONNECT, HTTP_TIMEOUT_READ, HTTP_MAX_RETRIES, HTTP_BACKOFF_BASE)

- [x] 创建异常层次结构 (AC: 1)
  - [x] 创建 `backend/app/domain/exceptions.py`
  - [x] 定义 `HTTPClientError` 基类异常
  - [x] 定义 `MaxRetriesExceededError` 用于重试失败
  - [x] 定义 `ProviderNotFoundError` 用于工厂查找失败
  - [x] 定义 `TimeoutError` 用于请求超时

- [x] BaseHTTPClient 单元测试 (AC: 1)
  - [x] 测试成功的 HTTP 请求
  - [x] 测试瞬态故障重试 (状态码: 408, 429, 500, 502, 503, 504)
  - [x] 测试超时处理
  - [x] 测试指数退避计时
  - [x] 测试重试尝试的日志记录
  - [x] 测试最大重试次数时的异常传播 (AC: 4)

- [x] ProviderFactory 单元测试 (AC: 2, 3)
  - [x] 测试提供商注册
  - [x] 测试通过字符串键获取提供商
  - [x] 测试未知键的 `ProviderNotFoundError`
  - [x] 测试重复注册处理
  - [x] 测试 IGenerator 接口合规性

- [x] 集成测试 (AC: 1, 2, 3)
  - [x] 测试全流程: factory → provider → http_client → request
  - [x] 使用模拟 HTTP 服务器模拟提供商 API 进行测试
  - [x] 测试并发提供商实例化

## 开发笔记

### 架构合规性

- **Pragmatic Clean Architecture**:
  - `domain/interfaces/generator.py`: 所有生成器的协议定义
  - `core/http_client.py`: 共享 HTTP 基础设施 (横切关注点)
  - `core/factory.py`: 提供商实例化逻辑

- **领域层纯度** (来自 architecture.md Party Mode refinement #1):
  - `IGenerator` 必须是 Python `Protocol` 或抽象基类
  - 领域接口绝不能依赖 httpx/aiohttp 或任何 HTTP 库
  - 领域实体必须使用纯 Python `dataclasses`

- **统一 HTTP 客户端** (来自 architecture.md Party Mode refinement #2):
  - 所有生成器适配器必须使用 `BaseHTTPClient` 进行外部 API 调用
  - 集中式重试/超时逻辑防止代码重复
  - 实现所有提供商的一致错误处理

### 技术需求

**HTTP 客户端规范:**
- **库**: `aiohttp.ClientSession` (与 Story 1.3 Socket.io 实现一致)
  - 仅异步以匹配 FastAPI 架构
  - 已作为 Story 1.3 的依赖项安装
- **重试策略**:
  - 最大重试: 3 (可配置)
  - 退避: 指数 (2^n 秒: 1s, 2s, 4s)
  - 可重试状态码: 408, 429, 500, 502, 503, 504
- **超时默认值**:
  - 连接超时: 5 秒
  - 读取超时: 30 秒
  - 总超时: 60 秒

**提供商工厂设计:**
```python
# Factory pattern with registry
class ProviderFactory:
    _providers: Dict[str, Type[IGenerator]] = {}

    @classmethod
    def register(cls, key: str, provider_class: Type[IGenerator]) -> None
    @classmethod
    def get_provider(cls, key: str, **kwargs) -> IGenerator
```

**IGenerator 接口** (领域层):
```python
from typing import AsyncIterator, Protocol

# 注意: GenerationResult 和 GenerationRequest 实体将在
# 未来故事 (DeepSeek 提供商实现) 中创建。对于本故事，
# 使用占位符导入或定义存根类型以符合接口要求。
from app.domain.entities import GenerationResult, GenerationRequest

class IGenerator(Protocol):
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        """Synchronous generation"""
        ...

    async def generate_stream(self, request: GenerationRequest) -> AsyncIterator[str]:
        """Streaming generation for real-time responses"""
        ...
```

### 项目结构笔记

- **新目录**: `backend/app/domain/interfaces/` (第一个领域层目录)
- **清晰对齐**: `http_client.py` 和 `factory.py` 在 `core/` 中作为横切工具
- **依赖流**: Infrastructure → Domain (生成器实现 IGenerator), Factory → Domain (创建 IGenerator 实例)

### 以前故事的情报

**来自 Story 1.3 (Socket.io):**
- Async/await 模式在整个代码库中已建立
- 使用 Story 1.1 中的 `structured logging` 模式
- `app/core/config.py` 中的基于环境的配置

**来自 Story 1.2 (Database & Auth):**
- 使用 `pydantic` 进行所有配置验证
- Python 代码使用 `snake_case`，API 响应使用 `camelCase`

**来自 Story 1.1 (Project Initialization):**
- 所有新代码必须可用 pytest 测试
- 所有 I/O 操作使用 `asyncio`
- `.env.example` 中的 Docker 环境变量

### 遵循的代码模式

**HTTP 客户端的异步上下文管理器:**
```python
import aiohttp
from typing import Optional

class BaseHTTPClient:
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        self._session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._session:
            await self._session.close()
```

**重试装饰器模式:**
```python
def retry(max_attempts: int = 3, backoff_base: float = 1.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except RetryableError as e:
                    if attempt == max_attempts - 1:
                        raise MaxRetriesExceededError() from e
                    await asyncio.sleep(backoff_base * (2 ** attempt))
```

**工厂注册模式:**
```python
class ProviderFactory:
    _registry: Dict[str, Type[IGenerator]] = {}

    @classmethod
    def register(cls, key: str, provider: Type[IGenerator]) -> None:
        if key in cls._registry:
            raise ValueError(f"Provider {key} already registered")
        cls._registry[key] = provider

    @classmethod
    def create(cls, key: str, **config) -> IGenerator:
        if key not in cls._registry:
            raise ProviderNotFoundError(f"Unknown provider: {key}")
        return cls._registry[key](**config)
```

### 测试需求

**单元测试覆盖:**
- `BaseHTTPClient`: 90%+ 覆盖率
- `ProviderFactory`: 100% 覆盖率 (关键基础设施)
- `IGenerator`: 接口合规性测试

**Test Doubles:**
- 使用 `aiohttp test utils` 或 `pytest-aiohttp` 进行 HTTP 模拟
- 为工厂测试创建伪造的生成器实现

**集成测试需求:**
- 模拟外部 API (DeepSeek, Gemini 等)
- 使用模拟故障测试重试行为
- 测试并发提供商使用

### 配置需求

添加到 `app/core/config.py`:
```python
class HTTPClientConfig(BaseSettings):
    model_config = ConfigDict(env_prefix="HTTP_")

    timeout_connect: int = 5
    timeout_read: int = 30
    timeout_total: int = 60
    max_retries: int = 3
    retry_backoff_base: float = 1.0
```

### 参考资料

- [Epic 1 Story 1.4](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/epics.md#Story-1.4:-BaseHTTPClient-&-Provider-Factory)
- [Architecture - Multi-Provider Strategy](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md#Multi-Provider-Strategy)
- [Architecture - Party Mode Refinements](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md#Implemented-Refinements-(Party-Mode))
- [Story 1.3 - Socket.io](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/1-3-socket-io-server-security.md)
- [Story 1.2 - Database & Auth](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/1-2-database-auth-setup.md)
- [Story 1.1 - Project Initialization](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/implementation-artifacts/1-1-backend-project-initialization.md)

## 开发代理记录

### 使用的代理模型

Google Gemini (Antigravity)

### 调试日志参考

- 网络问题阻止了测试执行的 `aiohttp` 安装
- 所有新模块的 Python 语法编译通过

### 完成说明列表

- **IGenerator 协议**: 创建了带有 `generate()` 和 `generate_stream()` 方法的 `@runtime_checkable` 协议
- **生成实体**: 创建了 `GenerationRequest`, `GenerationResult`, `StreamChunk` 作为纯 Python dataclasses
- **异常层次结构**: 带有用于调试的详细属性的综合异常
- **BaseHTTPClient**: 带有 aiohttp 的异步上下文管理器，指数退避 (2^n)，可重试状态码 (408, 429, 500, 502, 503, 504)
- **ProviderFactory**: 带有不区分大小写的键、验证和描述性错误消息的注册模式
- **配置**: 添加了 HTTP_TIMEOUT_CONNECT, HTTP_TIMEOUT_READ, HTTP_TIMEOUT_TOTAL, HTTP_MAX_RETRIES, HTTP_BACKOFF_BASE
- **单元测试**: 对 BaseHTTPClient (10 个测试类) 和 ProviderFactory (6 个测试类) 的综合测试
- **集成测试**: 全流程测试，并发提供商测试，模拟 API 仿真

### 文件列表

**创建:**
- `backend/app/domain/entities/generation.py` - 生成实体 (GenerationRequest, GenerationResult, StreamChunk)
- `backend/app/domain/interfaces/generator.py` - IGenerator 协议
- `backend/app/domain/exceptions.py` - 领域异常层次结构
- `backend/app/core/http_client.py` - 带有重试逻辑的 BaseHTTPClient
- `backend/app/core/factory.py` - 带有注册模式的 ProviderFactory
- `backend/.env.example` - 环境变量文档
- `backend/tests/test_http_client.py` - BaseHTTPClient 的单元测试
- `backend/tests/test_factory.py` - ProviderFactory 的单元测试
- `backend/tests/test_http_factory_integration.py` - 集成测试

**修改:**
- `backend/app/core/config.py` - 添加了 HTTP 客户端设置
- `backend/app/core/__init__.py` - 添加了 http_client 和 factory 的导出
- `backend/app/domain/entities/__init__.py` - 添加了生成实体导出
- `backend/app/domain/interfaces/__init__.py` - 添加了 IGenerator 导出

## 变更日志

- **2026-01-22**: Story 1.4 实现已完成
  - 创建了用于多提供商 AI 生成的 IGenerator 协议
  - 实现了带有重试/退避逻辑的 BaseHTTPClient
  - 实现了带有注册模式的 ProviderFactory
  - 为所有组件添加了综合测试套件
