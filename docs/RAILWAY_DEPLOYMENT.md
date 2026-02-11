# 🚀 Railway 部署指南

## 方式 1: 使用部署脚本（推荐用于 CLI 用户）

```bash
# 给脚本添加执行权限
chmod +x deploy_to_railway.sh

# 运行脚本
./deploy_to_railway.sh
```

脚本会引导您完成：
1. ✅ 检查/安装 Railway CLI
2. ✅ 登录 Railway
3. ✅ 初始化项目
4. ✅ 配置环境变量
5. ✅ 添加数据库（可选）
6. ✅ 部署应用

---

## 方式 2: 使用 Railway Web UI（推荐 - 最简单）

### 步骤 1: 推送代码到 GitHub

```bash
# 初始化 Git 仓库（如果还没有）
git init

# 添加所有文件
git add .

# 提交
git commit -m "Ready for Railway deployment"

# 添加远程仓库（替换为您的 GitHub 仓库地址）
git remote add origin https://github.com/YOUR_USERNAME/e-business.git

# 推送代码
git push -u origin main
```

### 步骤 2: 在 Railway 创建项目

1. **访问 Railway**
   - 打开 https://railway.app/
   - 登录您的账号（如果没有，请先注册）

2. **创建新项目**
   - 点击 "New Project" 或 "New Project +"
   - 选择 "Deploy from GitHub repo"

3. **连接 GitHub 仓库**
   - 如果是第一次使用，点击 "Configure GitHub App"
   - 授权 Railway 访问您的 GitHub
   - 选择 `e-business` 仓库

4. **配置部署设置**
   - **Root Directory**: 留空或设置为 `backend`
   - **Builder**: 选择 "Nixpacks"（自动检测）
   - Railway 会自动检测 Python 项目

5. **添加环境变量**
   在项目的 "Variables" 标签页添加：
   ```bash
   DEEPSEEK_API_KEY=your_deepseek_api_key
   LANGCHAIN_API_KEY=lsv2_pt_your_langsmith_key
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_PROJECT=e-business
   ```

6. **部署**
   - 点击 "Deploy" 或 "Deploy Now"
   - 等待几分钟部署完成

7. **获取应用 URL**
   - 部署完成后，点击项目名称
   - 在 "Networking" 或 "Domains" 标签查看您的应用 URL
   - 格式：`https://your-app-name.up.railway.app`

### 步骤 3: 添加数据库（可选）

如果需要在 Railway 上托管 PostgreSQL：

1. 在项目中点击 "New Service"
2. 选择 "Database" → "Add PostgreSQL"
3. Railway 会自动创建 `DATABASE_URL` 环境变量

### 步骤 4: 验证部署

访问您的应用：
```bash
# 健康检查
curl https://your-app-url.up.railway.app/health

# 检查 LangSmith 配置
curl https://your-app-url.up.railway.app/api/v1/debug/langsmith
```

---

## 方式 3: 使用 Railway CLI

```bash
# 1. 安装 Railway CLI
npm install -g @railway/cli

# 2. 登录（会打开浏览器）
railway login

# 3. 初始化项目
cd backend
railway init

# 4. 设置环境变量
railway variables set DEEPSEEK_API_KEY=your_key
railway variables set LANGCHAIN_API_KEY=your_key
railway variables set LANGCHAIN_TRACING_V2=true
railway variables set LANGCHAIN_PROJECT=e-business

# 5. 添加数据库（可选）
railway add postgresql

# 6. 部署
railway up

# 7. 查看状态
railway status

# 8. 打开 Dashboard
railway open
```

---

## 🔧 环境变量说明

### 必需变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | `sk-xxxxx` |
| `LANGCHAIN_API_KEY` | LangSmith API 密钥 | `lsv2_pt_xxxxx` |

### 可选变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `LANGCHAIN_TRACING_V2` | 启用 LangSmith | `true` |
| `LANGCHAIN_PROJECT` | LangSmith 项目名 | `e-business` |
| `DATABASE_URL` | PostgreSQL 连接 | Railway 自动提供 |
| `REDIS_URL` | Redis 连接 | Railway 自动提供 |

---

## 📊 LangSmith 监控

部署后，LangSmith 会自动追踪所有 AI 调用：

1. **访问 LangSmith**
   ```
   https://smith.langchain.com/projects
   ```

2. **选择项目**
   - 找到 "e-business" 项目
   - 点击进入查看详情

3. **查看追踪**
   - 点击 "Runs" 查看所有 LLM 调用
   - 点击具体记录查看详细信息

### 可追踪的工作流

- ✅ **Copywriting Agent**: Plan → Draft → Critique → Finalize
- ✅ **Image Agent**: Optimize Prompt → Generate Image → Persist

---

## 🎯 部署后检查清单

部署完成后，请确认：

- [ ] 访问应用 URL 返回正常响应
- [ ] `/health` 端点返回 `{"status": "ok"}`
- [ ] `/api/v1/debug/langsmith` 显示配置正确
- [ ] LangSmith 项目中有追踪记录出现
- [ ] 测试一个文案生成请求

---

## 🔍 监控和日志

### 查看实时日志

```bash
# CLI 方式
railway logs -f

# Web UI 方式
# 在 Railway Dashboard 中点击 "View Logs"
```

### 查看部署状态

```bash
railway status
```

### 打开项目 Dashboard

```bash
railway open
```

---

## 🆘 常见问题

### 1. 部署失败

**检查**:
- 确认 `requirements.txt` 在仓库中
- 确认 `app/main.py` 存在
- 查看部署日志：`railway logs`

### 2. 环境变量未生效

**解决**:
- 在 Railway Dashboard 的 Variables 标签页重新设置
- 重新部署：`railway up`

### 3. LangSmith 追踪不工作

**检查**:
- `LANGCHAIN_API_KEY` 格式是否正确（`lsv2_pt_...`）
- `LANGCHAIN_TRACING_V2=true` 已设置
- 访问 `/api/v1/debug/langsmith` 检查配置

### 4. 数据库连接错误

**解决**:
- 添加 PostgreSQL 服务：`railway add postgresql`
- Railway 会自动设置 `DATABASE_URL`

---

## 📚 相关链接

- [Railway 文档](https://docs.railway.app)
- [Railway 定价](https://railway.app/pricing)
- [LangSmith 文档](https://docs.smith.langchain.com)
- [项目 GitHub](https://github.com/yourusername/e-business)

---

## 🎉 完成！

部署成功后：

1. ✅ 您的应用运行在 Railway 上
2. ✅ LangSmith 正在监控所有 AI 调用
3. ✅ 访问 smith.langchain.com 查看追踪记录

**开始使用您的 AI E-Business 平台吧！** 🚀
