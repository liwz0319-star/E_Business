# 🎯 Agent 测试方案总结

## 已创建的测试文件

### 1. 单元测试 ✅
- `backend/tests/application/tools/test_filesystem_tools.py` - 文件系统工具测试
- `backend/tests/infrastructure/repositories/test_product_package_repo_async.py` - 异步仓储测试

### 2. 集成测试 ✅
- `backend/tests/integration/test_product_package_workflow.py` - 完整工作流集成测试

### 3. 手动测试脚本 ✅
- `backend/scripts/test_agents_manual.py` - 交互式 Agent 测试

### 4. 配置文件 ✅
- `backend/pyproject.test.toml` - Pytest 配置
- `backend/Makefile` - 测试快捷命令
- `backend/RUN_TESTS.md` - 测试运行脚本

### 5. 文档 ✅
- `docs/TESTING_GUIDE.md` - 完整测试指南

---

## 快速开始

### 方式 1: 使用 Makefile (推荐)

```bash
cd backend

# 运行快速测试
make test

# 运行所有测试
make test-all

# 运行手动测试
make test-manual

# 查看所有命令
make help
```

### 方式 2: 使用 pytest

```bash
cd backend

# 健康检查
python -m pytest tests/test_health.py -v

# 单元测试
python -m pytest tests/application/tools/ -v
python -m pytest tests/infrastructure/repositories/ -v

# 集成测试
python -m pytest tests/integration/ -v -s

# 覆盖率报告
python -m pytest --cov=app --cov-report=html
```

### 方式 3: 手动测试脚本

```bash
cd backend

# 运行交互式测试
python scripts/test_agents_manual.py
```

---

## 测试内容说明

### 1️⃣ FileSystemTools 测试

**测试文件**: `tests/application/tools/test_filesystem_tools.py`

**测试内容**:
- ✅ 创建工作区目录结构
- ✅ 文件读写操作
- ✅ JSON 序列化/反序列化
- ✅ 路径安全验证(防止路径遍历攻击)
- ✅ 目录列表功能
- ✅ 文件存在性检查

**运行**:
```bash
python -m pytest tests/application/tools/test_filesystem_tools.py -v
```

---

### 2️⃣ ProductPackageRepository 测试

**测试文件**: `tests/infrastructure/repositories/test_product_package_repo_async.py`

**测试内容**:
- ✅ 创建产品包记录
- ✅ 通过 workflow_id 查询
- ✅ 更新状态和阶段
- ✅ 添加工件引用
- ✅ 审批流程
- ✅ QA 报告更新

**运行**:
```bash
python -m pytest tests/infrastructure/repositories/test_product_package_repo_async.py -v
```

---

### 3️⃣ 工作流集成测试

**测试文件**: `tests/integration/test_product_package_workflow.py`

**测试场景**:
- ✅ 完整工作流(生成 → 状态查询 → 结果获取)
- ✅ 审批工作流(生成 → 审批请求 → 审批决策)
- ✅ 重新生成工作流(生成 → 部分重新生成)

**运行**:
```bash
python -m pytest tests/integration/test_product_package_workflow.py -v -s
```

---

### 4️⃣ 手动 Agent 测试

**测试文件**: `scripts/test_agents_manual.py`

**测试模块**:
- ✅ FileSystemTools - 文件系统操作
- ✅ VisionTools (Mock) - 产品图像分析
- ✅ TextTools (Mock) - 文本生成
- ✅ ProductAnalysisAgent - 完整分析流程
- ✅ QAAgent - 质量检查流程
- ✅ VideoTools (Mock) - 视频生成 + Fallback

**运行**:
```bash
python scripts/test_agents_manual.py
```

---

## 测试覆盖率

### 当前覆盖范围

