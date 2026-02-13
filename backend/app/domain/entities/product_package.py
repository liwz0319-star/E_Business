"""ProductPackage 领域实体

纯 Python 类,代表产品包聚合根。
遵循 Clean Architecture - 不依赖 ORM 框架。
"""

from datetime import datetime
from typing import Optional
from uuid import UUID


class ProductPackage:
    """
    产品包聚合根 - 工作流执行主记录

    领域实体,不是 ORM 模型。用于应用层的业务逻辑。
    """

    def __init__(
        self,
        id: UUID,
        workflow_id: str,
        name: str,
        user_id: UUID,
        status: str,
        stage: str,
        input_data: Optional[dict] = None,
        analysis_data: Optional[dict] = None,
        artifacts: dict = None,
        created_at: datetime = None,
        updated_at: datetime = None,
        completed_at: Optional[datetime] = None,
    ):
        self.id = id
        self.workflow_id = workflow_id
        self.name = name
        self.user_id = user_id
        self.status = status
        self.stage = stage
        self.input_data = input_data
        self.analysis_data = analysis_data
        self.artifacts = artifacts if artifacts is not None else {}
        self.created_at = created_at
        self.updated_at = updated_at
        self.completed_at = completed_at

    def __repr__(self) -> str:
        return f"<ProductPackage(id={self.id}, workflow_id={self.workflow_id}, status={self.status})>"

    def to_dict(self) -> dict:
        """转换为字典用于序列化"""
        return {
            "id": str(self.id),
            "workflow_id": self.workflow_id,
            "name": self.name,
            "user_id": str(self.user_id),
            "status": self.status,
            "stage": self.stage,
            "input_data": self.input_data,
            "analysis_data": self.analysis_data,
            "artifacts": self.artifacts,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
