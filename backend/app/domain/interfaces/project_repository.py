"""ProjectRepository 仓库接口

定义项目数据访问抽象。
遵循 Clean Architecture - 接口在 domain 层,实现在 infrastructure 层。
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
from uuid import UUID

from app.domain.entities.product_package import ProductPackage


class ProjectRepository(ABC):
    """
    项目仓库抽象接口

    定义数据访问方法,不依赖具体实现。
    """

    @abstractmethod
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
        """
        列出用户的项目

        Args:
            user_id: 用户 ID
            page: 页码(从 1 开始)
            limit: 每页条目数
            sort_by: 排序字段(created_at, name, updated_at)
            sort_order: 排序方向(asc, desc)
            status: 过滤状态(pending, running, completed, failed)
            search: 搜索关键词(在 name 中搜索)

        Returns:
            (项目列表, 总数)
        """
        pass

    @abstractmethod
    async def get_project_by_id(self, project_id: UUID) -> Optional[ProductPackage]:
        """
        通过 ID 获取项目

        Args:
            project_id: 项目 UUID

        Returns:
            ProductPackage 实体或 None
        """
        pass

    @abstractmethod
    async def delete_project(self, project_id: UUID) -> None:
        """
        删除项目(硬删除)

        Args:
            project_id: 要删除的项目 UUID

        Raises:
            HTTPException: 如果项目不存在或无权限
        """
        pass

    @abstractmethod
    async def duplicate_project(self, project_id: UUID) -> ProductPackage:
        """
        复制项目

        Args:
            project_id: 要复制的项目 UUID

        Returns:
            新创建的 ProductPackage 实体

        Raises:
            HTTPException: 如果项目不存在或无权限
        """
        pass

    @abstractmethod
    async def update_project(self, project_id: UUID, name: str) -> ProductPackage:
        """
        更新项目名称

        Args:
            project_id: 项目 UUID
            name: 新名称

        Returns:
            更新后的 ProductPackage 实体

        Raises:
            HTTPException: 如果项目不存在或无权限
        """
        pass
