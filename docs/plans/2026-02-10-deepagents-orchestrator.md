# DeepAgents 多 Agent 编排系统实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 构建 DeepAgents 主导的电商多 Agent 内容生产系统,实现"一次上传图片+背景文案,产出文案+上架组图+广告视频"的端到端生产线。

**架构:**
- **编排层:** DeepOrchestrator (主 Agent) + 5 个 Subagent (ProductAnalysis, Copywriting, Image, Video, QAReview)
- **工具层:** 原子化 text/image/video/storage 工具
- **存储层:** 混合模式 (数据库为真相源 + 文件工作区)
- **可靠性:** LangGraph Checkpointer + 幂等键 + 重试 + 降级路径

**技术栈:**
- DeepAgents (LangGraph)
- FastAPI + WebSocket
- PostgreSQL + SQLAlchemy
- Pytest (TDD)

**参考文档:** `Agent-plan2.md`

---

## Phase 1: 基础设施 - 数据模型与仓储 (M1 核心基础)

### Task 1.1: 创建 ProductPackage 数据模型

**目标:** 定义产品包的数据库模型,支持状态机和资产关联

**Files:**
- Create: `backend/app/infrastructure/database/models.py` (添加 ProductPackageModel)
- Create: `backend/tests/infrastructure/database/test_product_package_model.py`
- Modify: `backend/app/infrastructure/database/models.py` (导入新模型)

**Step 1: 写失败的测试**

创建 `backend/tests/infrastructure/database/test_product_package_model.py`:

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.database.models import Base, ProductPackageModel

@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_create_product_package_minimal(db_session):
    """测试:创建最小产品包记录"""
    package = ProductPackageModel(
        workflow_id="test-wf-001",
        status="pending",
        stage="analysis",
        user_id="test-user"
    )
    db_session.add(package)
    db_session.commit()
    db_session.refresh(package)

    assert package.id is not None
    assert package.workflow_id == "test-wf-001"
    assert package.status == "pending"
    assert package.stage == "analysis"
    assert package.created_at is not None

def test_product_package_status_transitions(db_session):
    """测试:状态机转换 (pending -> running -> completed)"""
    package = ProductPackageModel(
        workflow_id="test-wf-002",
        status="pending",
        stage="analysis",
        user_id="test-user"
    )
    db_session.add(package)
    db_session.commit()

    # pending -> running
    package.status = "running"
    db_session.commit()
    db_session.refresh(package)
    assert package.status == "running"

    # running -> completed
    package.status = "completed"
    db_session.commit()
    db_session.refresh(package)
    assert package.status == "completed"

def test_product_package_with_analysis_data(db_session):
    """测试:保存产品分析结果"""
    package = ProductPackageModel(
        workflow_id="test-wf-003",
        status="running",
        stage="copywriting",
        user_id="test-user",
        analysis_data={
            "product_category": "electronics",
            "target_audience": "young professionals",
            "key_selling_points": ["portable", "high capacity"]
        }
    )
    db_session.add(package)
    db_session.commit()
    db_session.refresh(package)

    assert package.analysis_data["product_category"] == "electronics"
    assert len(package.analysis_data["key_selling_points"]) == 3

def test_product_package_artifacts_tracking(db_session):
    """测试:跟踪生成的工件 (文案/图片/视频)"""
    package = ProductPackageModel(
        workflow_id="test-wf-004",
        status="running",
        stage="image_generation",
        user_id="test-user"
    )
    db_session.add(package)
    db_session.commit()

    # 添加文案工件
    package.artifacts = {
        "copywriting": ["cp-001", "cp-002"],
        "images": ["img-001", "img-002", "img-003"],
        "video": None  # 尚未生成
    }
    db_session.commit()
    db_session.refresh(package)

    assert len(package.artifacts["copywriting"]) == 2
    assert len(package.artifacts["images"]) == 3
    assert package.artifacts["video"] is None
```

**Step 2: 运行测试验证失败**

```bash
cd backend
poetry run pytest tests/infrastructure/database/test_product_package_model.py -v
```

**预期失败:** `ImportError: cannot import name 'ProductPackageModel'`

**Step 3: 写最小实现**

修改 `backend/app/infrastructure/database/models.py`,添加:

```python
from sqlalchemy import Column, String, JSON, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

