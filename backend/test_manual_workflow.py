"""
手动测试产品包生成 Workflow

测试完整的 API 流程：注册 -> 登录 -> 生成 -> 轮询 -> 获取结果
"""

import asyncio
import httpx
from uuid import uuid4


async def test_workflow():
    """完整工作流测试"""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient() as client:
        print("=" * 60)
        print("🧪 产品包生成 Workflow 手动测试")
        print("=" * 60)

        # ========== 步骤 1: 用户注册 ==========
        print("\n📝 步骤 1: 用户注册")
        register_data = {
            "email": f"test-{uuid4()}@example.com",
            "password": "TestPass123",  # 必须包含大小写字母和数字
        }

        response = await client.post(f"{base_url}/api/v1/auth/signup", json=register_data)
        if response.status_code == 201:
            print(f"✅ 注册成功: {register_data['email']}")
        else:
            print(f"❌ 注册失败: {response.status_code}")
            print(f"   详情: {response.text}")
            return

        # ========== 步骤 2: 用户登录 ==========
        print("\n🔑 步骤 2: 用户登录")
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"],
        }

        response = await client.post(f"{base_url}/api/v1/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["accessToken"]
            print(f"✅ 登录成功")
            print(f"   Token: {access_token[:50]}...")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"   详情: {response.text}")
            return

        headers = {"Authorization": f"Bearer {access_token}"}

        # ========== 步骤 3: 发起产品包生成 ==========
        print("\n🚀 步骤 3: 发起产品包生成")
        generate_request = {
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800",
            "background": "Premium wireless headphones with noise cancellation and superior sound quality",
            "options": {
                "copy_variants": 2,  # 生成 2 个文案变体
                "image_variants": 3,  # 需要 Image provider，暂时跳过
                "video_duration_sec": 15,  # 需要 Video provider，暂时跳过
                "require_approval": False,  # 不需要审批
                "force_fallback_video": True,  # 使用 slideshow fallback
            }
        }

        # 注意：由于没有配置 Image/Video providers，会失败
        # 这是预期行为
        print("⚠️  注意: 此测试需要配置 Image/Video providers")
        print("⚠️  当前将测试到发起请求，预期会返回错误")

        response = await client.post(
            f"{base_url}/api/v1/product-packages/generate",
            json=generate_request,
            headers=headers
        )

        if response.status_code == 202:
            data = response.json()
            workflow_id = data["workflowId"]
            package_id = data["packageId"]
            print(f"✅ 工作流已启动")
            print(f"   Workflow ID: {workflow_id}")
            print(f"   Package ID: {package_id}")
        elif response.status_code == 500:
            print(f"⚠️  服务器错误（预期，因为未配置 providers）")
            print(f"   状态码: {response.status_code}")

            # 即使失败，我们继续测试其他端点
            print("\n" + "=" * 60)
            print("📊 测试其他可用的 API 端点")
            print("=" * 60)

            # ========== 测试健康检查 ==========
            print("\n🏥 测试健康检查")
            response = await client.get(f"{base_url}/health")
            if response.status_code == 200:
                print(f"✅ 健康检查通过: {response.json()}")

            # ========== 测试获取当前用户信息 ==========
            print("\n👤 测试获取当前用户信息")
            response = await client.get(f"{base_url}/api/v1/auth/me", headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                print(f"✅ 用户信息: {user_data}")

            # ========== 测试列出产品包 ==========
            print("\n📦 测试列出产品包")
            response = await client.get(f"{base_url}/api/v1/product-packages", headers=headers)
            if response.status_code == 200:
                packages = response.json()
                print(f"✅ 获取到 {len(packages)} 个产品包")
                for pkg in packages[:3]:  # 只显示前 3 个
                    print(f"   - {pkg['workflowId']}: {pkg['status']}")

            return
        else:
            print(f"❌ 发起失败: {response.status_code}")
            print(f"   详情: {response.text}")
            return

        # ========== 步骤 4: 轮询状态 ==========
        print("\n⏳ 步骤 4: 轮询工作流状态")
        max_attempts = 30
        interval = 2

        for attempt in range(max_attempts):
            await asyncio.sleep(interval)

            response = await client.get(
                f"{base_url}/api/v1/product-packages/status/{workflow_id}",
                headers=headers
            )

            if response.status_code == 200:
                status_data = response.json()
                progress = status_data.get("progressPercentage", 0)
                step = status_data.get("currentStep", "unknown")
                status_val = status_data.get("status", "unknown")

                print(f"  [{attempt+1}/{max_attempts}] 进度: {progress}% - {step} - 状态: {status_val}")

                if status_val in ["completed", "failed"]:
                    print(f"\n{'✅' if status_val == 'completed' else '❌'} 工作流结束: {status_val}")

                    if status_val == "failed":
                        error = status_data.get("errorMessage", "未知错误")
                        print(f"   错误: {error}")

                    break
            else:
                print(f"❌ 状态查询失败: {response.status_code}")
                break

        # ========== 步骤 5: 获取最终结果 ==========
        print("\n📄 步骤 5: 获取最终结果")
        response = await client.get(
            f"{base_url}/api/v1/product-packages/{package_id}",
            headers=headers
        )

        if response.status_code == 200:
            package_data = response.json()
            print(f"✅ 获取到产品包详情:")
            print(f"   状态: {package_data.get('status')}")
            print(f"   阶段: {package_data.get('stage')}")
            print(f"   进度: {package_data.get('progressPercentage')}%")

            artifacts = package_data.get("artifacts", {})
            if artifacts.get("copywriting"):
                print(f"   文案数量: {len(artifacts['copywriting'])}")
            if artifacts.get("images"):
                print(f"   图片数量: {len(artifacts['images'])}")
            if artifacts.get("video"):
                print(f"   视频: {artifacts['video']}")
        else:
            print(f"❌ 获取详情失败: {response.status_code}")

        print("\n" + "=" * 60)
        print("🎉 测试完成")
        print("=" * 60)


if __name__ == "__main__":
    print("\n确保后端服务正在运行：")
    print("  cd backend")
    print("  python -m uvicorn app.main:app --reload --host 0.0.0.0.0 --port 8000")
    print()

    asyncio.run(test_workflow())