| 模块 | 单元测试 | 集成测试 | 手动测试 |
|------|---------|---------|---------|
| FileSystemTools | ✅ | ✅ | ✅ |
| TextTools | ❌ | ❌ | ✅ |
| VisionTools | ❌ | ❌ | ✅ |
| ImageTools | ❌ | ❌ | ❌ |
| VideoTools | ❌ | ❌ | ✅ |
| StorageTools | ❌ | ❌ | ❌ |
| ProductAnalysisAgent | ❌ | ❌ | ✅ |
| CopywritingSubagent | ❌ | ❌ | ❌ |
| ImageSubagent | ❌ | ❌ | ❌ |
| VideoGenerationAgent | ❌ | ❌ | ❌ |
| QAAgent | ❌ | ❌ | ✅ |
| DeepOrchestrator | ❌ | ✅ | ❌ |
| HITLManager | ❌ | ✅ | ❌ |
| ProductPackageRepository | ✅ | ✅ | ❌ |
| API Routes | ❌ | ✅ | ❌ |

### 待补充的测试

1. **工具层完整单元测试**
   - TextTools
   - VisionTools
   - ImageTools
   - VideoTools
   - StorageTools

2. **Agent 层单元测试**
   - CopywritingSubagent
   - ImageSubagent
   - VideoGenerationAgent

3. **编排层测试**
   - DeepOrchestrator 状态机转换
   - HITLManager 决策逻辑

4. **API 层测试**
   - 参数验证
   - 错误处理
   - 权限控制

---

## 使用真实 Providers 测试

当前所有 Agent 测试使用 Mock 数据。要使用真实 providers:

### 步骤 1: 配置环境变量

```bash
# backend/.env
DEEPSEEK_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here  # 如果使用 GPT-4 Vision
RUNWAY_API_KEY=your_key_here  # 如果使用 Runway 视频
```

### 步骤 2: 修改测试脚本

在 `scripts/test_agents_manual.py` 中:

```python
# 从 Mock 改为真实客户端
from app.infrastructure.generators import DeepSeekGenerator

llm_client = DeepSeekGenerator()
tools = ToolRegistry.create_default(llm_client=llm_client)
```

### 步骤 3: 运行测试

```bash
python scripts/test_agents_manual.py
```

---

## 性能测试

### 并发测试

```bash
# 创建并发测试
python scripts/test_concurrent_workflows.py
```

测试内容:
- 同时发起 N 个工作流
- 测量响应时间
- 检查资源使用
- 验证数据一致性

---

## 持续集成

### GitHub Actions 配置

已在 `docs/TESTING_GUIDE.md` 提供完整配置示例。

关键步骤:
1. 启动 PostgreSQL 服务
2. 安装依赖
3. 运行数据库迁移
4. 执行测试套件
5. 生成覆盖率报告
6. 上传到 Codecov

---

## 调试技巧

### 1. 查看详细日志

```bash
# 启动服务时
python -m uvicorn app.main:app --reload --log-level debug
```

### 2. 使用 pdb 调试

```bash
# 在测试中打断点
python -m pytest tests/integration/test_product_package_workflow.py -v -s --pdb
```

### 3. 检查工作区

```bash
# 查看生成的工作区
ls -la backend/projects/

# 查看特定工作流
cat backend/projects/WORKFLOW_ID/workspace/analysis_report.md
```

---

## 常见问题

### Q: 测试失败 "Database connection error"

**A**:
```bash
# 检查 PostgreSQL
docker ps | grep postgres

# 或启动本地服务
sudo systemctl start postgresql

# 检查 .env 配置
cat backend/.env
```

### Q: WebSocket 测试超时

**A**:
- 确保服务已启动
- 验证 token 有效性
- 检查 CORS 配置

### Q: Mock 测试通过但真实测试失败

**A**:
1. 检查 API keys 配置
2. 查看外部服务状态
3. 增加超时时间
4. 查看详细错误日志

---

## 下一步

### 短期 (本周)
1. ✅ 运行所有测试验证基础功能
2. ✅ 修复发现的问题
3. 🔄 补充缺失的单元测试

### 中期 (本月)
1. 🔄 集成真实 providers
2. 🔄 添加性能测试
3. 🔄 设置 CI/CD

### 长期 (下月)
1. 🔄 负载测试和压力测试
2. 🔄 安全测试
3. 🔄 用户验收测试

---

## 总结

✅ **已提供**:
- 完整的测试框架
- 单元/集成/手动测试
- 详细的测试文档
- Makefile 快捷命令

📋 **开始测试**:
```bash
cd backend
make test
```

🎯 **目标**:
- 确保所有 Agent 正常工作
- 验证 API 端点功能
- 测试完整业务流程
- 保证代码质量