class ProductPackageModel(Base):
    """产品包聚合根 - 工作流执行主记录"""
    __tablename__ = "product_packages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(String(50), nullable=False, default="pending")  # pending/running/completed/failed/approval_required
    stage = Column(String(50), nullable=False, default="analysis")  # analysis/copywriting/image_generation/video_generation/qa_review
    progress = Column(JSON, default={"percentage": 0, "current_step": "init"})

    # 输入数据
    input_data = Column(JSON, nullable=False)  # {image_url/background/options}

    # 分析结果
    analysis_data = Column(JSON)  # {product_category/target_audience/key_selling_points}

    # 生成的工件引用
    artifacts = Column(JSON, default={})  # {copywriting: [], images: [], video: video_id}

    # HITL 相关
    approval_status = Column(String(50), default="pending")  # pending/approved/rejected
    qa_report = Column(JSON)  # {score: 0.9, issues: [], suggestions: []}

    # 审计字段
    user_id = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)

    def __repr__(self):
        return f"<ProductPackage(id={self.id}, workflow_id={self.workflow_id}, status={self.status})>"
```

**Step 4: 运行测试验证通过**

```bash
cd backend
poetry run pytest tests/infrastructure/database/test_product_package_model.py -v
```

**预期:** 所有测试通过 ✅

**Step 5: 提交**

```bash
cd backend
git add app/infrastructure/database/models.py tests/infrastructure/database/test_product_package_model.py
git commit -m "feat(database): add ProductPackageModel with status machine and artifacts tracking"
```

---

### Task 1.2: 创建 ProductPackageRepository

**目标:** 实现数据访问层,封装 CRUD 操作

**Files:**
- Create: `backend/app/infrastructure/repositories/product_package_repository.py`
- Create: `backend/tests/infrastructure/repositories/test_product_package_repository.py`

**Step 1: 写失败的测试**

创建 `backend/tests/infrastructure/repositories/test_product_package_repository.py`:

```python
import pytest
from app.infrastructure.repositories.product_package_repository import ProductPackageRepository
from app.infrastructure.database.models import Base, ProductPackageModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="function")
def repo_and_session():
    """创建仓库和测试会话"""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    repo = ProductPackageRepository(session)
    yield repo, session
    session.close()

def test_create_package(repo_and_session):
    """测试:创建新产品包"""
    repo, session = repo_and_session

    package = repo.create({
        "workflow_id": "wf-001",
        "user_id": "user-123",
        "input_data": {"image_url": "http://example.com/img.jpg", "background": "test"}
    })

    assert package.id is not None
    assert package.workflow_id == "wf-001"
    assert package.status == "pending"

def test_get_by_workflow_id(repo_and_session):
    """测试:通过 workflow_id 查询"""
    repo, session = repo_and_session

    # 创建
    repo.create({
        "workflow_id": "wf-002",
        "user_id": "user-456",
        "input_data": {"background": "test"}
    })

    # 查询
    found = repo.get_by_workflow_id("wf-002")
    assert found is not None
    assert found.workflow_id == "wf-002"

    # 不存在
    not_found = repo.get_by_workflow_id("wf-999")
    assert not_found is None

def test_update_status(repo_and_session):
    """测试:更新状态和进度"""
    repo, session = repo_and_session

    package = repo.create({
        "workflow_id": "wf-003",
        "user_id": "user-789",
        "input_data": {}
    })

    updated = repo.update_status(
        package.id,
        status="running",
        stage="copywriting",
        progress={"percentage": 25, "current_step": "generating_copywriting"}
    )

    assert updated.status == "running"
    assert updated.stage == "copywriting"
    assert updated.progress["percentage"] == 25

def test_add_artifact(repo_and_session):
    """测试:添加生成的工件"""
    repo, session = repo_and_session

    package = repo.create({
        "workflow_id": "wf-004",
        "user_id": "user-abc",
        "input_data": {}
    })

    # 添加文案
    repo.add_artifact(package.id, "copywriting", "cp-001")
    repo.add_artifact(package.id, "copywriting", "cp-002")

    updated = repo.get_by_workflow_id("wf-004")
    assert len(updated.artifacts["copywriting"]) == 2
    assert "cp-001" in updated.artifacts["copywriting"]
