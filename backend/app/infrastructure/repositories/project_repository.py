"""SQLAlchemy 实现 ProjectRepository

数据访问层实现,将 ProductPackageModel 映射到 ProductPackage 实体。
"""

from typing import Optional, Tuple
from uuid import UUID, uuid4
from copy import deepcopy

from sqlalchemy import select, func, desc, asc, delete
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

from app.domain.entities.product_package import ProductPackage
from app.domain.interfaces.project_repository import ProjectRepository
from app.infrastructure.database.models import ProductPackageModel, VideoAssetModel


class SQLAlchemyProjectRepository(ProjectRepository):
    """SQLAlchemy 实现的项目仓库"""

    def __init__(self, session: AsyncSession):
        self.session = session

    def _to_entity(self, model: ProductPackageModel) -> ProductPackage:
        """将 ORM 模型转换为领域实体"""
        return ProductPackage(
            id=model.id,
            workflow_id=model.workflow_id,
            name=model.name,
            user_id=model.user_id,
            status=model.status,
            stage=model.stage,
            input_data=model.input_data,
            analysis_data=model.analysis_data,
            artifacts=model.artifacts,
            created_at=model.created_at,
            updated_at=model.updated_at,
            completed_at=model.completed_at,
        )

    async def list_projects(
        self,
        user_id: UUID,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        status: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Tuple[list[ProductPackage], int]:
        """列出用户的项目,支持分页、排序、过滤和搜索"""
        # 基础过滤条件 (用于 count 和查询)
        base_filter = [ProductPackageModel.user_id == user_id]

        if status:
            base_filter.append(ProductPackageModel.status == status)

        if search:
            search_pattern = f"%{search}%"
            base_filter.append(ProductPackageModel.name.ilike(search_pattern))

        # 优化: 先获取总数 (不带排序,避免不必要开销)
        total_query = select(func.count()).select_from(ProductPackageModel).where(*base_filter)
        total = await self.session.scalar(total_query) or 0

        # 构建数据查询 (带排序和分页)
        query = select(ProductPackageModel).where(*base_filter)

        order_col = getattr(ProductPackageModel, sort_by, ProductPackageModel.created_at)
        if sort_order == "desc":
            query = query.order_by(desc(order_col))
        else:
            query = query.order_by(asc(order_col))

        # 分页
        query = query.offset((page - 1) * limit).limit(limit)
        result = await self.session.execute(query)
        models = result.scalars().all()

        entities = [self._to_entity(m) for m in models]
        return entities, total

    async def get_project_by_id(self, project_id: UUID) -> Optional[ProductPackage]:
        """通过 ID 获取项目"""
        query = select(ProductPackageModel).where(
            ProductPackageModel.id == project_id
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if model is None:
            return None
        return self._to_entity(model)

    async def delete_project(self, project_id: UUID) -> None:
        """硬删除项目及关联资产

        AC2: 删除项目时级联删除通过 workflow_id 关联的所有资产
        """
        query = select(ProductPackageModel).where(
            ProductPackageModel.id == project_id
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if model is None:
            raise HTTPException(status_code=404, detail="Project not found")

        # AC2: 级联删除关联资产 (通过 workflow_id)
        workflow_id = model.workflow_id
        await self.session.execute(
            delete(VideoAssetModel).where(VideoAssetModel.workflow_id == workflow_id)
        )

        # 删除项目本身
        await self.session.delete(model)
        await self.session.flush()

    async def duplicate_project(self, project_id: UUID) -> ProductPackage:
        """深度复制项目"""
        query = select(ProductPackageModel).where(
            ProductPackageModel.id == project_id
        )
        result = await self.session.execute(query)
        source = result.scalar_one_or_none()

        if source is None:
            raise HTTPException(status_code=404, detail="Project not found")

        # 创建新项目
        new_model = ProductPackageModel(
            workflow_id=str(uuid4()),
            name=f"{source.name} (Copy)",
            user_id=source.user_id,
            status="pending",
            stage="analysis",
            input_data=deepcopy(source.input_data) if source.input_data else None,
            analysis_data=deepcopy(source.analysis_data) if source.analysis_data else None,
            artifacts={},
        )

        self.session.add(new_model)
        await self.session.flush()
        await self.session.refresh(new_model)

        return self._to_entity(new_model)

    async def update_project(self, project_id: UUID, name: str) -> ProductPackage:
        """更新项目名称"""
        query = select(ProductPackageModel).where(
            ProductPackageModel.id == project_id
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if model is None:
            raise HTTPException(status_code=404, detail="Project not found")

        model.name = name
        await self.session.flush()
        await self.session.refresh(model)

        return self._to_entity(model)
