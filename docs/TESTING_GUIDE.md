# 🧪 Agent 测试方案指南

## 测试概览

本测试方案涵盖 3 个层级:
- **单元测试**: 测试独立组件
- **集成测试**: 测试 API 和工作流
- **E2E 测试**: 测试完整业务流程

---

## 一、快速开始

### 1.1 运行所有测试

```bash
cd backend

# 运行核心测试套件
python -m pytest tests/test_health.py -v

# 运行工具层测试
python -m pytest tests/application/tools/ -v

# 运行仓储层测试
python -m pytest tests/infrastructure/repositories/ -v

# 运行集成测试
python -m pytest tests/integration/ -v -s
```

### 1.2 手动 Agent 测试

```bash
cd backend

# 运行交互式测试
python scripts/test_agents_manual.py
```

这会测试:
- FileSystemTools
- VisionTools (Mock)
- TextTools (Mock)
- ProductAnalysisAgent
- QAAgent
- VideoTools (Mock)

---

## 二、测试层级详解

### 2.1 单元测试

#### 测试文件系统工具
```bash
python -m pytest tests/application/tools/test_filesystem_tools.py -v
```

**测试内容**:
- 工作区创建
- 文件读写
- JSON 操作
- 路径安全验证
- 目录列表

#### 测试产品包仓储
```bash
python -m pytest tests/infrastructure/repositories/test_product_package_repo_async.py -v
```

**测试内容**:
- 创建产品包
- 通过 workflow_id 查询
- 更新状态
- 添加工件引用
- 审批流程
- QA 报告更新

### 2.2 集成测试

#### 测试完整工作流
```bash
python -m pytest tests/integration/test_product_package_workflow.py -v -s
```

**测试场景**:
1. **完整工作流测试**:
   - 发起生成请求
   - 轮询状态
   - 获取最终结果

2. **审批工作流测试**:
   - 创建需要审批的包
   - 提交审批决策
   - 验证状态变更

3. **重新生成测试**:
   - 部分重新生成 (copywriting/images/video/all)

### 2.3 手动测试脚本

```bash
cd backend
python scripts/test_agents_manual.py
```

**测试模块**:
- ✓ FileSystemTools - 文件系统操作
- ✓ VisionTools - 产品图像分析 (Mock)
- ✓ TextTools - 文本生成 (Mock)
- ✓ ProductAnalysisAgent - 产品分析流程
- ✓ QAAgent - 质量检查流程
- ✓ VideoTools - 视频生成 (Mock + Fallback)

---

## 三、测试 API 端点

### 3.1 使用 curl 测试

#### 1. 注册用户
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

#### 2. 登录获取 Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"
```

保存返回的 `access_token`。

#### 3. 发起产品包生成
```bash
curl -X POST http://localhost:8000/api/v1/product-packages/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/product.jpg",
    "background": "Premium wireless headphones",
    "options": {
      "copy_variants": 2,
      "image_variants: 3,
      "video_duration_sec": 15,
      "require_approval": false,
      "force_fallback_video": true
    }
  }'
```

#### 4. 查询状态
```bash
curl -X GET http://localhost:8000/api/v1/product-packages/status/WORKFLOW_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 5. 获取详情
```bash
curl -X GET http://localhost:8000/api/v1/product-packages/PACKAGE_ID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 6. 审批
```bash
curl -X POST http://localhost:8000/api/v1/product-packages/PACKAGE_ID/approve \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "decision": "approve",
    "comment": "Looks good!"
  }'
```

#### 7. 重新生成
```bash
curl -X POST http://localhost:8000/api/v1/product-packages/PACKAGE_ID/regenerate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "target": "images",
    "reason": "Want different style"
  }'
```

### 3.2 使用 Python 测试

创建 `test_api.py`:

```python
import asyncio
import httpx

async def test_workflow():
    async with httpx.AsyncClient() as client:
        # 1. 登录
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpass123"
            }
        )
        token = response.json()["access_token"]

        headers = {"Authorization": f"Bearer {token}"}

        # 2. 发起生成
        response = await client.post(
            "http://localhost:8000/api/v1/product-packages/generate",
            headers=headers,
            json={
                "image_url": "https://example.com/product.jpg",
                "background": "Test product",
                "options": {"require_approval": False}
            }
        )
        workflow_id = response.json()["workflow_id"]

        # 3. 轮询状态
        while True:
            await asyncio.sleep(2)
            response = await client.get(
                f"http://localhost:8000/api/v1/product-packages/status/{workflow_id}",
                headers=headers
            )
            status = response.json()
            print(f"进度: {status['progress_percentage']}%")

            if status["status"] in ["completed", "failed"]:
                break

        print(f"✅ 工作流完成: {status['status']}")

