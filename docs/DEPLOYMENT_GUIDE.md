# 部署指南

本文档说明如何将 E-Business 项目部署到生产环境，并配置 LangSmith 监控。

## 📋 部署架构

```
┌─────────────────────────────────────────────────────────┐
│                     生产环境                             │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐      ┌──────────────┐               │
│  │  Nginx/Caddy │ ───> │   FastAPI    │               │
│  │   (反向代理)  │      │   (后端)     │               │
│  └──────────────┘      └──────────────┘               │
│                                │                       │
│                         ┌──────┴──────┐               │
│                         │             │               │
│                    ┌────▼──┐    ┌────▼────┐          │
│                    │  PG   │    │  Redis  │          │
│                    └───────┘    └─────────┘          │
│                                │                       │
│                         ┌──────▼──────┐               │
│                         │  LangSmith  │ ◀─── 监控     │
│                         │  (追踪数据)  │               │
│                         └─────────────┘               │
└─────────────────────────────────────────────────────────┘
```

## 🚀 部署选项

### 选项 1: Railway （推荐 - 最简单）

**优点**:
- ✅ 零配置，自动检测
- ✅ 内置 PostgreSQL、Redis
- ✅ 自动 HTTPS
- ✅ 免费额度

**步骤**:

```bash
# 1. 安装 Railway CLI
npm install -g railway

# 2. 登录
railway login

# 3. 初始化项目
cd backend
railway init

# 4. 设置环境变量
railway variables set DEEPSEEK_API_KEY=your_api_key
railway variables set LANGCHAIN_TRACING_V2=true
railway variables set LANGCHAIN_API_KEY=your_langsmith_key
railway variables set LANGCHAIN_PROJECT=e-business

# 5. 部署
railway up
```

### 选项 2: Render

**步骤**:

1. **准备代码**
```bash
git init
git add .
git commit -m "Ready for deployment"
git push origin main
```

2. **创建 Render 服务**
   - 访问 https://render.com
   - 点击 "New +" → "Web Service"
   - 连接 GitHub 仓库
   - 配置：
     - **Root Directory**: `backend`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - 添加环境变量：
     - `DEEPSEEK_API_KEY`
     - `LANGCHAIN_TRACING_V2=true`
     - `LANGCHAIN_API_KEY`
     - `LANGCHAIN_PROJECT=e-business`

3. **添加数据库**
   - 在 Render 创建 PostgreSQL
   - 获取内部数据库 URL
   - 设置 `DATABASE_URL` 环境变量

### 选项 3: Docker 部署（自建服务器）

**使用 Docker Compose**:

```bash
# 1. 创建生产环境配置
cp .env.example .env.prod

# 2. 编辑 .env.prod，填入真实值
nano .env.prod

# 3. 启动所有服务
docker-compose -f docker-compose.prod.yml up -d

# 4. 查看日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 5. 运行数据库迁移
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head
```

**环境变量配置 (.env.prod)**:

```bash
# 数据库
DATABASE_URL=postgresql+asyncpg://postgres:password@postgres:5432/e_business
REDIS_URL=redis://redis:6379/0

# API Keys
DEEPSEEK_API_KEY=your_deepseek_api_key
SECRET_KEY=your_secret_key_here

# LangSmith（关键配置）
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=lsv2_pt_your_langsmith_key
LANGCHAIN_PROJECT=e-business
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com

# MinIO
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin

# 应用配置
APP_ENV=production
DEBUG=false
LOG_LEVEL=INFO
```

### 选项 4: Kubernetes

如果您有 Kubernetes 集群，可以使用以下配置：

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: e-business-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: your-registry/e-business:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        - name: DEEPSEEK_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secret
              key: deepseek
        - name: LANGCHAIN_TRACING_V2
          value: "true"
        - name: LANGCHAIN_API_KEY
          valueFrom:
            secretKeyRef:
              name: langsmith-secret
              key: api-key
        - name: LANGCHAIN_PROJECT
          value: "e-business"
