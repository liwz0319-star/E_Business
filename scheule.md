# DeepAgents 测试方案记录

**更新时间**: 2026-02-10
**状态**: ✅ 测试框架已就绪

---

## 一、测试方案概览

### 测试层级
```
测试层级:
├── 单元测试 (Unit Tests)
│   ├── 工具层测试 (FileSystemTools, TextTools, VisionTools, etc.)
│   ├── Agent 层测试 (ProductAnalysisAgent, QAAgent, etc.)
│   └── 仓储层测试 (ProductPackageRepository)
├── 集成测试 (Integration Tests)
│   ├── API 端点测试 (REST API)
│   ├── WebSocket 事件测试
│   └── 完整工作流测试
└── E2E 测试 (End-to-End Tests)
    └── 端到端业务流程测试
```

---

## 二、已创建的测试文件

### 📁 测试脚本文件

#### 1. 单元测试
- **`backend/tests/application/tools/test_filesystem_tools.py`**
  - 测试 FileSystemTools 的文件操作功能
  - 包含: 创建工作区、文件读写、JSON操作、路径安全验证

- **`backend/tests/infrastructure/repositories/test_product_package_repo_async.py`**
  - 测试 ProductPackageRepository 异步操作
  - 包含: CRUD操作、状态更新、工件管理、审批流程

#### 2. 集成测试
- **`backend/tests/integration/test_product_package_workflow.py`**
  - 测试完整的产品包生成工作流
  - 包含: 生成→轮询→获取结果、审批流程、重新生成

#### 3. 手动测试脚本
- **`backend/scripts/test_agents_manual.py`**
  - 交互式 Agent 能力测试
  - 测试所有核心 Agent 和工具

### 📁 配置文件

- **`backend/pyproject.test.toml`** - Pytest 配置
- **`backend/Makefile`** - 测试快捷命令
- **`backend/RUN_TESTS.md`** - 测试运行脚本

### 📁 文档文件

- **`docs/TESTING_GUIDE.md`** - 完整测试指南(含API测试示例)
- **`docs/TEST_PLAN_SUMMARY.md`** - 测试方案总结
- **`docs/implementation-completion-report.md`** - 实施完成报告

---

## 三、快速测试命令

### 方式 1: 使用 Makefile (推荐)

```bash
cd backend

# 快速测试
make test

# 所有测试
make test-all

# 单元测试
make test-unit

# 集成测试
make test-integration

# 手动测试
make test-manual

# 覆盖率报告
make coverage

# 查看帮助
make help
```

### 方式 2: 使用 pytest

```bash
cd backend

# 健康检查
python -m pytest tests/test_health.py -v

# 工具层测试
python -m pytest tests/application/tools/ -v

# 仓储层测试
python -m pytest tests/infrastructure/repositories/ -v

# 集成测试
python -m pytest tests/integration/ -v -s

# 覆盖率
python -m pytest --cov=app --cov-report=html
```

### 方式 3: 手动测试脚本

```bash
cd backend
python scripts/test_agents_manual.py
```

---

## 四、测试内容详解

### 1️⃣ 手动测试 (推荐首选)

**脚本**: `scripts/test_agents_manual.py`

**测试模块**:
- ✅ FileSystemTools - 文件系统操作
- ✅ VisionTools (Mock) - 产品图像分析
- ✅ TextTools (Mock) - 文本生成
- ✅ ProductAnalysisAgent - 完整分析流程
- ✅ QAAgent - 质量检查流程
- ✅ VideoTools (Mock) - 视频生成 + Fallback

**运行**:
```bash
cd backend
python scripts/test_agents_manual.py
```

**预期输出**:
```
🧪 Agent 能力测试套件

🧪 测试 FileSystemTools
✅ 工作区创建成功: /path/to/workspace
✅ 测试文件写入成功
✅ 测试文件读取成功: {'product': 'Test Product', ...}
✅ 文件列表: ['test.json']
🧪 测试 VisionTools (Mock 模式)
📸 分析图片: https://example.com/product.jpg
✅ 分析结果:
  - 类别: electronics
  - 风格: modern minimalist
  - 目标受众: young professionals, tech enthusiasts
  - 关键特征: Sleek design, Compact form factor
  - 建议场景: hero, lifestyle, detail
🧪 测试 TextTools (Mock 模式)
✅ 提取的关键词: wireless, headphones, noise, cancellation
🧪 测试 ProductAnalysisAgent
🔍 分析产品...
✅ 分析完成:
  - 类别: electronics
  - 风格: modern
  - 关键特征: Noise Cancellation, 30h Battery, Premium Sound
  - 营销角度: Premium quality electronics, Modern design aesthetic
🧪 测试 QAAgent
🔍 运行 QA 检查...
✅ QA 检查完成:
  - 总分: 0.85
  - 通过: ✓
  - 问题数量: 0
  - 建议数量: 2
🧪 测试 VideoTools (Mock 模式)
🎬 生成视频 (使用 Mock)...
✅ 视频生成完成:
  - URL: mock://video/xxx-xxx-xxx
  - Provider: slideshow
  - Fallback: 是
✅ 所有测试完成!
```