```

**Step 2: 运行测试验证失败**

```bash
poetry run pytest tests/infrastructure/repositories/test_product_package_repository.py -v
```

**预期失败:** `ModuleNotFoundError: No module named 'app.infrastructure.repositories'`

**Step 3: 写最小实现**

创建 `backend/app/infrastructure/repositories/product_package_repository.py`:

```python
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.infrastructure.database.models import ProductPackageModel

class ProductPackageRepository:
    """产品包仓储 - 数据访问层"""

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: Dict[str, Any]) -> ProductPackageModel:
        """创建新产品包"""
        package = ProductPackageModel(**data)
        self.session.add(package)
        self.session.commit()
        self.session.refresh(package)
        return package

    def get_by_workflow_id(self, workflow_id: str) -> Optional[ProductPackageModel]:
        """通过 workflow_id 查询"""
        return self.session.query(ProductPackageModel)\
            .filter(ProductPackageModel.workflow_id == workflow_id)\
            .first()

    def get_by_id(self, package_id: str) -> Optional[ProductPackageModel]:
        """通过 ID 查询"""
        return self.session.query(ProductPackageModel)\
            .filter(ProductPackageModel.id == package_id)\
            .first()

    def update_status(
        self,
        package_id: str,
        status: str,
        stage: str = None,
        progress: Dict[str, Any] = None
    ) -> ProductPackageModel:
        """更新状态"""
        package = self.get_by_id(package_id)
        package.status = status
        if stage:
            package.stage = stage
        if progress:
            package.progress = progress
        self.session.commit()
        self.session.refresh(package)
        return package

    def add_artifact(self, package_id: str, artifact_type: str, artifact_id: str):
        """添加工件引用"""
        package = self.get_by_id(package_id)
        if not package.artifacts:
            package.artifacts = {}
        if artifact_type not in package.artifacts:
            package.artifacts[artifact_type] = []
        package.artifacts[artifact_type].append(artifact_id)
        self.session.commit()
```

**Step 4: 运行测试验证通过**

```bash
poetry run pytest tests/infrastructure/repositories/test_product_package_repository.py -v
```

**预期:** 所有测试通过 ✅

**Step 5: 提交**

```bash
git add app/infrastructure/repositories/ tests/infrastructure/repositories/
git commit -m "feat(repository): add ProductPackageRepository with CRUD operations"
```

---

## Phase 2: 编排层 - DeepOrchestrator 核心 (M1 关键)

### Task 2.1: 创建原子工具注册表

**目标:** 定义 text/image/video/storage 原子工具

**Files:**
- Create: `backend/app/application/tools/__init__.py`
- Create: `backend/app/application/tools/text_tools.py`
- Create: `backend/app/application/tools/image_tools.py`
- Create: `backend/app/application/tools/video_tools.py`
- Create: `backend/app/application/tools/storage_tools.py`
- Create: `backend/tests/application/tools/test_text_tools.py`

**Step 1: 写失败的测试 (text_tools 示例)**

创建 `backend/tests/application/tools/test_text_tools.py`:

```python
import pytest
from app.application.tools.text_tools import generate_text, extract_keywords

@pytest.mark.asyncio
async def test_generate_text_basic():
    """测试:基础文本生成"""
    result = await generate_text({
        "prompt": "写一句关于手机的广告语",
        "max_length": 50
    })

    assert "text" in result
    assert len(result["text"]) > 0
    assert len(result["text"]) <= 50

@pytest.mark.asyncio
async def test_extract_keywords():
    """测试:从文本提取关键词"""
    result = await extract_keywords({
        "text": "这款智能手机拥有强大的处理器和超长续航能力",
        "max_keywords": 3
    })

    assert "keywords" in result
    assert isinstance(result["keywords"], list)
    assert len(result["keywords"]) <= 3
```

**Step 2: 运行测试验证失败**

```bash
poetry run pytest tests/application/tools/test_text_tools.py -v
```

**预期失败:** `ModuleNotFoundError`

**Step 3: 写最小实现**

创建 `backend/app/application/tools/text_tools.py`:

```python
from typing import Dict, Any
from app.infrastructure.generators.deepseek import DeepSeekGenerator

async def generate_text(params: Dict[str Any]) -> Dict[str, str]:
    """生成文本 (文案/描述等)"""
    prompt = params.get("prompt")
    max_length = params.get("max_length", 200)

    # 复用现有 DeepSeekGenerator
    generator = DeepSeekGenerator()
    result = await generator.generate(prompt)

    # 截断到指定长度
    if len(result) > max_length:
        result = result[:max_length]

    return {"text": result}

