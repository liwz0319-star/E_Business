# 🔧 修复 Render 部署 - 添加数据库指南

## 问题
应用启动失败，错误：`ConnectionRefusedError: [Errno 111] Connection refused`

**原因**：缺少 PostgreSQL 数据库

---

## ✅ 解决方案：在 Render 添加 PostgreSQL

### 步骤 1: 创建 PostgreSQL 数据库

1. **访问 Render Dashboard**
   ```
   https://dashboard.render.com
   ```

2. **点击 "New +" 按钮**（右上角）

3. **选择 "PostgreSQL"**

4. **配置数据库**：

   | 字段 | 填写内容 |
   |------|----------|
   | **Name** | `e-business-db` |
   | **Database** | `e_business` |
   | **User** | `e_business_user` |
   | **Region** | `Singapore`（与应用相同）|
   | **Plan** | `Free` |

5. **点击 "Create Database"**

6. **等待创建完成**（约 1-2 分钟）
   - 状态会从 "Deploying" 变为 "Available"

---

### 步骤 2: 获取数据库连接 URL

1. **在 Dashboard 中找到刚创建的数据库** `e-business-db`

2. **点击进入数据库详情页**

3. **滚动到 "Connections" 部分**

4. **找到 "Internal Connections"**
   ```
   复制这个 URL（类似）：
   postgresql://e_business_user:password@hostname/e_business
   ```

5. **复制完整的 Database URL**

---

### 步骤 3: 将数据库连接到应用

1. **回到 "e-business-api" 服务**

2. **点击 "Environment" 标签**

3. **添加新的环境变量**：

   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | `粘贴刚才复制的 URL` |

   **完整示例**：
   ```bash
   DATABASE_URL=postgresql://e_business_user:xxxxx@hostname/e_business
   ```

4. **保存更改**

---

### 步骤 4: 重新部署应用

1. **点击 "Manual Deploy" 按钮**（右上角）

2. **选择 "Deploy latest commit"**

3. **等待部署完成**（2-3 分钟）

4. **查看日志**：
   - 点击 **"Logs"** 标签
   - 应该看到：
     ```
     INFO:     Application startup complete.
     INFO:     Uvicorn running on port 10000
     ```

5. **状态变为 "Live"**（绿色）✅

---

## ✅ 验证部署成功

### 1. 健康检查
```bash
curl https://e-business-api.onrender.com/health
```

应该返回：
```json
{"status": "ok"}
```

### 2. 检查 LangSmith
```bash
curl https://e-business-api.onrender.com/api/v1/debug/langsmith
```

应该返回：
```json
{
  "enabled": true,
  "project": "e-business",
  "api_key_configured": true
}
```

---

## 📊 数据库迁移（可选）

如果需要运行数据库迁移：

1. **在 Render Dashboard**
   - 进入 "e-business-api" 服务
   - 点击 **"Shell"** 标签

2. **运行迁移命令**：
   ```bash
   cd backend
   python -m alembic upgrade head
   ```

3. **点击 "Deploy"** 重新部署

---

## 🎯 完成！

现在您的应用应该：
- ✅ 成功启动
- ✅ 连接到数据库
- ✅ LangSmith 追踪已启用
- ✅ 可以处理 API 请求

---

## 🆘 如果还有问题

### 问题 1: 数据库连接仍然失败

**检查**：
- DATABASE_URL 是否正确复制
- 数据库状态是否为 "Available"
- Region 是否一致（都在 Singapore）

**解决**：
- 删除并重新创建 DATABASE_URL
- 确保使用 "Internal Connection" URL（不是 External）

### 问题 2: 应用仍然失败

**检查日志**：
- 复制新的错误信息
- 查看是否还有其他问题

---

## 📚 相关资源

- [Render PostgreSQL 文档](https://render.com/docs/databases)
- [环境变量配置](https://render.com/docs/env-vars)
- [数据库连接示例](https://render.com/docs/databases#connecting-from-services)