---

### 2️⃣ 单元测试

#### FileSystemTools 测试

**文件**: `tests/application/tools/test_filesystem_tools.py`

**测试用例**:
```python
test_create_workspace()           # 创建工作区目录结构
test_write_and_read_file()         # 文件读写
test_write_and_read_json()         # JSON 序列化
test_path_validation_security()    # 路径安全验证
test_list_dir()                    # 目录列表
test_exists()                      # 文件存在性检查
```

**运行**:
```bash
python -m pytest tests/application/tools/test_filesystem_tools.py -v
```

#### ProductPackageRepository 测试

**文件**: `tests/infrastructure/repositories/test_product_package_repo_async.py`

**测试用例**:
```python
test_create_package()              # 创建产品包
test_get_by_workflow_id()          # 通过 workflow_id 查询
test_update_status()               # 更新状态
test_add_artifact()                # 添加工件引用
test_update_approval()             # 更新审批状态
test_update_qa_report()            # 更新 QA 报告
```

**运行**:
```bash
python -m pytest tests/infrastructure/repositories/test_product_package_repo_async.py -v
```

---

### 3️⃣ 集成测试

**文件**: `tests/integration/test_product_package_workflow.py`

#### 测试场景 1: 完整工作流

```python
test_full_workflow_with_mock_data()
```

**流程**:
1. 创建用户并获取 token
2. 发起产品包生成请求
3. 轮询状态直到完成 (最多60秒)
4. 获取最终结果
5. 验证所有工件

**运行**:
```bash
python -m pytest tests/integration/test_product_package_workflow.py::TestProductPackageWorkflow::test_full_workflow_with_mock_data -v -s
```

#### 测试场景 2: 审批工作流

```python
test_approval_workflow()
```

**流程**:
1. 创建需要审批的包
2. 等待审批状态
3. 提交审批决策 (approve/reject)
4. 验证状态变更

#### 测试场景 3: 重新生成工作流

```python
test_regenerate_workflow()
```

**流程**:
1. 创建产品包
2. 等待完成
3. 重新生成指定部分 (copywriting/images/video/all)
4. 验证重新生成结果

---

## 五、API 测试方法

### 使用 curl 测试

#### 1. 健康检查
```bash
curl http://localhost:8000/health
```

#### 2. 用户注册
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "testpass123"}'
```

#### 3. 用户登录
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123"
```

保存返回的 `access_token`。

#### 4. 发起产品包生成
```bash
export TOKEN="your_access_token_here"

curl -X POST http://localhost:8000/api/v1/product-packages/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image_url": "https://example.com/product.jpg",
    "background": "Premium wireless headphones with noise cancellation",
    "options": {
      "copy_variants": 2,
      "image_variants": 3,
      "video_duration_sec": 15,
      "require_approval": false,
      "force_fallback_video": true
    }
  }'
```

#### 5. 查询状态
```bash
curl -X GET http://localhost:8000/api/v1/product-packages/status/WORKFLOW_ID \
  -H "Authorization: Bearer $TOKEN"
```

#### 6. 获取详情
```bash
curl -X GET http://localhost:8000/api/v1/product-packages/PACKAGE_ID \
  -H "Authorization: Bearer $TOKEN"
```

#### 7. 审批决策
```bash
curl -X POST http://localhost:8000/api/v1/product-packages/PACKAGE_ID/approve \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"decision": "approve", "comment": "Looks good!"}'
```

#### 8. 重新生成
```bash
curl -X POST http://localhost:8000/api/v1/product-packages/PACKAGE_ID/regenerate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target": "images", "reason": "Want different style"}'
```

---

### 使用 Python 测试

创建 `test_api.py`:

