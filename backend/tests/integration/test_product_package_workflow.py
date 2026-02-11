"""
Product Package Workflow Integration Tests

测试完整的产品包生成工作流
"""

import pytest
import asyncio
from uuid import uuid4
from httpx import AsyncClient

from app.main import app


@pytest.mark.asyncio
class TestProductPackageWorkflow:
    """测试产品包工作流"""

    async def test_full_workflow_with_mock_data(self, async_client: AsyncClient, auth_token: str):
        """
        测试完整工作流（使用 Mock 数据）

        这个测试会：
        1. 创建用户并获取 token
        2. 发起产品包生成请求
        3. 轮询状态直到完成
        4. 获取最终结果
        """
        # 步骤 1: 发起生成
        generate_request = {
            "image_url": "https://example.com/product.jpg",
            "background": "Premium wireless headphones with noise cancellation",
            "options": {
                "copy_variants": 2,
                "image_variants": 3,
                "video_duration_sec": 15,
                "require_approval": False,  # 跳过审批以简化测试
                "force_fallback_video": True,  # 强制使用 slideshow 加快测试
            }
        }

        response = await async_client.post(
            "/api/v1/product-packages/generate",
            json=generate_request,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 202
        data = response.json()
        workflow_id = data["workflow_id"]
        package_id = data["package_id"]

        print(f"\n✅ 工作流已启动: {workflow_id}")

        # 步骤 2: 轮询状态（最多等待 60 秒）
        max_attempts = 30
        interval = 2

        for attempt in range(max_attempts):
            await asyncio.sleep(interval)

            status_response = await async_client.get(
                f"/api/v1/product-packages/status/{workflow_id}",
                headers={"Authorization": f"Bearer {auth_token}"}
            )

            assert status_response.status_code == 200
            status_data = status_response.json()

            print(f"  进度: {status_data['progress_percentage']}% - {status_data['current_step']}")

            # 检查是否完成
            if status_data["status"] in ["completed", "failed"]:
                break

        # 步骤 3: 验证最终状态
        assert status_data["status"] == "completed", f"工作流失败: {status_data.get('error')}"
        print(f"✅ 工作流完成: {status_data['status']}")

        # 步骤 4: 获取详细结果
        detail_response = await async_client.get(
            f"/api/v1/product-packages/{package_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        if detail_response.status_code == 200:
            detail_data = detail_response.json()
            print(f"\n📦 产品包详情:")
            print(f"  状态: {detail_data['status']}")
            print(f"  阶段: {detail_data['stage']}")

            if detail_data.get("analysis"):
                print(f"  分析结果: {detail_data['analysis'].get('category', 'N/A')}")

            if detail_data.get("copywriting_versions"):
                print(f"  文案版本: {len(detail_data['copywriting_versions'])}")

            if detail_data.get("images"):
                print(f"  图片数量: {len(detail_data['images'])}")

            if detail_data.get("video"):
                print(f"  视频: {'✓' if detail_data['video'] else '✗'}")

    async def test_approval_workflow(self, async_client: AsyncClient, auth_token: str):
        """测试审批工作流"""
        # 创建需要审批的包
        generate_request = {
            "image_url": "https://example.com/product2.jpg",
            "background": "Test product for approval",
            "options": {
                "require_approval": True,
            }
        }

        response = await async_client.post(
            "/api/v1/product-packages/generate",
            json=generate_request,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert response.status_code == 202
        data = response.json()
        workflow_id = data["workflow_id"]
        package_id = data["package_id"]

        # 等待审批状态
        await asyncio.sleep(5)  # 简化等待

        # 获取状态
        status_response = await async_client.get(
            f"/api/v1/product-packages/status/{workflow_id}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        status_data = status_response.json()

        if status_data["status"] == "approval_required":
            # 审批通过
            approve_response = await async_client.post(
                f"/api/v1/product-packages/{package_id}/approve",
                json={"decision": "approve", "comment": "Looks good!"},
                headers={"Authorization": f"Bearer {auth_token}"}
            )

            assert approve_response.status_code == 200
            approve_data = approve_response.json()
            assert approve_data["decision"] == "approve"
            assert approve_data["status"] == "completed"

            print(f"✅ 审批工作流测试通过")

    async def test_regenerate_workflow(self, async_client: AsyncClient, auth_token: str):
        """测试重新生成工作流"""
        # 首先创建一个包
        generate_request = {
            "image_url": "https://example.com/product3.jpg",
            "background": "Test product for regeneration",
            "options": {"require_approval": False}
        }

        response = await async_client.post(
            "/api/v1/product-packages/generate",
            json=generate_request,
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        data = response.json()
        package_id = data["package_id"]

        # 等待完成
        await asyncio.sleep(5)

        # 重新生成图片
        regenerate_response = await async_client.post(
            f"/api/v1/product-packages/{package_id}/regenerate",
            json={
                "target": "images",
                "reason": "Want different style"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )

        assert regenerate_response.status_code == 202
        regen_data = regenerate_response.json()
        assert regen_data["target"] == "images"

        print(f"✅ 重新生成工作流测试通过")


@pytest.fixture
async def auth_token(async_client: AsyncClient) -> str:
    """创建测试用户并获取 token"""
    # 注册用户
    register_data = {
        "email": f"test-{uuid4()}@example.com",
        "password": "testpass123",
    }

    await async_client.post("/api/v1/auth/register", json=register_data)

    # 登录获取 token
    login_data = {
        "username": register_data["email"],
        "password": register_data["password"],
    }

    response = await async_client.post(
        "/api/v1/auth/login",
        data=login_data
    )

    assert response.status_code == 200
    token_data = response.json()
    return token_data["access_token"]
