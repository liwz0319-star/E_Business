# Epic 2 手动测试指南：AI 提供商集成与文案代理

**Epic 状态**: 进行中 / 验证中
**相关 Stories**:
- Story 2-1: DeepSeek 客户端实现
- Story 2-2: 文案代理工作流
- Story 2-3: 思考流集成

本文档提供了验证 Epic 2 核心功能（DeepSeek 集成、文案生成工作流、实时思考流）的详细手动测试步骤。

---

## 🛠️ 前置条件

1.  **后端服务**: 确保后端 API 服务正在运行。
    ```bash
    # 在 backend 目录下
    poetry run uvicorn app.main:app --reload
    ```
2.  **环境变量**: 确认 `.env` 文件已配置 DeepSeek 凭证。
    *   `DEEPSEEK_API_KEY=your_key_here`
    *   `DEEPSEEK_MODEL=deepseek-chat` (或 deepseek-reasoner)
3.  **工具准备**: 建议安装 Postman 或使用 curl，以及 Python 环境用于运行测试脚本。

---

## Part 1: DeepSeek 客户端连接 (Story 2-1)

**目标**: 验证系统底层能否成功连接 DeepSeek API 并进行基础对话。

### 测试用例 1.1: 基础连通性测试

我们将使用一个简单的 Python 脚本来直接调用 `ProviderFactory`，绕过上层业务逻辑，直接测试 DeepSeek 集成。

1.  **创建测试脚本** `test_deepseek_manual.py`:

    ```python
    import asyncio
    import os
    from app.core.factory import ProviderFactory
    from app.domain.entities.generation import GenerationRequest
    
    # 确保在运行前设置了环境变量，或者依靠 .env 文件
    # os.environ["DEEPSEEK_API_KEY"] = "sk-..." 
    
    async def main():
        print("Testing DeepSeek connection...")
        try:
            async with ProviderFactory.get_provider("deepseek") as generator:
                request = GenerationRequest(
                    prompt="Say 'Hello, DeepSeek!'",
                    model="deepseek-chat"
                )
                result = await generator.generate(request)
                print(f"✅ Success! Response: {result.content}")
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    if __name__ == "__main__":
        asyncio.run(main())
    ```

2.  **运行脚本**:
    ```bash
    poetry run python test_deepseek_manual.py
    ```

3.  **预期结果**: 控制台输出 "✅ Success! Response: Hello, DeepSeek!" 或类似内容。

---

## Part 2: 文案代理工作流 API (Story 2-2)

**目标**: 验证 REST API 端点能够接受请求并启动后台工作流。

### 测试用例 2.1: 启动生成任务

1.  **请求**: 发送 POST 请求到生成端点。

    *   **URL**: `http://localhost:8000/api/v1/copywriting/generate`
    *   **Method**: `POST`
    *   **Headers**: `Content-Type: application/json`
    *   **Body**:
        ```json
        {
          "productName": "AI 智能咖啡机",
          "features": [
            "语音控制",
            "3秒速热",
            "自定义浓度"
          ],
          "brandGuidelines": "科技感，现代简约"
        }
        ```

    **Curl 命令**:
    ```bash
    curl -X POST "http://localhost:8000/api/v1/copywriting/generate" \
         -H "Content-Type: application/json" \
         -d "{\"productName\": \"AI 智能咖啡机\", \"features\": [\"语音控制\", \"3秒速热\", \"自定义浓度\"]}"
    ```

2.  **预期结果**:
    *   Status Code: `200 OK`
    *   Response Body:
        ```json
        {
          "workflowId": "UUID-STRING-HERE",
          "status": "started",
          "message": "Copywriting workflow initiated. Listen for agent:thought events."
        }
        ```
    *   **注意**: 记下返回的 `workflowId`，后续测试可能需要。

---

## Part 3: 思考流与实时反馈 (Story 2-3)

**目标**: 验证 Socket.IO 能够实时推送 AI 的思考过程（包括 DeepSeek 的 reasoning_content）和最终结果。

