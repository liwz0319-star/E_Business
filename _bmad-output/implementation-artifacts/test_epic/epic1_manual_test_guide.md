# Epic 1 手动测试指南

本文档旨在指导您完成 Epic 1 (Stories 1.1 - 1.4) 的核心功能手动验证。

## 前置条件

1. 确保 Docker 和 Docker Compose 已安装。
2. 终端当前目录为项目根目录。
3. 推荐工具：Postman 或 Bruno (用于 API 测试)。

---

## Story 1.1: 后端项目初始化 & 基础设施

### 1. 启动服务
在终端运行：
```bash
docker-compose up -d --build
```
确保所有容器 (db, redis, minio, api) 均处于 `Up` 状态：
```bash
docker-compose ps
```

### 2. 验证健康检查
在浏览器访问：[http://localhost:8000/health](http://localhost:8000/health)
**预期结果**: 返回 `{"status": "ok"}`

### 3. 验证 Swagger 文档
在浏览器访问：[http://localhost:8000/docs](http://localhost:8000/docs)
**预期结果**: 看到 Swagger UI 界面。

---

## Story 1.2: 数据库与身份验证

使用 Swagger UI ([http://localhost:8000/docs](http://localhost:8000/docs)) 或 Postman 进行测试。

### 1. 用户注册
*   **Endpoint**: `POST /api/v1/auth/signup`
*   **Payload**:
    ```json
    {
      "email": "test@example.com",
      "password": "Password123!",
      "full_name": "Test User"
    }
    ```
*   **预期结果**: 状态码 200，返回用户信息。

### 2. 用户登录
*   **Endpoint**: `POST /api/v1/auth/login`
*   **Payload** (Form-Data):
    *   `username`: test@example.com
    *   `password`: Password123!
*   **预期结果**: 状态码 200，返回 `access_token`。

### 3. 验证受保护路由
*   **Endpoint**: `GET /api/v1/auth/me`
*   **Auth**: Bearer Token (使用上一步获取的 token)
*   **预期结果**: 状态码 200，返回当前用户信息。

---

## Story 1.3: Socket.io 服务器 & 安全

由于 Swagger 不支持 Socket.io，我们使用浏览器控制台或简单的测试脚本进行验证。

### 1. 准备测试页面
在项目根目录创建一个临时文件 `test_socket.html`，内容如下：
```html
<!DOCTYPE html>
<html>
<head>
    <title>Socket.IO Test</title>
    <script src="https://cdn.socket.io/4.7.4/socket.io.min.js"></script>
</head>
<body>
    <h2>Socket.IO Connection Test</h2>
    <div>
        <label>Token:</label>
        <input type="text" id="token" placeholder="Paste Access Token Here" style="width: 300px;">
        <button onclick="connect()">Connect</button>
        <button onclick="disconnect()">Disconnect</button>
    </div>
    <div id="status">Status: Disconnected</div>
    <div id="logs"></div>

    <script>
        let socket;

        function log(msg) {
            const div = document.createElement('div');
            div.textContent = `[${new Date().toLocaleTimeString()}] ${msg}`;
            document.getElementById('logs').appendChild(div);
        }

        function connect() {
            const token = document.getElementById('token').value;
            if (!token) {
                alert('Please enter a token');
                return;
            }

            socket = io('http://localhost:8000', {
                path: '/ws',
                auth: { token: token },
                transports: ['websocket']
            });

            socket.on('connect', () => {
                document.getElementById('status').textContent = 'Status: Connected (' + socket.id + ')';
                document.getElementById('status').style.color = 'green';
                log('Connected! ID: ' + socket.id);
            });

            socket.on('connect_error', (err) => {
                document.getElementById('status').textContent = 'Status: Error - ' + err.message;
                document.getElementById('status').style.color = 'red';
                log('Connection Error: ' + err.message);
            });

            socket.on('disconnect', () => {
                document.getElementById('status').textContent = 'Status: Disconnected';
                document.getElementById('status').style.color = 'black';
                log('Disconnected');
            });
            
            socket.on('agent:thought', (data) => log('Thought: ' + JSON.stringify(data)));
        }
        
        function disconnect() {
            if (socket) socket.disconnect();
        }
    </script>
</body>
</html>
```

### 2. 执行测试
1.  打开 `test_socket.html` (直接双击或拖入浏览器)。
2.  从 Story 1.2 的登录步骤获取 `access_token`。
3.  **测试认证失败**: 不填 Token 点击 Connect -> 应显示 "Connection Error: Authentication required" 或类似错误。
4.  **测试认证成功**: 填入有效 Token 点击 Connect -> 应显示 "Status: Connected"。
5.  查看 Docker 日志 (`docker logs -f e_business-api-1`)，应能看到连接成功的日志信息。

---

## Story 1.4: Provider Factory & HTTP Client

此功能为内部基础设施，暂时没有公开 API。我们可以通过在容器内运行 Python 脚本来验证。

### 验证脚本测试

1.  进入后端容器：
    ```bash
    docker exec -it e_business-api-1 bash
    ```

2.  运行验证脚本 (在容器内输入 `python` 进入交互模式，然后粘贴以下代码)：

    ```python
    import asyncio
    from app.core.factory import ProviderFactory
    from app.domain.interfaces.generator import IGenerator
    from app.domain.entities.generation import GenerationRequest, GenerationResult

    # 1. 定义一个 Mock Provider
    class MockProvider:
        async def generate(self, request: GenerationRequest) -> GenerationResult:
            return GenerationResult(content="Mock Verified", raw_response={})
        
        async def generate_stream(self, request):
            yield "Mock"
            yield "Verified"

    # 2. 注册 Provider
    print("Registering provider...")
    ProviderFactory.register("test_provider", MockProvider)

    # 3. 获取并使用 Provider
    async def test():
        try:
            provider = ProviderFactory.get_provider("test_provider")
            print(f"Got provider: {provider}")
            
            req = GenerationRequest(prompt="test", model="gpt-4")
            result = await provider.generate(req)
            print(f"Generation result: {result.content}")
            
            if result.content == "Mock Verified":
                print("✅ Story 1.4 Verification PASSED")
            else:
                print("❌ Verification FAILED: Content mismatch")
                
        except Exception as e:
            print(f"❌ Verification FAILED: {e}")

    # 运行测试
    asyncio.run(test())
    ```

3.  **预期结果**: 终端输出 `✅ Story 1.4 Verification PASSED`。
4.  退出容器 (`exit`)。

---

## 总结

如果在以上所有步骤中都获得了预期结果，则 Epic 1 (Stories 1-4) 的核心功能已通过验证。
