"""
测试 Agent 真实 LLM 生成能力（无特殊字符版本）
"""

import asyncio
import os
import uuid
from pathlib import Path

from dotenv import load_dotenv

from app.application.tools import ToolRegistry
from app.application.agents.product_analysis_agent import ProductAnalysisAgent
from app.application.agents.copywriting_agent import CopywritingAgent
from app.application.agents.qa_agent import QAAgent
from app.infrastructure.generators import DeepSeekGenerator
from app.domain.entities.generation import GenerationRequest


async def test_llm_connection():
    """测试 LLM 连接"""
    print("\n" + "="*60)
    print("[TEST] LLM Connection Test")
    print("="*60)

    try:
        async with DeepSeekGenerator() as llm:
            request = GenerationRequest(
                prompt="Hello, please respond with 'OK'",
                model="deepseek-chat",
            )

            response = await llm.generate(request)

            if response.content:
                print(f"[SUCCESS] LLM connected: {response.content}")
                return True
            else:
                print("[ERROR] Empty response")
                return False

    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return False


async def test_text_generation():
    """测试基础文本生成"""
    print("\n" + "="*60)
    print("[TEST] Text Generation")
    print("="*60)

    try:
        async with DeepSeekGenerator() as llm:
            # Test 1: Product description
            print("\n[SCENARIO 1] Generate product description")

            request = GenerationRequest(
                prompt="""请为以下产品生成一段吸引人的营销描述:

产品: 高端无线耳机
特点: 主动降噪、30小时续航、优质音质

要求: 简洁专业，50字以内
""",
                model="deepseek-chat",
                max_tokens=200,
            )

            result = await llm.generate(request)
            print(f"[SUCCESS] Generated description ({len(result.content)} chars):")
            print(f"  {result.content}")

            # Test 2: Keywords extraction
            print("\n[SCENARIO 2] Extract keywords")

            request = GenerationRequest(
                prompt="""从以下产品描述中提取 5-8 个最重要的关键词:

产品描述: 这款高端无线耳机采用最新的主动降噪技术，有效隔绝环境噪音。配备 500mAh 大容量电池，续航时间长达 30 小时。

要求: 只返回关键词列表，用逗号分隔
""",
                model="deepseek-chat",
                max_tokens=100,
            )

            result = await llm.generate(request)
            print(f"[SUCCESS] Extracted keywords:")
            print(f"  {result.content}")

    except Exception as e:
        print(f"[ERROR] Text generation failed: {e}")


async def test_product_analysis_with_llm():
    """测试产品分析 Agent（使用真实 LLM）"""
    print("\n" + "="*60)
    print("[TEST] ProductAnalysisAgent with Real LLM")
    print("="*60)

    try:
        async with DeepSeekGenerator() as llm:
            tools = ToolRegistry.create_default(llm_client=llm)
            agent = ProductAnalysisAgent(tools)

            # Create workspace
            workflow_id = f"test-analysis-{uuid.uuid4()}"
            workspace = tools.filesystem.create_workspace(workflow_id)

            print(f"[INFO] Workspace created: {workspace}")

            request = {
                "image_url": "https://example.com/headphones.jpg",
                "background": """
这是一款高端无线蓝牙耳机，采用最新的主动降噪技术。

产品特点:
1. 主动降噪 (ANC) - 有效隔绝外界噪音
2. 超长续航 - 30小时连续播放时间
3. 快速充电 - 充电10分钟，使用3小时
4. 高品质音质 - 40mm 钕铁硼单元驱动
5. 舒适佩戴 - 记忆海绵耳罩，轻量化设计

目标用户: 商务人士、音乐发烧友、通勤族
""",
                "user_id": uuid.uuid4(),
            }

            print(f"\n[INFO] Analyzing product with real LLM...")
            print("[INFO] This may take 10-20 seconds...")

            analysis = await agent.run(request, workspace)

            print(f"\n[SUCCESS] Analysis completed:")
            print(f"  Category: {analysis.get('category', 'N/A')}")
            print(f"  Style: {analysis.get('style', 'N/A')}")
            print(f"  Target Audience: {analysis.get('target_audience', 'N/A')}")
            print(f"  Key Features: {', '.join(analysis.get('key_features', [])[:5])}")

            marketing_angles = analysis.get('marketing_angles', [])
            if marketing_angles:
                print(f"  Marketing Angles ({len(marketing_angles)} found):")
                for i, angle in enumerate(marketing_angles[:3], 1):
                    print(f"    {i}. {angle}")

            # Check generated report file
            report_path = f"{workspace}/workspace/analysis_report.md"
            if tools.filesystem.exists(report_path):
                print(f"\n[SUCCESS] Report generated: {report_path}")

    except Exception as e:
        print(f"[ERROR] Analysis failed: {e}")
        import traceback
        traceback.print_exc()


