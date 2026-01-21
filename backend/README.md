# E-Business Backend API

FastAPI 后端服务，采用 Clean Architecture 架构设计。

## 技术栈

- **Python 3.11+** - 编程语言
- **FastAPI** - 高性能异步 Web 框架
- **SQLAlchemy 2.0** - 异步 ORM
- **PostgreSQL + pgvector** - 数据库 (支持向量搜索)
- **Redis** - 缓存和实时通信
- **MinIO** - 对象存储
- **Alembic** - 数据库迁移
- **Poetry** - 依赖管理
- **Docker** - 容器化部署

## 项目结构

```
backend/
├── app/
│   ├── alembic/          # 数据库迁移脚本
│   │   ├── versions/     # 迁移版本
│   │   ├── env.py        # Alembic 环境配置
│   │   └── script.py.mako
│   ├── application/      # 用例层 (业务逻辑)
│   ├── core/             # 核心配置
│   │   └── config.py     # 应用配置
│   ├── domain/           # 领域层 (实体、接口)
│   ├── infrastructure/   # 基础设施层 (数据库、外部API)
│   ├── interface/        # 接口层 (API 路由)
│   └── main.py           # 应用入口
├── tests/                # 测试目录
├── alembic.ini           # Alembic 配置
├── Dockerfile            # Docker 构建文件
└── pyproject.toml        # Poetry 依赖配置
```

## 前置条件

- Docker & Docker Compose
- Python 3.11+
- Poetry (可选，用于本地开发)

## 快速启动

### 使用 Docker (推荐)

```bash
# 在项目根目录
docker-compose up -d --build

# 检查服务状态
docker-compose ps

# 验证健康检查
curl http://localhost:8000/health
```

### 本地开发

```bash
# 1. 进入 backend 目录
cd backend

# 2. 安装依赖
poetry install

# 3. 复制环境变量配置
cp ../.env.example .env
# 编辑 .env 文件，填入实际配置

# 4. 启动依赖服务 (PostgreSQL, Redis, MinIO)
docker-compose up -d db redis minio

# 5. 运行数据库迁移
poetry run alembic upgrade head

# 6. 启动开发服务器
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 环境变量配置

| 变量名 | 描述 | 默认值 |
|--------|------|--------|
| `DATABASE_URL` | PostgreSQL 连接 URL | `postgresql+asyncpg://postgres:postgres@localhost:5432/e_business` |
| `REDIS_URL` | Redis 连接 URL | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT 签名密钥 | - (必须设置) |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | - (AI 功能必需) |
| `MINIO_ENDPOINT` | MinIO 端点 | `localhost:9000` |
| `APP_ENV` | 运行环境 | `development` |

完整配置请参考 `.env.example` 文件。

## 数据库迁移

```bash
# 创建新迁移
poetry run alembic revision --autogenerate -m "描述"

# 执行迁移
poetry run alembic upgrade head

# 回滚上一个版本
poetry run alembic downgrade -1

# 查看当前版本
poetry run alembic current
```

## 运行测试

```bash
# 运行所有测试
poetry run pytest

# 运行并显示覆盖率
poetry run pytest --cov=app

# 运行特定测试
poetry run pytest tests/test_health.py -v
```

## API 文档

服务启动后访问:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## 故障排查

### 数据库连接失败

1. 确认 PostgreSQL 容器正在运行: `docker-compose ps db`
2. 检查连接 URL 配置是否正确
3. 确认端口 5432 未被占用

### Redis 连接失败

1. 确认 Redis 容器正在运行: `docker-compose ps redis`
2. 检查 REDIS_URL 配置

### Docker 构建失败

1. 清理 Docker 缓存: `docker-compose build --no-cache`
2. 检查网络连接 (可能需要配置镜像源)
3. 确认 Dockerfile 中的基础镜像可访问

### 依赖安装失败

1. 使用国内镜像源:
   ```bash
   poetry source add tsinghua https://pypi.tuna.tsinghua.edu.cn/simple
   poetry install
   ```

### 端口冲突

如果 8000 端口被占用，可以修改启动命令:
```bash
poetry run uvicorn app.main:app --reload --port 8001
```

## 开发规范

- 遵循 Clean Architecture 分层原则
- Domain 层不依赖任何外部库
- 使用 AsyncIO 进行异步编程
- 所有配置通过环境变量管理
- 编写单元测试覆盖核心业务逻辑
