"""
手动测试 Agent 能力的脚本

这个脚本提供交互式界面来测试各个 Agent 的能力
"""

import asyncio
import uuid
from pathlib import Path

from app.application.tools import ToolRegistry
from app.application.agents.product_analysis_agent import ProductAnalysisAgent
from app.application.agents.qa_agent import QAAgent


async def test_filesystem_tools():
    """测试文件系统工具"""
    print("\n" + "="*60)
    print("🧪 测试 FileSystemTools")
    print("="*60)

    tools = ToolRegistry.create_default()
    fs = tools.filesystem

    # 创建工作区
    workflow_id = f"test-{uuid.uuid4()}"
    workspace = fs.create_workspace(workflow_id)

    print(f"✅ 工作区创建成功: {workspace}")

    # 写入测试文件
    test_data = {
        "product": "Test Product",
        "features": ["Feature 1", "Feature 2"],
    }

    fs.write_json(f"{workflow_id}/input/test.json", test_data)
    print(f"✅ 测试文件写入成功")

    # 读取测试文件
    read_data = fs.read_json(f"{workflow_id}/input/test.json")
    print(f"✅ 测试文件读取成功: {read_data}")

    # 列出文件
    files = fs.list_dir(f"{workflow_id}/input")
    print(f"✅ 文件列表: {files}")


async def test_vision_tools():
    """测试视觉工具（Mock 模式）"""
    print("\n" + "="*60)
    print("🧪 测试 VisionTools (Mock 模式)")
    print("="*60)

    tools = ToolRegistry.create_default()
    vision = tools.vision

    # 使用 Mock 数据分析图片
    image_path = "https://example.com/product.jpg"

    print(f"📸 分析图片: {image_path}")
    analysis = await vision.analyze_product_image(image_path)

    print(f"✅ 分析结果:")
    print(f"  - 类别: {analysis['category']}")
    print(f"  - 风格: {analysis['style']}")
    print(f"  - 目标受众: {analysis['target_audience']}")
    print(f"  - 关键特征: {', '.join(analysis['key_features'][:3])}")
    print(f"  - 建议场景: {', '.join(analysis['suggested_scenes'])}")


async def test_text_tools():
    """测试文本工具（Mock 模式）"""
    print("\n" + "="*60)
    print("🧪 测试 TextTools (Mock 模式)")
    print("="*60)

    tools = ToolRegistry.create_default()
    text = tools.text

    # 提取关键词
    sample_text = """
    Premium wireless headphones with active noise cancellation,
    30-hour battery life, and superior sound quality.
    Perfect for professionals and audiophiles.
    """

    keywords = text.extract_keywords(sample_text, top_k=5)
    print(f"✅ 提取的关键词: {', '.join(keywords)}")

    # 生成文案提示词
    analysis = {
        "category": "electronics",
        "style": "modern",
        "key_features": ["Noise Cancellation", "30h Battery", "Premium Sound"]
    }

    prompt = text.format_copywriting_prompt("product_page", analysis, "Premium headphones")
    print(f"\n✅ 生成的文案提示词:")
    print(f"  {prompt[:200]}...")


async def test_product_analysis_agent():
    """测试产品分析 Agent"""
    print("\n" + "="*60)
    print("🧪 测试 ProductAnalysisAgent")
    print("="*60)

    tools = ToolRegistry.create_default()
    agent = ProductAnalysisAgent(tools)

    # 创建工作区
    workflow_id = f"test-analysis-{uuid.uuid4()}"
    workspace = tools.filesystem.create_workspace(workflow_id)

    # 模拟请求
    request = {
        "image_url": "https://example.com/headphones.jpg",
        "background": "Premium wireless headphones for professionals",
        "user_id": uuid.uuid4(),
    }

    print(f"🔍 分析产品...")
    analysis = await agent.run(request, workspace)

    print(f"✅ 分析完成:")
    print(f"  - 类别: {analysis['category']}")
    print(f"  - 风格: {analysis['style']}")
    print(f"  - 关键特征: {', '.join(analysis['key_features'][:3])}")
    print(f"  - 营销角度: {', '.join(analysis.get('marketing_angles', []))}")

    # 检查分析报告文件
    report_path = f"{workspace}/workspace/analysis_report.md"
    if tools.filesystem.exists(report_path):
        print(f"✅ 分析报告已生成: {report_path}")


async def test_qa_agent():
    """测试 QA Agent"""
    print("\n" + "="*60)
    print("🧪 测试 QAAgent")
    print("="*60)

    tools = ToolRegistry.create_default()
    agent = QAAgent(tools)

    # 创建工作区
    workflow_id = f"test-qa-{uuid.uuid4()}"
    workspace = tools.filesystem.create_workspace(workflow_id)

    # 模拟数据
    analysis = {
        "category": "electronics",
        "key_features": ["Feature 1", "Feature 2", "Feature 3"],
    }

    copy_assets = [
        {"channel": "product_page", "content": "Great product with amazing features! " * 10},
        {"channel": "social_post", "content": "Check this out! " * 10},
    ]

    image_assets = [
        {"scene": "hero", "url": "https://example.com/hero.jpg"},
        {"scene": "lifestyle", "url": "https://example.com/lifestyle.jpg"},
        {"scene": "detail", "url": "https://example.com/detail.jpg"},
    ]

    video_asset = {
        "asset_id": "video-123",
        "url": "https://example.com/video.mp4",
        "is_fallback": False,
    }

    print(f"🔍 运行 QA 检查...")
    qa_report = await agent.run(
        analysis, copy_assets, image_assets, video_asset, workspace
    )

    print(f"✅ QA 检查完成:")
    print(f"  - 总分: {qa_report['score']:.2f}")
    print(f"  - 通过: {'✓' if qa_report['passed'] else '✗'}")
    print(f"  - 问题数量: {len(qa_report['issues'])}")
    print(f"  - 建议数量: {len(qa_report['suggestions'])}")

    if qa_report['issues']:
        print(f"\n  发现的问题:")
        for issue in qa_report['issues'][:3]:
            print(f"    - {issue}")


async def test_video_tools():
    """测试视频工具（Mock 模式）"""
    print("\n" + "="*60)
    print("🧪 测试 VideoTools (Mock 模式)")
    print("="*60)

    tools = ToolRegistry.create_default()
    video = tools.video

    # 测试视频生成（会自动 fallback 到 slideshow）
    prompt = "Dynamic product video showcasing premium features"
    images = [
        "https://example.com/img1.jpg",
        "https://example.com/img2.jpg",
        "https://example.com/img3.jpg",
    ]

    print(f"🎬 生成视频 (使用 Mock)...")
    result = await video.generate_video(
        prompt=prompt,
        image_paths=images,
        duration_sec=15,
        timeout_sec=5,
    )

    print(f"✅ 视频生成完成:")
    print(f"  - URL: {result['url']}")
    print(f"  - Provider: {result['provider']}")
    print(f"  - Fallback: {'是' if result.get('is_fallback') else '否'}")


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 Agent 能力测试套件")
    print("="*60)
    print("\n注意: 此测试使用 Mock 数据，不会调用真实的外部 API")

    try:
        await test_filesystem_tools()
        await test_vision_tools()
        await test_text_tools()
        await test_product_analysis_agent()
        await test_qa_agent()
        await test_video_tools()

        print("\n" + "="*60)
        print("✅ 所有测试完成!")
        print("="*60)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