```

## 🔧 LangSmith 配置说明

### LangSmith 的作用

**重要**: LangSmith 不是部署平台，而是监控工具！

```
┌─────────────────────────────────────────┐
│  您的应用 (部署在 Railway/Render/VPS)    │
│                                         │
│  Copywriting Agent ─┐                   │
│  Image Agent ───────┤──► LangSmith API  │
│                     │   (发送追踪数据)   │
└─────────────────────┼───────────────────┘
                      │
                      ▼
         ┌────────────────────────┐
         │  smith.langchain.com   │
         │  - 查看追踪记录         │
         │  - 调试提示词           │
         │  - 监控性能             │
         └────────────────────────┘
```

### 关键环境变量

| 变量 | 说明 | 示例 |
|-----|------|------|
| `LANGCHAIN_TRACING_V2` | 启用追踪 | `true` |
| `LANGCHAIN_API_KEY` | LangSmith API Key | `lsv2_pt_xxx` |
| `LANGCHAIN_PROJECT` | 项目名称 | `e-business` |
| `LANGCHAIN_ENDPOINT` | API 端点 | `https://api.smith.langchain.com` |

### 获取 LangSmith API Key

1. 访问 https://smith.langchain.com
2. 注册/登录
3. Settings → API Keys → Create Key

### 验证 LangSmith 追踪

部署后，访问：
```bash
curl https://your-app.com/api/v1/debug/langsmith
```

响应：
```json
{
  "enabled": true,
  "project": "e-business",
  "api_key_configured": true
}
```

## 📊 监控和日志

### 查看 LangSmith 追踪

1. 访问 https://smith.langchain.com/projects
2. 选择 "e-business" 项目
3. 查看实时追踪

### 应用日志

```bash
# Docker
docker-compose -f docker-compose.prod.yml logs -f backend

# Railway
railway logs

# Render
# 在 Dashboard 查看 Logs
```

## 🔒 安全检查清单

部署前确保：

- [ ] 更换所有默认密码
- [ ] 使用强随机 `SECRET_KEY`
- [ ] 设置 `DEBUG=false`
- [ ] 配置 HTTPS
- [ ] 限制 CORS 源
- [ ] API Key 不提交到 Git
- [ ] 使用环境变量或 Secrets

## 🎯 快速部署推荐

**如果您是第一次部署**，推荐使用 **Railway**:

```bash
# 1. 安装 CLI
npm install -g railway

# 2. 登录并部署
railway login
railway init
railway up

# 3. 配置环境变量
railway variables set DEEPSEEK_API_KEY=xxx
railway variables set LANGCHAIN_API_KEY=xxx
railway variables set LANGCHAIN_TRACING_V2=true

# 4. 完成！访问您的 URL
```

## 📝 总结

| 组件 | 部署位置 | 说明 |
|-----|---------|------|
| **应用代码** | Railway/Render/VPS | 您的 FastAPI 应用 |
| **数据库** | Railway/Render/自建 | PostgreSQL + Redis |
| **LangSmith** | smith.langchain.com | 监控服务（不是部署目标） |

**关键点**:
- ✅ 应用部署到云平台
- ✅ LangSmith 用于监控，不是部署平台
- ✅ 通过环境变量配置 LangSmith API Key
- ✅ 访问 smith.langchain.com 查看追踪

## 🆘 故障排除

### LangSmith 追踪不工作

1. 检查环境变量是否正确设置
2. 访问 `/api/v1/debug/langsmith` 检查配置
3. 确认网络可以访问 `api.smith.langchain.com`

### 应用无法启动

1. 检查日志: `docker-compose logs backend`
2. 验证数据库连接
3. 确认所有环境变量已设置

## 📚 相关资源

- [Railway 文档](https://docs.railway.app)
- [Render 文档](https://render.com/docs)
- [LangSmith 文档](https://docs.smith.langchain.com)
- [Docker 文档](https://docs.docker.com)