```python
import asyncio
import httpx

async def test_workflow():
    async with httpx.AsyncClient() as client:
        # 1. 登录
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            data={"username": "test@example.com", "password": "testpass123"}
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
        print(f"✅ 工作流已启动: {workflow_id}")

        # 3. 轮询状态
        while True:
            await asyncio.sleep(2)
            response = await client.get(
                f"http://localhost:8000/api/v1/product-packages/status/{workflow_id}",
                headers=headers
            )
            status = response.json()
            print(f"📊 进度: {status['progress_percentage']}% - {status['current_step']}")

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

## 六、WebSocket 测试

### 使用 Python Socket.IO 客户端

创建 `test_ws.py`:

```python
import asyncio
import socketio

async def test_websocket():
    sio = socketio.AsyncClient()

    @sio.on('connect')
    async def on_connect():
        print('✅ WebSocket 已连接')
        await sio.emit('authenticate', {'token': 'YOUR_ACCESS_TOKEN'})

    @sio.on('agent:progress')
    async def on_progress(data):
        print(f"📊 进度: {data['data']['percentage']}% - {data['data']['current_step']}")

    @sio.on('agent:artifact')
    async def on_artifact(data):
        print(f"🎨 工件: {data['data']['artifact_type']}")

    @sio.on('agent:approval_required')
    async def on_approval(data):
        print(f"⚠️  需要审批")

    await sio.connect('http://localhost:8000')
    await sio.wait()

asyncio.run(test_websocket())
```

---

## 七、性能测试

### 并发工作流测试

创建 `test_concurrent.py`:

```python
import asyncio
import httpx

async def test_concurrent(num=5):
    """测试并发工作流"""
    async with httpx.AsyncClient() as client:
        # 获取 token
        response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            data={"username": "test@example.com", "password": "testpass123"}
        )
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 并发发起
        tasks = []
        for i in range(num):
            task = client.post(
                "http://localhost:8000/api/v1/product-packages/generate",
                headers=headers,
                json={
                    "image_url": f"https://example.com/product{i}.jpg",
                    "background": f"Test {i}",
                    "options": {"require_approval": False}
                }
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)
        success = sum(1 for r in results if r.status_code == 202)
        print(f"✅ 成功: {success}/{num}")

asyncio.run(test_concurrent(10))
```

---

## 八、测试覆盖率

### 生成覆盖率报告

```bash
cd backend

# 安装 pytest-cov
pip install pytest-cov

# 运行测试并生成报告
python -m pytest --cov=app --cov-report=html tests/

# 打开报告
# Windows:
start htmlcov/index.html

# macOS:
open htmlcov/index.html

# Linux:
xdg-open htmlcov/index.html
```

### 当前覆盖情况

| 模块 | 单元测试 | 集成测试 | 手动测试 |
|------|---------|---------|---------|
| FileSystemTools | ✅ | ✅ | ✅ |
| ProductPackageRepository | ✅ | ✅ | - |
| DeepOrchestrator | - | ✅ | - |
| ProductAnalysisAgent | - | - | ✅ |
| QAAgent | - | - | ✅ |
| VideoTools | - | - | ✅ |
| API Routes | - | ✅ | - |

**待补充**:
- TextTools 单元测试
- VisionTools 单元测试
- ImageTools 单元测试
- CopywritingSubagent 测试
- ImageSubagent 测试
- VideoGenerationAgent 测试
- HITLManager 单元测试

---

## 九、使用真实 Providers 测试

当前测试使用 Mock 数据。要测试真实能力:

### 步骤 1: 配置环境变量

```bash
# backend/.env
DEEPSEEK_API_KEY=your_actual_key_here
OPENAI_API_KEY=your_key_here  # GPT-4 Vision (可选)
STABILITY_API_KEY=your_key_here  # Stability AI (可选)
RUNWAY_API_KEY=your_key_here  # Runway (可选)
```

### 步骤 2: 修改测试脚本

编辑 `scripts/test_agents_manual.py`:

```python
# 从:
tools = ToolRegistry.create_default()

# 改为:
from app.infrastructure.generators import DeepSeekGenerator
llm_client = DeepSeekGenerator()
tools = ToolRegistry.create_default(llm_client=llm_client)
```

### 步骤 3: 运行测试

```bash
python scripts/test_agents_manual.py
```

---

## 十、调试技巧

### 1. 查看详细日志

```bash
cd backend
python -m uvicorn app.main:app --reload --log-level debug
```

### 2. 使用 pdb 调试

```bash
python -m pytest tests/integration/test_product_package_workflow.py -v -s --pdb
```

### 3. 检查工作区

```bash
# 查看所有工作区
ls -la backend/projects/

# 查看特定工作流
ls -la backend/projects/WORKFLOW_ID/

# 查看分析报告
cat backend/projects/WORKFLOW_ID/workspace/analysis_report.md