async def extract_keywords(params: Dict[str, Any]) -> Dict[str, Any]:
    """从文本提取关键词"""
    text = params.get("text", "")
    max_keywords = params.get("max_keywords", 5)

    # 简单实现:基于词频 (后续可用 NLP 库优化)
    words = text.split()
    word_freq = {}
    for word in words:
        if len(word) > 2:  # 过滤单字
            word_freq[word] = word_freq.get(word, 0) + 1

    # 取前 N 个高频词
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    keywords = [w[0] for w in sorted_words[:max_keywords]]

    return {"keywords": keywords}
```

**Step 4-5: 运行测试并提交**

(同上流程)

---

### Task 2.2: 创建 DeepOrchestrator 主 Agent

**目标:** 实现多 Agent 编排逻辑

**Files:**
- Create: `backend/app/application/orchestration/deep_orchestrator.py`
- Create: `backend/tests/application/orchestration/test_deep_orchestrator.py`

**Step 1: 写失败的测试**

```python
# backend/tests/application/orchestration/test_deep_orchestrator.py
import pytest
from app.application.orchestration.deep_orchestrator import DeepOrchestrator

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    """测试:编排器初始化"""
    orchestrator = DeepOrchestrator()
    assert orchestrator is not None
    assert orchestrator.state == "idle"

@pytest.mark.asyncio
async def test_start_workflow():
    """测试:启动工作流"""
    orchestrator = DeepOrchestrator()

    workflow_id = await orchestrator.start({
        "image_url": "http://example.com/product.jpg",
        "background": "高端智能手机"
    })

    assert workflow_id is not None
    assert orchestrator.state == "running"

@pytest.mark.asyncio
async def test_workflow_progress():
    """测试:获取工作流进度"""
    orchestrator = DeepOrchestrator()

    workflow_id = await orchestrator.start({"image_url": "test.jpg", "background": "test"})

    progress = await orchestrator.get_progress(workflow_id)
    assert progress["status"] == "running"
    assert progress["percentage"] >= 0
```

**Step 3: 写最小实现**

创建 `backend/app/application/orchestration/deep_orchestrator.py`:

```python
from typing import Dict, Any, Optional
import uuid
from app.infrastructure.repositories.product_package_repository import ProductPackageRepository
from app.application.tools.text_tools import generate_text, extract_keywords

class DeepOrchestrator:
    """多 Agent 编排器 - 主 Agent"""

    def __init__(self):
        self.state = "idle"
        self.active_workflows: Dict[str, Dict[str, Any]] = {}

    async def start(self, input_data: Dict[str, Any]) -> str:
        """启动新工作流"""
        workflow_id = f"workflow-{uuid.uuid4().hex[:8]}"

        # 初始化工作流状态
        self.active_workflows[workflow_id] = {
            "status": "running",
            "stage": "analysis",
            "progress": {"percentage": 0, "current_step": "init"},
            "input_data": input_data
        }

        self.state = "running"
        return workflow_id

    async def get_progress(self, workflow_id: str) -> Dict[str, Any]:
        """获取工作流进度"""
        if workflow_id not in self.active_workflows:
            return {"status": "not_found"}

        return self.active_workflows[workflow_id]

    async def run_analysis_stage(self, workflow_id: str):
        """执行产品分析阶段"""
        workflow = self.active_workflows[workflow_id]
        workflow["stage"] = "analysis"
        workflow["progress"]["current_step"] = "analyzing_product"
        workflow["progress"]["percentage"] = 10

        # TODO: 调用 ProductAnalysisSubagent
        # 临时:模拟分析完成
        workflow["stage"] = "copywriting"
        workflow["progress"]["percentage"] = 25
```

(后续任务按相同模式...)

---

## Phase 3: API 路由层 (M1 可闭环体验)

### Task 3.1: 创建产品包生成 API

**Files:**
- Create: `backend/app/interface/routes/product_packages.py`
- Create: `backend/tests/interface/routes/test_product_packages_api.py`

**Step 1: 写失败的测试**

```python
# backend/tests/interface/routes/test_product_packages_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_generate_package():
    """测试:POST /api/v1/product-packages/generate"""
    response = client.post("/api/v1/product-packages/generate", json={
        "image_url": "http://example.com/product.jpg",
        "background": "高端智能手机",
        "options": {
            "copywriting_versions": 1,
            "image_count": 3,
            "enable_video": True
        }
    })

    assert response.status_code == 202
    data = response.json()
    assert "workflow_id" in data
    assert data["status"] == "running"