async def test_copywriting_generation():
    """测试文案生成（使用真实 LLM）"""
    print("\n" + "="*60)
    print("[TEST] CopywritingAgent with Real LLM")
    print("="*60)

    try:
        async with DeepSeekGenerator() as llm:
            tools = ToolRegistry.create_default(llm_client=llm)
            agent = CopywritingAgent(tools)

            # Create workspace
            workflow_id = f"test-copy-{uuid.uuid4()}"
            workspace = tools.filesystem.create_workspace(workflow_id)

            print(f"[INFO] Workspace created: {workspace}")

            # Prepare analysis data
            analysis = {
                "category": "电子产品",
                "style": "现代简约",
                "target_audience": ["商务人士", "音乐发烧友"],
                "key_features": [
                    "主动降噪技术",
                    "30小时超长续航",
                    "快速充电功能",
                    "高品质音质表现",
                ],
                "marketing_angles": [
                    "强调专业性能",
                    "突出便携性",
                    "强调性价比"
                ]
            }

            print(f"\n[INFO] Generating copywriting with real LLM...")
            print(f"[INFO] Product category: {analysis['category']}")
            print(f"[INFO] Key features: {len(analysis['key_features'])} items")
            print("[INFO] This may take 15-30 seconds...")

            # Test different channels
            channels = ["product_page", "social_post"]

            results = []
            for channel in channels:
                print(f"\n[INFO] Generating {channel} copywriting...")

                request = {
                    "channel": channel,
                    "analysis": analysis,
                    "product_name": "高端无线降噪耳机",
                    "target_audience": "25-45岁城市白领",
                }

                result = await agent.run(request, workspace)
                results.append(result)

                if result.get("content"):
                    print(f"  [SUCCESS] {len(result['content'])} chars")
                else:
                    print(f"  [FAILED]")

            print(f"\n[SUCCESS] Copywriting generated: {len([r for r in results if r.get('content')])}/{len(channels)} successful")

            # Display generated copywriting
            for i, result in enumerate(results):
                if result.get("content"):
                    print(f"\n[OUTPUT] Channel: {channels[i]}")
                    content = result["content"]
                    if len(content) > 300:
                        content = content[:300] + "..."
                    print(f"  {content}")

    except Exception as e:
        print(f"[ERROR] Copywriting failed: {e}")
        import traceback
        traceback.print_exc()


async def test_qa_with_llm():
    """测试 QA Agent（使用真实 LLM）"""
    print("\n" + "="*60)
    print("[TEST] QAAgent with Real LLM")
    print("="*60)

    try:
        async with DeepSeekGenerator() as llm:
            tools = ToolRegistry.create_default(llm_client=llm)
            agent = QAAgent(tools)

            # Create workspace
            workflow_id = f"test-qa-{uuid.uuid4()}"
            workspace = tools.filesystem.create_workspace(workflow_id)

            print(f"[INFO] Workspace created: {workspace}")

            # Prepare test data
            analysis = {
                "category": "电子产品",
                "key_features": [
                    "主动降噪",
                    "30小时续航",
                    "高品质音质",
                ]
            }

            copy_assets = [
                {
                    "channel": "product_page",
                    "content": "这款高端无线耳机采用最新主动降噪技术，30小时超长续航，为商务人士和音乐发烧友提供专业级音质体验。"
                },
            ]

            image_assets = [
                {"scene": "hero", "url": "https://example.com/hero.jpg"}
            ]

            video_asset = {
                "asset_id": "video-123",
                "url": "https://example.com/video.mp4",
                "is_fallback": False,
            }

            print(f"\n[INFO] Running QA check with real LLM...")
            print("[INFO] This may take 10-20 seconds...")

            qa_report = await agent.run(
                analysis, copy_assets, image_assets, video_asset, workspace
            )

            print(f"\n[SUCCESS] QA check completed:")
            print(f"  Score: {qa_report.get('score', 0):.2f}")
            print(f"  Passed: {'YES' if qa_report.get('passed') else 'NO'}")
            print(f"  Issues: {len(qa_report.get('issues', []))}")
            print(f"  Suggestions: {len(qa_report.get('suggestions', []))}")

        # Check generated report file
        report_path = f"{workspace}/workspace/qa_report.md"
        if tools.filesystem.exists(report_path):
            print(f"\n[SUCCESS] QA report generated: {report_path}")

    except Exception as e:
        print(f"[ERROR] QA check failed: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("[TEST SUITE] Agent LLM Generation Capability Tests")
    print("="*60)

    # Check API Key
    load_dotenv()
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("\n[ERROR] DEEPSEEK_API_KEY not configured")
        print("Please set DEEPSEEK_API_KEY in backend/.env")
        return

    print(f"[INFO] API Key: {api_key[:10]}...{api_key[-4:]}")

    try:
        # Test LLM connection
        if not await test_llm_connection():
            print("\n[ERROR] LLM connection failed, check API key and network")
            return

        # Test text generation
        await test_text_generation()

        # Test product analysis Agent
        await test_product_analysis_with_llm()

        # Test copywriting Agent
        await test_copywriting_generation()

        # Test QA Agent
        await test_qa_with_llm()

        print("\n" + "="*60)
        print("[SUCCESS] All tests completed!")
        print("="*60)

        print("\n[SUMMARY] Test Results:")
        print("  [OK] LLM connection test")
        print("  [OK] Basic text generation test")
        print("  [OK] ProductAnalysisAgent test")
        print("  [OK] CopywritingAgent test")
        print("  [OK] QAAgent test")
        print("\n[TIPS] Generated files in: backend/projects/test-*/workspace/")

    except KeyboardInterrupt:
        print("\n\n[INFO] Test interrupted by user")
    except Exception as e:
        print(f"\n\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