asyncio.run(test_workflow())
```

运行:
```bash
python test_api.py
```

---

## 四、WebSocket 测试

### 4.1 使用 Python 客户端

创建 `test_ws.py`:

```python
import asyncio
import socketio

async def test_websocket():
    # 创建 Socket.IO 客户端
    sio = socketio.AsyncClient()

    @sio.on('connect')
    async def on_connect():
        print('✅ WebSocket 已连接')
        # 发送认证
        await sio.emit('authenticate', {
            'token': 'YOUR_ACCESS_TOKEN'
        })

    @sio.on('agent:progress')
    async def on_progress(data):
        print(f"📊 进度更新: {data['data']['percentage']}% - {data['data']['current_step']}")

    @sio.on('agent:artifact')
    async def on_artifact(data):
        print(f"🎨 工件生成: {data['data']['artifact_type']}")

    @sio.on('agent:approval_required')
    async def on_approval(data):
        print(f"⚠️  需要审批: QA分数 {data['data']['qa_score']}")

    await sio.connect('http://localhost:8000')
    await sio.wait()

asyncio.run(test_websocket())
```

---

## 五、性能测试

### 5.1 并发测试

```python
import asyncio
import httpx
from uuid import uuid4

async def test_concurrent_workloads(num_concurrent=5):
    """测试并发工作流"""
    async with httpx.AsyncClient() as client:
        # 获取 token
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            data={"username": "test@example.com", "password": "testpass123"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 并发发起多个工作流
        tasks = []
        for i in range(num_concurrent):
            task = client.post(
                "http://localhost:8000/api/v1/product-packages/generate",
                headers=headers,
                json={
                    "image_url": f"https://example.com/product{i}.jpg",
                    "background": f"Test product {i}",
                    "options": {"require_approval": False}
                }
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        success_count = sum(1 for r in results if r.status_code == 202)
        print(f"✅ 成功发起 {success_count}/{num_concurrent} 个工作流")

asyncio.run(test_concurrent_workloads(10))
```

---

## 六、调试技巧

### 6.1 查看日志

```bash
# 启动服务时显示详细日志
cd backend
python -m uvicorn app.main:app --reload --log-level debug
```

### 6.2 使用 pytest 调试

```bash
# 运行单个测试并进入调试
python -m pytest tests/integration/test_product_package_workflow.py::TestProductPackageWorkflow::test_full_workflow_with_mock_data -v -s --pdb
```

### 6.3 检查工作区文件

```bash
# 查看生成的工作区
ls -la backend/projects/

# 查看特定工作流的内容
ls -la backend/projects/WORKFLOW_ID/
```

---

## 七、测试覆盖率

### 7.1 生成覆盖率报告

```bash
# 安装 pytest-cov
pip install pytest-cov

# 运行测试并生成报告
python -m pytest --cov=app --cov-report=html tests/

# 打开报告
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
xdg-open htmlcov/index.html  # Linux
```

---

## 八、常见问题

### Q1: 测试失败 "ModuleNotFoundError"

**解决方案**:
```bash
cd backend
pip install -e .
```

### Q2: 数据库连接错误

**解决方案**:
```bash
# 检查 .env 文件
cat backend/.env

# 确保数据库运行
docker ps | grep postgres

# 或启动本地 PostgreSQL
# 检查连接字符串
```

### Q3: WebSocket 测试超时

**解决方案**:
- 确保服务已启动
- 检查 CORS 配置
- 验证 token 有效性

---

## 九、CI/CD 集成

### 9.1 GitHub Actions 示例

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -e .
          pip install pytest pytest-asyncio pytest-cov

      - name: Run tests
        run: |
          cd backend
          python -m pytest tests/ -v --cov=app

      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## 十、下一步

1. ✅ 运行单元测试验证各个组件
2. ✅ 运行集成测试验证 API
3. ✅ 使用手动测试脚本验证 Agent
4. 🔄 添加真实 providers 并重新测试
5. 🔄 添加性能测试和压力测试
6. 🔄 设置 CI/CD 自动化测试

---

## 总结

本测试方案提供:
- ✓ 3 层测试覆盖(单元/集成/E2E)
- ✓ 多种测试方式(pytest/curl/Python)
- ✓ WebSocket 测试支持
- ✓ 并发性能测试
- ✓ 调试技巧和常见问题

开始测试:
```bash
cd backend
python scripts/test_agents_manual.py
```