def test_get_status():
    """测试:GET /api/v1/product-packages/status/{workflow_id}"""
    # 先创建
    create_resp = client.post("/api/v1/product-packages/generate", json={
        "image_url": "test.jpg",
        "background": "test"
    })
    workflow_id = create_resp.json()["workflow_id"]

    # 查询状态
    response = client.get(f"/api/v1/product-packages/status/{workflow_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["workflow_id"] == workflow_id
```

**Step 3: 写最小实现**

创建 `backend/app/interface/routes/product_packages.py`:

```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any
from app.application.orchestration.deep_orchestrator import DeepOrchestrator

router = APIRouter(prefix="/api/v1/product-packages", tags=["product-packages"])

# 全局编排器实例 (临时,后续用依赖注入)
orchestrator = DeepOrchestrator()

class ProductPackageRequest(BaseModel):
    image_url: str
    background: str
    options: Optional[Dict[str, Any]] = {}

class ProductPackageStatusResponse(BaseModel):
    workflow_id: str
    status: str
    stage: str
    progress: Dict[str, Any]

@router.post("/generate", status_code=status.HTTP_202_ACCEPTED)
async def generate_package(request: ProductPackageRequest):
    """启动产品包生成工作流"""
    workflow_id = await orchestrator.start({
        "image_url": request.image_url,
        "background": request.background,
        "options": request.options
    })

    return {
        "workflow_id": workflow_id,
        "status": "running",
        "message": "Product package generation started"
    }

@router.get("/status/{workflow_id}")
async def get_status(workflow_id: str) -> ProductPackageStatusResponse:
    """获取工作流状态"""
    progress = await orchestrator.get_progress(workflow_id)

    if progress["status"] == "not_found":
        raise HTTPException(status_code=404, detail="Workflow not found")

    return ProductPackageStatusResponse(
        workflow_id=workflow_id,
        status=progress["status"],
        stage=progress.get("stage", "unknown"),
        progress=progress.get("progress", {})
    )
```

注册路由到 `backend/app/main.py`:

```python
from app.interface.routes.product_packages import router as product_packages_router

app.include_router(product_packages_router)
```

---

## Phase 4: WebSocket 事件扩展 (M1 实时反馈)

### Task 4.1: 扩展 socket_manager 支持新事件类型

**Files:**
- Modify: `backend/app/interface/ws/socket_manager.py`
- Create: `backend/tests/interface/ws/test_socket_manager_events.py`

**Step 1: 写失败的测试**

```python
# backend/tests/interface/ws/test_socket_manager_events.py
import pytest
from app.interface.ws.socket_manager import manager

@pytest.mark.asyncio
async def test_send_progress_event():
    """测试:发送进度事件"""
    await manager.broadcast_progress("workflow-123", {
        "percentage": 50,
        "stage": "copywriting",
        "current_step": "generating_version_2"
    })

    # 验证事件被发送 (需 mock websocket)
    # TODO: 添加断言

@pytest.mark.asyncio
async def test_send_artifact_event():
    """测试:发送工件完成事件"""
    await manager.broadcast_artifact("workflow-123", {
        "type": "copywriting",
        "artifact_id": "cp-001",
        "content": "..."
    })
```

**Step 3: 扩展实现**

在 `backend/app/interface/ws/socket_manager.py` 添加:

```python
async def broadcast_progress(self, workflow_id: str, progress_data: Dict[str, Any]):
    """广播进度更新事件"""
    message = {
        "type": "agent:progress",
        "workflow_id": workflow_id,
        "data": progress_data
    }
    await self.broadcast(json.dumps(message))

async def broadcast_artifact(self, workflow_id: str, artifact_data: Dict[str, Any]):
    """广播工件生成完成事件"""
    message = {
        "type": "agent:artifact",
        "workflow_id": workflow_id,
        "data": artifact_data
    }
    await self.broadcast(json.dumps(message))

async def broadcast_approval_required(self, workflow_id: str, approval_data: Dict[str, Any]):
    """广播需要人工审批事件"""
    message = {
        "type": "agent:approval_required",
        "workflow_id": workflow_id,
        "data": approval_data
    }
    await self.broadcast(json.dumps(message))
```

---

## Phase 5: 前端集成 (M1 完整体验)

### Task 5.1: 创建产品包服务

**Files:**
- Create: `frontend/src/services/productPackageService.ts`
- Create: `frontend/src/services/__tests__/productPackageService.test.ts`

**Step 1: 写失败的测试**

```typescript
// frontend/src/services/__tests__/productPackageService.test.ts
import { generatePackage, getPackageStatus } from '../productPackageService';

describe('ProductPackageService', () => {
  test('generatePackage should return workflow_id', async () => {
    const result = await generatePackage({
      image_url: 'http://example.com/product.jpg',
      background: 'test',
      options: {}
    });

    expect(result.workflow_id).toBeDefined();
    expect(result.status).toBe('running');
  });

  test('getPackageStatus should fetch status', async () => {
    const status = await getPackageStatus('workflow-123');
    expect(status.workflow_id).toBe('workflow-123');
    expect(status.stage).toBeDefined();
  });
});
```

**Step 3: 写最小实现**

```typescript
// frontend/src/services/productPackageService.ts
const API_BASE = '/api/v1/product-packages';

export interface ProductPackageRequest {
  image_url: string;
  background: string;
  options?: Record<string, any>;
}

export async function generatePackage(request: ProductPackageRequest) {
  const response = await fetch(`${API_BASE}/generate`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(request)
  });

  if (!response.ok) {
    throw new Error('Failed to generate package');
  }

  return response.json();
}