### 测试用例 3.1: 完整工作流与实时流监听

为了直观地验证 Socket.IO 事件，我们将使用一个 Python 客户端脚本来模拟前端行为。

1.  **创建监听脚本** `test_socket_workflow.py`:

    ```python
    import socketio
    import requests
    import json
    import time
    
    # 配置
    API_URL = "http://localhost:8000/api/v1/copywriting/generate"
    WS_URL = "http://localhost:8000"
    
    sio = socketio.Client()
    
    @sio.on('connect')
    def on_connect():
        print("✅ Connected to WebSocket")
    
    @sio.on('agent:thought')
    def on_thought(data):
        # 验证 Story 2-3 的关键点：node_name 和 content
        node = data.get('data', {}).get('node_name', 'UNKNOWN')
        content = data.get('data', {}).get('content', '')
        print(f"🤔 [{node}] {content[:50]}..." if len(content) > 50 else f"🤔 [{node}] {content}")
    
    @sio.on('agent:result')
    def on_result(data):
        print(f"\n🎉 Workflow Completed!")
        print(f"Final Copy Preview: {data.get('finalCopy')[:100]}...")
        sio.disconnect()
    
    @sio.on('agent:error')
    def on_error(data):
        print(f"❌ Error: {data}")
        sio.disconnect()
    
    def main():
        # 1. 连接 WebSocket
        try:
            sio.connect(WS_URL)
        except Exception as e:
            print(f"Failed to connect to WS: {e}")
            return
    
        # 2. 触发 API
        print("🚀 Triggering Workflow via API...")
        payload = {
            "productName": "未来派悬浮滑板",
            "features": ["磁悬浮技术", "时速 80km/h", "无线充电"]
        }
        try:
            resp = requests.post(API_URL, json=payload)
            print(f"API Response: {resp.status_code} - {resp.json()}")
        except Exception as e:
            print(f"Failed to call API: {e}")
            return
    
        # 3. 等待事件
        print("👂 Listening for events (Press Ctrl+C to stop)...")
        sio.wait()
    
    if __name__ == "__main__":
        main()
    ```

2.  **准备依赖**:
    ```bash
    pip install "python-socketio[client]" requests
    ```

3.  **运行测试**:
    ```bash
    python test_socket_workflow.py
    ```

4.  **观察重点**:
    *   **连接成功**: 看到 `✅ Connected to WebSocket`.
    *   **阶段流转**: 看到 `[plan]`, `[draft]`, `[critique]`, `[finalize]` 不同 `node_name` 的输出。
    *   **DeepSeek 思考**: 在每个阶段，应该能看到密集的输出更新，这代表 DeepSeek 的 `reasoning_content`正在被流式传输。
    *   **最终结果**: 最后看到 `🎉 Workflow Completed!` 和文案预览。

### 测试用例 3.2: 错误处理

**目标**: 验证当 LLM 调用失败时，系统能优雅报错。

1.  **操作**: 临时修改 `.env` 中的 `DEEPSEEK_API_KEY` 为无效值。
2.  **操作**: 重新运行 `test_socket_workflow.py`。
3.  **预期结果**:
    *   API 调用仍然返回 200 (因为是异步启动)。
    *   WebSocket 客户端收到 `agent:error` 事件。
    *   控制台输出 `❌ Error: ... Invalid API key ...`。
4.  **恢复**: 还原正确的 API Key。

---

## 常见问题排查

*   **WebSocket 连接失败**:
    *   检查后端是否允许了跨域 (CORS)。
    *   确保客户端库版本与服务器兼容 (`python-socketio` v5+)。
*   **收不到 `node_name`**:
    *   确认 Story 2-3 的代码已部署，检查 `socket_manager.py` 是否包含 update 后的 `emit_thought` 方法签名。
*   **没有流式输出**:
    *   检查 `.env` 中的模型配置，部分模型可能不支持 reasoner 流式输出，确认使用的是 `deepseek-chat` 或支持 streaming 的模型。
