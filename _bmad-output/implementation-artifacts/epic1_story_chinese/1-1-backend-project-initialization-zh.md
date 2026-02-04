# Story 1.1: 后端项目初始化

Status: done

<!-- 注意：验证是可选的。在 dev-story 之前运行 validate-create-story 进行质量检查。 -->

## 用户故事 (Story)

作为一个开发者，
我想要使用 Docker 和 Poetry 初始化 FastAPI 项目结构，
以便我拥有一个一致且可运行的开发环境。

## 验收标准 (Acceptance Criteria)

1. **给定** 一个干净的 git 分支
   **当** 我执行 `poetry install` 和 `docker-compose up -d --build`
   **那么** 会创建一个包含 `app` 和 `tests` 文件夹的 `backend` 目录

2. **并且** `pyproject.toml` 包含 fastapi, uvicorn, sqlalchemy, asyncpg, python-socketio 依赖

3. **并且** `docker-compose.yml` 成功启动 `api`, `db` 和 `redis` 容器

4. **并且** 访问 `http://localhost:8000/health` 返回 200 OK

## 任务 / 子任务 (Tasks / Subtasks)

- [x] 初始化 Python 项目 (AC 1, 2)
  - [x] 创建 `backend` 目录
  - [x] 初始化 `poetry` 项目 (Python 3.11)
  - [x] 添加依赖: `fastapi`, `uvicorn`, `sqlalchemy`, `asyncpg`, `python-socketio`, `pydantic-settings`, `alembic`
  - [x] 添加开发依赖: `pytest`, `pytest-asyncio`, `httpx`
- [x] 实现项目结构 (Clean Architecture) (AC 1)
  - [x] 创建 `app/domain` (实体, 接口)
  - [x] 创建 `app/application` (用例)
  - [x] 创建 `app/infrastructure` (实现)
  - [x] 创建 `app/interface` (API 路由)
  - [x] 创建 `app/main.py` 入口点
- [x] Docker 设置 (AC 3)
  - [x] 为后端创建 `Dockerfile` (多阶段构建)
  - [x] 创建/更新 `docker-compose.yml` (Postgres 16 + pgvector, Redis, Minio, Backend)
- [x] 健康检查端点 (AC 4)
  - [x] 在 `app/main.py` (或接口层) 中实现 `GET /health`
- [x] 初始化 Alembic 用于数据库迁移 (AC 1, 2)
  - [x] 在 backend 目录中运行 `alembic init alembic`
  - [x] 配置 `alembic.ini` 中的数据库连接 URL
  - [x] 创建 `backend/app/alembic/env.py` 并配置异步 SQLAlchemy
  - [x] 创建初始迁移模板
- [x] 创建配置模板 (AC 1, 2)
  - [x] 创建 `.env.example` 并包含所需的环境变量:
    - `DATABASE_URL` (PostgreSQL 连接)
    - `REDIS_URL` (Redis 连接)
    - `SECRET_KEY` (JWT 签名)
    - `DEEPSEEK_API_KEY` (AI 提供商)
  - [x] 使用 pydantic-settings 创建 `backend/app/core/config.py`
  - [x] 在开发说明文档中记录环境变量要求
- [x] 创建项目文档 (AC 1)
  - [x] 创建 `backend/README.md`，包含:
    - 项目概述和技术栈
    -先决条件 (Docker, Poetry)
    - 快速开始命令
    - 开发设置说明
    - 环境变量配置指南
    - 运行测试
  - [x] 添加常见问题的故障排除部分

## 开发说明 (Dev Notes)

- **架构合规性**:
  - 遵循 **实用主义整洁架构 (Pragmatic Clean Architecture)**:
    - `domain/`: 纯 Python，无外部依赖 (pydantic 除外)。
    - `application/`: 编排逻辑，依赖于 domain。
    - `infrastructure/`: 数据库，外部 API，依赖于 application/domain。
    - `interface/`: FastAPI 路由，依赖于 application。
  - **工具**: 使用 `poetry` 进行依赖管理。
  - **数据库**: 使用 `pgvector/pgvector:phgc` 镜像作为 Postgres，以支持未来的 RAG。

### 项目结构说明

- 确保 `backend/` 是 Python 代码的根目录。
- `docker-compose.yml` 应位于项目根目录 (即 `backend/` 的父目录)。

### 参考资料

- [架构决策](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/architecture.md#Implementation-Patterns)
- [Epics 来源](file:///f:/AAA Work/AIproject/E_Business/_bmad-output/planning-artifacts/epics.md#Story-1.1:-Backend-Project-Initialization)

## 开发代理记录 (Dev Agent Record)

### 使用的代理模型

Antigravity (BMad Master)

### 调试日志参考

### 完成说明列表

- 实现了标准的 FastAPI 结构 (Domain/App/Infra/Interface)。
- 配置了 Poetry 和所需的依赖。
- 创建了后端 Dockerfile 和根目录 docker-compose.yml。
- 使用异步 SQLAlchemy 配置初始化了 Alembic。
- 创建了配置模板 (.env.example, config.py)。
- 创建了包含设置说明的项目 README。
- 通过 pytest 验证了健康检查 `GET /health` 返回 200 OK。
- 验证了全栈：Docker 容器 (api, db, redis) 均运行正常。
- 验证了数据库连接池初始化成功。
- 验证了 Redis 连接已建立。

### 文件列表

- backend/pyproject.toml
- backend/Dockerfile
- docker-compose.yml
- backend/alembic.ini
- backend/app/alembic/env.py
- backend/app/alembic/script.py.mako
- .env.example
- backend/app/core/config.py
- backend/app/main.py
- backend/app/domain/__init__.py
- backend/app/application/__init__.py
- backend/app/infrastructure/__init__.py
- backend/app/interface/__init__.py
- backend/README.md
- backend/tests/test_health.py
