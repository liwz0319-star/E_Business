# LangSmith 集成完成

## 已完成的工作

### 1. 添加依赖
- ✅ 在 `requirements.txt` 中添加 `langsmith>=0.1.0`

### 2. 配置系统
- ✅ 在 `app/core/config.py` 中添加 LangSmith 配置字段
  - `langchain_tracing_v2`: 启用/禁用追踪
  - `langchain_api_key`: API 密钥
  - `langchain_project`: 项目名称
  - `langchain_endpoint`: API 端点

### 3. 初始化模块
- ✅ 创建 `app/core/langchain_init.py`
  - `init_langsmith()`: 初始化 LangSmith
  - `get_langsmith_config()`: 获取配置信息
  - `enable_langsmith_tracing()`: 运行时启用
  - `disable_langsmith_tracing()`: 运行时禁用

### 4. 应用集成
- ✅ 在 `app/main.py` 中添加启动时初始化
- ✅ 在 `app/interface/routes/debug.py` 中添加配置检查端点

### 5. 文档和工具
- ✅ `backend/.env.example`: 环境变量示例
- ✅ `docs/LANGSMITH_GUIDE.md`: 详细使用指南
- ✅ `backend/test_langsmith_setup.py`: 配置测试脚本
- ✅ `backend/setup_langsmith.py`: 交互式设置向导

## 快速开始

### 方式 1：使用交互式设置向导（推荐）

```bash
cd backend
python setup_langsmith.py
```

按照提示输入您的 LangSmith API Key 和配置。

### 方式 2：手动配置

1. 编辑 `.env` 文件，添加以下配置：

```bash
# 启用 LangSmith 追踪
LANGCHAIN_TRACING_V2=true

# 您的 LangSmith API Key
LANGCHAIN_API_KEY=lsv2_pt_xxxxx...

# 项目名称
LANGCHAIN_PROJECT=e-business

# API 端点（通常使用默认值）
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

2. 启动应用：

```bash
cd backend
python -m uvicorn app.main:app --reload
```

3. 查看启动日志，确认 LangSmith 已初始化

### 验证配置

运行测试脚本：

```bash
cd backend
python test_langsmith_setup.py
```

或访问调试端点：

```bash
curl http://localhost:8000/api/v1/debug/langsmith
```

## 使用 LangSmith

### 查看追踪记录

1. 访问 [LangSmith Projects](https://smith.langchain.com/projects)
2. 选择您的项目（例如：e-business）
3. 查看 "Runs" 标签页

### 追踪的数据

您的 LangGraph Agent 会自动追踪：

#### Copywriting Agent
- Plan → Draft → Critique → Finalize

#### Image Agent
- Optimize Prompt → Generate Image → Persist Asset

每个阶段记录：
- 输入提示词
- LLM 响应
- Token 使用
- 执行时间
- 错误信息

## API 端点

### 检查 LangSmith 配置

```bash
GET /api/v1/debug/langsmith
```

响应：
```json
{
  "enabled": true,
  "project": "e-business",
  "endpoint": "https://api.smith.langchain.com",
  "api_key_configured": true,
  "tracing_env_var": "true"
}
```

### 检查环境变量

```bash
GET /api/v1/debug/langsmith/env
```

## 获取 LangSmith API Key

1. 访问 [LangSmith](https://smith.langchain.com)
2. 注册/登录账号
3. 进入 Settings → API Keys
4. 创建新的 API Key

详细步骤请参考：[docs/LANGSMITH_GUIDE.md](LANGSMITH_GUIDE.md)

## 文件清单

```
backend/
├── requirements.txt                          # 添加 langsmith 依赖
├── .env.example                              # 环境变量示例
├── test_langsmith_setup.py                   # 配置测试脚本
├── setup_langsmith.py                        # 交互式设置向导
└── app/
    ├── main.py                               # 添加 LangSmith 初始化
    ├── core/
    │   ├── config.py                         # 添加 LangSmith 配置字段
    │   └── langchain_init.py                 # LangSmith 初始化模块
    └── interface/
        └── routes/
            └── debug.py                      # 添加配置检查端点

docs/
└── LANGSMITH_GUIDE.md                        # 详细使用指南
```

## 故障排除

### 问题：追踪记录未出现

**检查**：
1. `LANGCHAIN_TRACING_V2=true`
2. `LANGCHAIN_API_KEY` 有效
3. 网络可以访问 `api.smith.langchain.com`

**调试**：
```bash
curl http://localhost:8000/api/v1/debug/langsmith/env
```

### 问题：依赖包未安装

```bash
pip install langsmith>=0.1.0
```

## 相关资源

- [LangSmith 文档](https://docs.smith.langchain.com)
- [LangChain 文档](https://python.langchain.com)
- [详细使用指南](LANGSMITH_GUIDE.md)
