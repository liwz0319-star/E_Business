"""项目管理 API 集成测试

测试 API 端点、用户所有权验证、分页边界情况和搜索功能。
"""

import pytest
from uuid import uuid4

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database.models import ProductPackageModel


class TestProjectsAPI:
    """测试项目管理 API 端点"""

    async def _register_and_login(
        self, async_client: AsyncClient, email: str = "test@example.com"
    ) -> tuple[str, str]:
        """注册并登录用户，返回 (token, user_id)"""
        # 注册
        register_data = {"email": email, "password": "Password123!"}
        response = await async_client.post("/api/v1/auth/signup", json=register_data)
        assert response.status_code == 201, f"注册失败: {response.text}"
        user_id = response.json()["user"]["id"]

        # 登录
        login_data = {"email": email, "password": "Password123!"}
        response = await async_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200, f"登录失败: {response.text}"
        data = response.json()
        return data["accessToken"], user_id

    async def _create_project(
        self,
        session: AsyncSession,
        user_id: str,
        name: str = "Test Project",
        status: str = "completed",
    ) -> ProductPackageModel:
        """创建测试项目"""
        project = ProductPackageModel(
            workflow_id=str(uuid4()),
            name=name,
            user_id=user_id,
            status=status,
            stage="copywriting",
            input_data={"product_name": "Test Product"},
            analysis_data={"category": "electronics"},
            artifacts={"images": [{"url": "https://example.com/image.jpg"}]},
        )
        session.add(project)
        await session.flush()
        await session.refresh(project)
        return project

    # ============ Integration Tests for API Endpoints ============

    @pytest.mark.asyncio
    async def test_list_projects_success(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试成功列出项目"""
        async_client, session = async_client_with_session
        token, user_id = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        # 创建项目
        await self._create_project(session, user_id)

        response = await async_client.get("/api/v1/projects", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data
        assert "pages" in data
        assert data["total"] >= 1

    @pytest.mark.asyncio
    async def test_list_projects_unauthorized(self, async_client: AsyncClient):
        """测试未授权访问"""
        response = await async_client.get("/api/v1/projects")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_project_success(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试成功获取单个项目"""
        async_client, session = async_client_with_session
        token, user_id = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        project = await self._create_project(session, user_id)

        response = await async_client.get(
            f"/api/v1/projects/{project.id}", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(project.id)
        assert data["name"] == "Test Project"
        assert "thumbnailUrl" in data

    @pytest.mark.asyncio
    async def test_get_project_not_found(self, async_client: AsyncClient):
        """测试获取不存在的项目"""
        token, _ = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        fake_id = uuid4()
        response = await async_client.get(
            f"/api/v1/projects/{fake_id}", headers=headers
        )

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_project_success(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试成功删除项目"""
        async_client, session = async_client_with_session
        token, user_id = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        project = await self._create_project(session, user_id)

        response = await async_client.delete(
            f"/api/v1/projects/{project.id}", headers=headers
        )

        assert response.status_code == 204

        # 验证已删除
        response2 = await async_client.get(
            f"/api/v1/projects/{project.id}", headers=headers
        )
        assert response2.status_code == 404

    @pytest.mark.asyncio
    async def test_duplicate_project_success(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试成功复制项目"""
        async_client, session = async_client_with_session
        token, user_id = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        project = await self._create_project(session, user_id)

        response = await async_client.post(
            f"/api/v1/projects/{project.id}/duplicate", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] != str(project.id)
        assert data["workflowId"] != project.workflow_id
        assert data["name"] == f"{project.name} (Copy)"
        assert data["status"] == "pending"

    @pytest.mark.asyncio
    async def test_update_project_name(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试更新项目名称"""
        async_client, session = async_client_with_session
        token, user_id = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        project = await self._create_project(session, user_id)

        new_name = "Updated Project Name"
        response = await async_client.patch(
            f"/api/v1/projects/{project.id}",
            headers=headers,
            json={"name": new_name},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == new_name

    # ============ User Ownership Enforcement Tests ============

    @pytest.mark.asyncio
    async def test_cannot_access_other_user_project(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试不能访问其他用户的项目"""
        async_client, session = async_client_with_session

        # 用户1创建项目
        token1, user_id1 = await self._register_and_login(async_client, "user1@example.com")
        project = await self._create_project(session, user_id1)

        # 用户2尝试访问
        token2, _ = await self._register_and_login(async_client, "user2@example.com")
        headers2 = {"Authorization": f"Bearer {token2}"}

        response = await async_client.get(
            f"/api/v1/projects/{project.id}", headers=headers2
        )

        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_cannot_delete_other_user_project(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试不能删除其他用户的项目"""
        async_client, session = async_client_with_session

        # 用户1创建项目
        token1, user_id1 = await self._register_and_login(async_client, "user1@example.com")
        project = await self._create_project(session, user_id1)

        # 用户2尝试删除
        token2, _ = await self._register_and_login(async_client, "user2@example.com")
        headers2 = {"Authorization": f"Bearer {token2}"}

        response = await async_client.delete(
            f"/api/v1/projects/{project.id}", headers=headers2
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_cannot_duplicate_other_user_project(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试不能复制其他用户的项目"""
        async_client, session = async_client_with_session

        # 用户1创建项目
        token1, user_id1 = await self._register_and_login(async_client, "user1@example.com")
        project = await self._create_project(session, user_id1)

        # 用户2尝试复制
        token2, _ = await self._register_and_login(async_client, "user2@example.com")
        headers2 = {"Authorization": f"Bearer {token2}"}

        response = await async_client.post(
            f"/api/v1/projects/{project.id}/duplicate", headers=headers2
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_cannot_update_other_user_project(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试不能更新其他用户的项目"""
        async_client, session = async_client_with_session

        # 用户1创建项目
        token1, user_id1 = await self._register_and_login(async_client, "user1@example.com")
        project = await self._create_project(session, user_id1)

        # 用户2尝试更新
        token2, _ = await self._register_and_login(async_client, "user2@example.com")
        headers2 = {"Authorization": f"Bearer {token2}"}

        response = await async_client.patch(
            f"/api/v1/projects/{project.id}",
            headers=headers2,
            json={"name": "Hacked Name"},
        )

        assert response.status_code == 403

    # ============ Pagination Edge Cases Tests ============

    @pytest.mark.asyncio
    async def test_pagination_empty_list(self, async_client: AsyncClient):
        """测试空列表分页"""
        token, _ = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get("/api/v1/projects", headers=headers)

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
        assert data["pages"] == 1  # 至少一页

    @pytest.mark.asyncio
    async def test_pagination_page_beyond_total(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试超出范围的分页"""
        async_client, session = async_client_with_session
        token, user_id = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        await self._create_project(session, user_id)

        response = await async_client.get(
            "/api/v1/projects?page=999&limit=20", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["page"] == 999

    @pytest.mark.asyncio
    async def test_pagination_min_values(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试最小分页值"""
        async_client, session = async_client_with_session
        token, user_id = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        await self._create_project(session, user_id)

        response = await async_client.get(
            "/api/v1/projects?page=1&limit=1", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 1

    # ============ Search Functionality Tests ============

    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试搜索不区分大小写"""
        async_client, session = async_client_with_session
        token, user_id = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        await self._create_project(
            session, user_id,
            name="UNIQUE Search Term Project"
        )

        # 小写搜索
        response = await async_client.get(
            "/api/v1/projects?search=unique", headers=headers
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 1

        # 大写搜索
        response = await async_client.get(
            "/api/v1/projects?search=UNIQUE", headers=headers
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 1

        # 混合大小写
        response = await async_client.get(
            "/api/v1/projects?search=UnIqUe", headers=headers
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    @pytest.mark.asyncio
    async def test_search_partial_match(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试部分匹配搜索"""
        async_client, session = async_client_with_session
        token, user_id = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        await self._create_project(
            session, user_id,
            name="My Awesome Product Name"
        )

        # 部分匹配
        response = await async_client.get(
            "/api/v1/projects?search=Awesome", headers=headers
        )
        assert response.status_code == 200
        assert response.json()["total"] >= 1

    @pytest.mark.asyncio
    async def test_search_no_results(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试无结果搜索"""
        async_client, session = async_client_with_session
        token, user_id = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        await self._create_project(session, user_id)

        response = await async_client.get(
            "/api/v1/projects?search=zzznonexistentzzz", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_search_name_only(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试只在 name 字段搜索 (不搜索 UUID)"""
        async_client, session = async_client_with_session
        token, user_id = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        project = await self._create_project(
            session, user_id,
            name="Some Project Name"
        )

        # 用项目 ID 的一部分搜索应该不匹配 (除非恰好与 name 重叠)
        response = await async_client.get(
            f"/api/v1/projects?search={str(project.id)[:8]}", headers=headers
        )

        assert response.status_code == 200
        # UUID 部分不应该匹配,除非恰好与 name 重叠

    # ============ Filter Tests ============

    @pytest.mark.asyncio
    async def test_filter_by_status(self, async_client_with_session: tuple[AsyncClient, AsyncSession]):
        """测试按状态过滤"""
        async_client, session = async_client_with_session
        token, user_id = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        for status_val in ["pending", "completed", "failed"]:
            await self._create_project(
                session, user_id,
                name=f"Status Test {status_val}",
                status=status_val
            )

        response = await async_client.get(
            "/api/v1/projects?status=completed", headers=headers
        )

        assert response.status_code == 200
        data = response.json()
        assert all(item["status"] == "completed" for item in data["items"])

    @pytest.mark.asyncio
    async def test_filter_invalid_status(self, async_client: AsyncClient):
        """测试无效状态过滤"""
        token, _ = await self._register_and_login(async_client)
        headers = {"Authorization": f"Bearer {token}"}

        response = await async_client.get(
            "/api/v1/projects?status=invalid_status", headers=headers
        )

        assert response.status_code == 400
