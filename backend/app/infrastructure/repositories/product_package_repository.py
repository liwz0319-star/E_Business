# backend/app/infrastructure/repositories/product_package_repository.py
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
    ) -> Optional[ProductPackageModel]:
        """更新状态"""
        package = self.get_by_id(package_id)

        if package is None:
            return None

        package.status = status
        if stage:
            package.stage = stage
        if progress:
            package.progress = progress

        try:
            self.session.commit()
            self.session.refresh(package)
            return package
        except Exception as e:
            self.session.rollback()
            raise

    def add_artifact(
        self,
        package_id: str,
        artifact_type: str,
        artifact_id: str
    ) -> Optional[ProductPackageModel]:
        """添加工件引用"""
        package = self.get_by_id(package_id)

        if package is None:
            return None

        # 创建新的 artifacts 字典
        new_artifacts = dict(package.artifacts or {})
        if artifact_type not in new_artifacts:
            new_artifacts[artifact_type] = []
        new_artifacts[artifact_type] = list(new_artifacts[artifact_type])
        new_artifacts[artifact_type].append(artifact_id)

        package.artifacts = new_artifacts

        try:
            self.session.commit()
            self.session.refresh(package)
            return package
        except Exception as e:
            self.session.rollback()
            raise
