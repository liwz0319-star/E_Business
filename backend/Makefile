# Makefile for running tests
# 使用方法: make test 或 make test-all

.PHONY: help test test-all test-unit test-integration test-e2e test-manual clean

# 默认目标
help:
	@echo "可用命令:"
	@echo "  make test          - 运行健康检查测试"
	@echo "  make test-all      - 运行所有测试"
	@echo "  make test-unit     - 运行单元测试"
	@echo "  make test-integration - 运行集成测试"
	@echo "  make test-e2e      - 运行 E2E 测试"
	@echo "  make test-manual   - 运行手动测试"
	@echo "  make test-watch    - 监视文件变化自动测试"
	@echo "  make clean         - 清理测试缓存"
	@echo "  make coverage      - 生成测试覆盖率报告"

# 快速测试
test:
	@echo "运行健康检查测试..."
	python -m pytest tests/test_health.py -v

# 所有测试
test-all:
	@echo "运行所有测试..."
	python -m pytest tests/ -v

# 单元测试
test-unit:
	@echo "运行单元测试..."
	python -m pytest tests/application/ tests/infrastructure/ -v

# 集成测试
test-integration:
	@echo "运行集成测试..."
	python -m pytest tests/integration/ -v -s

# E2E 测试
test-e2e:
	@echo "运行 E2E 测试..."
	python -m pytest tests/e2e/ -v -s

# 手动测试
test-manual:
	@echo "运行手动测试..."
	python scripts/test_agents_manual.py

# 监视模式
test-watch:
	@echo "监视文件变化并自动测试..."
	python -m pytest tests/ -v -f

# 清理
clean:
	@echo "清理测试缓存..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "清理完成"

# 覆盖率报告
coverage:
	@echo "生成测试覆盖率报告..."
	python -m pytest tests/ --cov=app --cov-report=html --cov-report=term
	@echo "报告已生成: htmlcov/index.html"

# 数据库迁移
migrate:
	@echo "运行数据库迁移..."
	python -m alembic upgrade head

# 回滚迁移
migrate-down:
	@echo "回滚数据库迁移..."
	python -m alembic downgrade -1

# 启动服务
serve:
	@echo "启动开发服务器..."
	python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 代码格式化
format:
	@echo "格式化代码..."
	black app/ tests/
	isort app/ tests/

# 代码检查
lint:
	@echo "检查代码..."
	black --check app/ tests/
	isort --check-only app/ tests/
	flake8 app/ tests/
	mypy app/

# 类型检查
type-check:
	@echo "类型检查..."
	mypy app/

# 安装依赖
install:
	@echo "安装依赖..."
	pip install -e .
	pip install pytest pytest-asyncio pytest-cov black isort flake8 mypy

# 所有检查
check: lint type-check test
	@echo "✅ 所有检查通过!"