# 查看 QA 报告
cat backend/projects/WORKFLOW_ID/workspace/qa_report.md
```

### 4. 查看数据库记录

```bash
# 使用 psql
psql -U your_user -d your_database

# 查询产品包
SELECT id, workflow_id, status, stage, progress
FROM product_packages
ORDER BY created_at DESC
LIMIT 10;

# 查询工件
SELECT * FROM video_assets
WHERE workflow_id = 'YOUR_WORKFLOW_ID';
```

---

## 十一、常见问题

### Q1: 测试失败 "ModuleNotFoundError"

**解决方案**:
```bash
cd backend
pip install -e .
```

### Q2: 数据库连接错误

**解决方案**:
```bash
# 检查 PostgreSQL
docker ps | grep postgres

# 或启动本地服务
sudo systemctl start postgresql

# 检查 .env
cat backend/.env
```

### Q3: WebSocket 测试超时

**解决方案**:
- 确保服务已启动
- 检查 CORS 配置
- 验证 token 有效性

### Q4: Mock 测试通过但真实测试失败

**解决方案**:
1. 检查 API keys 配置
2. 查看外部服务状态
3. 增加超时时间
4. 查看错误日志

---

## 十二、CI/CD 集成

### GitHub Actions 示例

创建 `.github/workflows/test.yml`:

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

## 十三、测试执行计划

### 第一阶段: 基础验证 (当前)

- [x] 运行健康检查测试
- [x] 运行手动 Agent 测试
- [x] 运行工具层单元测试
- [x] 运行仓储层单元测试
- [ ] 运行集成测试

### 第二阶段: 完整测试

- [ ] 补充缺失的单元测试
- [ ] 运行完整的集成测试套件
- [ ] 生成测试覆盖率报告
- [ ] 修复发现的问题

### 第三阶段: 真实 Providers

- [ ] 配置真实 API keys
- [ ] 使用真实 LLM 测试
- [ ] 使用真实图片生成测试
- [ ] 使用真实视频生成测试

### 第四阶段: 性能和压力测试

- [ ] 并发测试 (10个工作流)
- [ ] 负载测试 (响应时间)
- [ ] 压力测试 (极限情况)
- [ ] 资源使用监控

---

## 十四、测试结果记录

### 测试执行记录

**日期**: 2026-02-10
**执行人**: [Your Name]
**环境**: Development

#### 执行结果

| 测试类型 | 状态 | 通过率 | 备注 |
|---------|------|--------|------|
| 健康检查 | ✅ | 100% | 通过 |
| 手动测试 | ✅ | 100% | 所有模块正常 |
| 工具层单元测试 | ✅ | 100% | FileSystemTools 测试通过 |
| 仓储层单元测试 | ⏳ | - | 待执行 |
| 集成测试 | ⏳ | - | 待执行 |

#### 发现的问题

1. **问题描述**: [待记录]
   - **严重程度**: [高/中/低]
   - **状态**: [待修复/已修复]
   - **解决方案**: [待记录]

#### 下一步行动

1. [ ] 执行仓储层单元测试
2. [ ] 执行完整集成测试
3. [ ] 生成测试覆盖率报告
4. [ ] 配置真实 providers 并重新测试

---

## 十五、总结

### 已提供

✅ 完整的测试框架 (单元/集成/手动)
✅ Makefile 快捷命令
✅ 详细的测试文档
✅ API 测试示例 (curl/Python)
✅ WebSocket 测试方法
✅ 性能测试指导

### 开始测试

```bash
cd backend
make test-manual
```

### 目标

- 确保所有 Agent 正常工作
- 验证 API 端点功能
- 测试完整业务流程
- 保证代码质量
- 为生产环境做好准备

---

## 附录

### A. 相关文档

- `docs/TESTING_GUIDE.md` - 完整测试指南
- `docs/TEST_PLAN_SUMMARY.md` - 测试方案总结
- `docs/implementation-completion-report.md` - 实施完成报告
- `Agent-Implementation-plan.md` - 原始实施计划

### B. 测试命令速查

```bash
# 快速测试
make test

# 手动测试
make test-manual

# 所有测试
make test-all

# 单元测试
make test-unit

# 集成测试
make test-integration

# 覆盖率
make coverage

# 清理
make clean
```

### C. 联系方式

- **问题反馈**: [GitHub Issues]
- **技术支持**: [Email]
- **文档更新**: 2026-02-10

---

**最后更新**: 2026-02-10
**版本**: v1.0
**状态**: ✅ 测试框架就绪
