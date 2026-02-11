# LangSmith 集成指南

本文档介绍如何在 E-Business 项目中配置和使用 LangSmith 进行 AI 应用的追踪和监控。

## 什么是 LangSmith？

LangSmith 是 LangChain 提供的开发者平台，用于：
- **追踪**: 可视化 LLM 应用的执行流程
- **调试**: 分析和优化提示词和参数
- **测试**: 批量评估和测试不同的提示词
- **监控**: 生产环境的性能监控

## 快速开始

### 1. 获取 LangSmith API Key

1. 访问 [LangSmith](https://smith.langchain.com)
2. 注册/登录账号
3. 进入 Settings → API Keys
4. 创建新的 API Key

### 2. 配置环境变量

编辑 `.env` 文件，添加以下配置：

```bash
# 启用 LangSmith 追踪
LANGCHAIN_TRACING_V2=true

# 您的 LangSmith API Key
LANGCHAIN_API_KEY=lsv2_pt_xxxxx...

# 项目名称（会在 LangSmith 中创建对应项目）
LANGCHAIN_PROJECT=e-business

# API 端点（通常使用默认值）
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

### 3. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

`langsmith>=0.1.0` 已经包含在 requirements.txt 中。

### 4. 启动应用

```bash
python -m uvicorn app.main:app --reload
```

启动时您会看到：

```
==================================================
LANGSMITH INITIALIZATION
==================================================
LangSmith Enabled: True
LangSmith Project: e-business
LangSmith API Key Configured: True
LangSmith tracing is ACTIVE
==================================================
```

## 使用 LangSmith

### 查看追踪记录

1. 访问 [LangSmith Projects](https://smith.langchain.com/projects)
2. 选择您的项目（例如：e-business）
3. 查看 "Runs" 标签页，您会看到所有的 LLM 调用记录

### 追踪的数据

您的应用会自动追踪以下信息：

#### Copywriting Agent 工作流
- **Plan**: DeepSeek 生成营销计划
- **Draft**: 基于计划生成初稿
- **Critique**: 自我审查和改进建议
- **Finalize**: 最终打磨的文案

每个阶段会记录：
- 输入提示词
- LLM 响应内容
- Token 使用量
- 延迟时间
- 错误信息（如有）

#### Image Agent 工作流
- **Optimize Prompt**: DeepSeek 优化图像提示词
- **Generate Image**: MCP 图像生成器调用
- **Persist Asset**: 数据库持久化

### LangGraph 可视化

LangSmith 会自动可视化 LangGraph 工作流：

```
[Plan] → [Draft] → [Critique] → [Finalize] → [END]
```

您可以在 LangSmith 界面中：
- 查看每个节点的输入输出
- 检查状态转换
- 分析执行时间

## 高级配置

### 会话采样

如果您不想追踪所有会话（例如生产环境减少成本），设置采样率：

```python
# 在 app/core/langchain_init.py 中
os.environ["LANGCHAIN_SESSION_SAMPLING_RATE"] = "0.1"  # 只追踪 10% 的会话
```

### 动态启用/禁用追踪

```python
from app.core.langchain_init import enable_langsmith_tracing, disable_langsmith_tracing

# 运行时启用
enable_langsmith_tracing()

# 运行时禁用
disable_langsmith_tracing()
```

### 自定义标签

在您的 Agent 代码中添加自定义标签：

```python
from langsmith import traceable

@traceable(name="custom_copywriting_generation")
async def generate_copywriting(product_name: str, features: list):
    # 您的代码
    pass
```

## 调试技巧

### 1. 检查配置状态

访问 `/api/v1/debug/langsmith` 端点查看配置：

```bash
curl http://localhost:8000/api/v1/debug/langsmith
```

响应示例：

```json
{
  "enabled": true,
  "project": "e-business",
  "endpoint": "https://api.smith.langchain.com",
  "api_key_configured": true,
  "tracing_env_var": "true"
}
```

### 2. 查看启动日志

启动应用时检查日志输出：

```
LangSmith 初始化成功 - 项目: e-business, 端点: https://api.smith.langchain.com
```

如果看到警告：

```
LangSmith 追踪已启用，但未提供 API key
```

请检查 `LANGCHAIN_API_KEY` 环境变量。

### 3. 测试追踪

触发一个文案生成请求：

```bash
curl -X POST http://localhost:8000/api/v1/copywriting/generate \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "智能手表",
    "features": ["GPS定位", "心率监测", "防水"]
  }'
```

然后在 LangSmith 项目页面应该能看到新的运行记录。

## 成本考虑

LangSmith 定价基于：
- 追踪的运行次数
- 存储的日志大小

建议：
- 开发环境：100% 追踪（`LANGCHAIN_TRACING_V2=true`）
- 生产环境：采样追踪（`LANGCHAIN_SESSION_SAMPLING_RATE=0.1`）

参考：[LangSmith Pricing](https://smith.langchain.com/pricing)

## 故障排除

### 问题：追踪记录未出现在 LangSmith

**检查清单**：
1. ✅ `LANGCHAIN_TRACING_V2=true`
2. ✅ `LANGCHAIN_API_KEY` 有效
3. ✅ 网络可以访问 `api.smith.langchain.com`
4. ✅ 项目名称正确

**调试命令**：
```bash
# 检查环境变量
echo $LANGCHAIN_TRACING_V2
echo $LANGCHAIN_API_KEY
echo $LANGCHAIN_PROJECT
```

### 问题：导入错误

确保安装了最新版本：
```bash
pip install --upgrade langsmith langchain-core langgraph
```

### 问题：认证失败

检查 API Key 格式：
- 正确：`lsv2_pt_xxxxx...`
- 错误：可能是旧版本的 `sk-xxxxx` 格式

## 相关资源

- [LangSmith 官方文档](https://docs.smith.langchain.com)
- [LangChain 文档](https://python.langchain.com)
- [项目文档](../README.md)

## 支持

如有问题，请：
1. 查看本文档的故障排除部分
2. 检查 [LangSmith Status](https://status.smith.langchain.com)
3. 提交 Issue 到项目仓库