export async function getPackageStatus(workflowId: string) {
  const response = await fetch(`${API_BASE}/status/${workflowId}`);
  if (!response.ok) {
    throw new Error('Failed to get status');
  }
  return response.json();
}
```

---

## Phase 6: E2E 测试与集成验证 (M1 完整闭环)

### Task 6.1: 端到端工作流测试

**Files:**
- Create: `backend/tests/e2e/test_full_workflow.py`

**Step 1: 写失败的测试**

```python
# backend/tests/e2e/test_full_workflow.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_full_workflow_e2e():
    """测试:完整的端到端工作流"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. 启动工作流
        response = await client.post("/api/v1/product-packages/generate", json={
            "image_url": "http://example.com/product.jpg",
            "background": "高端智能手机"
        })
        assert response.status_code == 202
        workflow_id = response.json()["workflow_id"]

        # 2. 轮询状态直到完成 (或超时)
        import time
        max_wait = 60  # 秒
        start = time.time()

        while time.time() - start < max_wait:
            status_resp = await client.get(f"/api/v1/product-packages/status/{workflow_id}")
            status_data = status_resp.json()

            if status_data["status"] in ["completed", "failed"]:
                break

            time.sleep(2)

        # 3. 验证最终状态
        final_status = await client.get(f"/api/v1/product-packages/status/{workflow_id}")
        final_data = final_status.json()

        assert final_data["status"] in ["completed", "approval_required"]
        assert "artifacts" in final_data or "error" in final_data
```

---

## 执行说明

### 前置条件
1. 安装依赖: `poetry install` (backend) / `npm install` (frontend)
2. 数据库迁移: 创建 `product_packages` 表
3. DeepSeek API key 已配置

### 执行顺序
1. **Phase 1** (基础设施) → 必须首先完成
2. **Phase 2** (编排层) → 依赖 Phase 1
3. **Phase 3** (API 路由) → 依赖 Phase 2
4. **Phase 4** (WebSocket) → 可与 Phase 3 并行
5. **Phase 5** (前端) → 依赖 Phase 3
6. **Phase 6** (E2E) → 最后验证

### 验证检查点
- ✅ 所有单元测试通过
- ✅ 集成测试通过
- ✅ E2E 测试通过
- ✅ 前端可以触发完整工作流
- ✅ WebSocket 实时事件正常显示

### M1 交付标准
- 用户可上传图片 + 输入背景文案
- 系统执行: 分析 → 文案 → 3张图 → 视频(fallback)
- 前端实时显示进度
- 最终生成完整产品包

---

**下一步:** 使用 `superpowers:executing-plans` 或 `superpowers:subagent-driven-development` 执行此计划。

**参考文档:**
- DeepAgents: https://docs.langchain.com/oss/python/deepagents/overview
- LangGraph: https://docs.langchain.com/oss/python/langgraph/durable-execution
- 原始需求: `Agent-plan2.md`
