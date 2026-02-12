"""
测试 Agent 真实 LLM 生成能力

这个脚本使用真实的 LLM API（DeepSeek）来测试 Agent 的文本生成能力
"""

# 修复 Windows 终端编码问题
import sys
import io
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
from app.core.factory import ProviderFactory
from app.core.langchain_init import init_langsmith, get_langsmith_config

# 注册 providers（因为测试脚本不会通过 main.py 启动）
ProviderFactory.register("deepseek", DeepSeekGenerator)

# 初始化 LangSmith 追踪
init_langsmith()
langsmith_config = get_langsmith_config()
print(f"\n📊 LangSmith 配置:")
print(f"  - 启用: {langsmith_config['enabled']}")
print(f"  - 项目: {langsmith_config['project']}")
print(f"  - API Key: {langsmith_config['api_key_configured']}")
print(f"  - 追踪状态: {langsmith_config['tracing_env_var']}")


def check_api_key():
    """检查 API Key 是否配置"""
    load_dotenv()

    api_key = os.getenv("DEEPSEEK_API_KEY")

    if not api_key or api_key == "your-api-key-here":
        print("\n" + "="*60)
        print("❌ 错误: DEEPSEEK_API_KEY 未配置")
        print("="*60)
        print("\n请在 backend/.env 文件中设置:")
        print("  DEEPSEEK_API_KEY=your_actual_api_key_here")
        print("\n或者设置环境变量:")
        print("  export DEEPSEEK_API_KEY=your_actual_api_key_here")
        print("\n获取 API Key: https://platform.deepseek.com/api_keys")
        print("="*60)
        return False

    return True


async def test_llm_connection():
    """测试 LLM 连接"""
    print("\n" + "="*60)
    print("🔗 测试 LLM 连接")
    print("="*60)

    try:
        async with DeepSeekGenerator() as llm:
            request = GenerationRequest(
                prompt="Hello, please respond with 'OK'",
                model="deepseek-chat"
            )
            result = await llm.generate(request)
            response = result.content

            if response and len(response) > 0:
                print(f"✅ LLM 连接成功")
                print(f"   响应: {response[:100]}...")
                return True
            else:
                print(f"❌ LLM 响应异常")
                return False

    except Exception as e:
        print(f"❌ LLM 连接失败: {e}")
        return False


async def test_text_generation():
    """测试基础文本生成"""
    print("\n" + "="*60)
    print("📝 测试文本生成")
    print("="*60)

    try:
        async with DeepSeekGenerator() as llm:
            # 测试场景 1: 产品描述生成
            print("\n📝 场景 1: 生成产品描述")
            prompt = """请为以下产品生成一段吸引人的营销描述:

产品: 高端无线耳机
特点: 主动降噪、30小时续航、优质音质

要求: 简洁专业，50字以内
"""
            request = GenerationRequest(prompt=prompt, model="deepseek-chat", temperature=0.7)
            description = (await llm.generate(request)).content
            print(f"✅ 生成的描述:")
            print(f"   {description}")
            print(f"   字数: {len(description)}")

            # 测试场景 2: 营销文案生成
            print("\n📝 场景 2: 生成营销文案")
            prompt = """请为无线耳机生成3个不同风格的社交媒体营销文案:

产品特点:
- 主动降噪技术
- 30小时超长续航
- 专业级音质

要求: 每个文案 100 字以内，风格分别为: 专业、活泼、简洁
"""
            request = GenerationRequest(prompt=prompt, model="deepseek-chat", temperature=0.8)
            copywriting = (await llm.generate(request)).content
            print(f"✅ 生成的文案:")
            for i, variant in enumerate(copywriting.split('\n\n')[:3], 1):
                print(f"\n   变体 {i}:")
                print(f"   {variant.strip()}")

            # 测试场景 3: 关键词提取
            print("\n📝 场景 3: 提取产品关键词")
            prompt = """从以下产品描述中提取 5-8 个最重要的关键词:

产品描述:
这款高端无线耳机采用最新的主动降噪技术，有效隔绝环境噪音。
配备 500mAh 大容量电池，续航时间长达 30 小时。
40mm 钕铁硼单元驱动单元，提供专业级音质表现。
适合商务人士、音乐发烧友和对音质有要求的用户。

要求: 只返回关键词列表，用逗号分隔
"""
            request = GenerationRequest(prompt=prompt, model="deepseek-chat", temperature=0.5)
            keywords = (await llm.generate(request)).content
            print(f"✅ 提取的关键词:")
            print(f"   {keywords}")

    except Exception as e:
        print(f"❌ 文本生成失败: {e}")


async def test_product_analysis_with_llm():
    """测试产品分析 Agent（使用真实 LLM）"""
    print("\n" + "="*60)
    print("🔍 测试 ProductAnalysisAgent (真实 LLM)")
    print("="*60)

    try:
        # 使用真实 LLM client
        llm = DeepSeekGenerator()
        tools = ToolRegistry.create_default(llm_client=llm)

        agent = ProductAnalysisAgent(tools)

        # 创建工作区
        workflow_id = f"test-analysis-{uuid.uuid4()}"
        workspace = tools.filesystem.create_workspace(workflow_id)

        print(f"✅ 工作区创建成功: {workspace}")

        # 模拟真实请求
        request = {
            "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e",
            "background": """
这是一款高端无线蓝牙耳机，采用最新的主动降噪技术。

产品特点:
1. 主动降噪 (ANC) - 有效隔绝外界噪音
2. 超长续航 - 30小时连续播放时间
3. 快速充电 - 充电10分钟，使用3小时
4. 高品质音质 - 40mm 钕铁硼单元驱动
5. 舒适佩戴 - 记忆海绵耳罩，轻量化设计

目标用户: 商务人士、音乐发烧友、通勤族
价格定位: 中高端 (¥899-1299)
""",
            "user_id": uuid.uuid4(),
        }

        print(f"\n🔍 使用真实 LLM 分析产品...")
        print("⏳ 这可能需要 10-20 秒...")

        analysis = await agent.run(request, workspace)

        print(f"\n✅ 分析完成:")
        print(f"  - 类别: {analysis.get('category', 'N/A')}")
        print(f"  - 风格: {analysis.get('style', 'N/A')}")
        print(f"  - 目标受众: {analysis.get('target_audience', 'N/A')}")
        print(f"  - 关键特征: {', '.join(analysis.get('key_features', [])[:5])}")

        marketing_angles = analysis.get('marketing_angles', [])
        if marketing_angles:
            print(f"  - 营销角度: {len(marketing_angles)} 个")
            for i, angle in enumerate(marketing_angles[:3], 1):
                print(f"     {i}. {angle}")

        # 检查生成的文件
        report_path = f"{workspace}/workspace/analysis_report.md"
        if tools.filesystem.exists(report_path):
            print(f"\n✅ 分析报告已生成: {report_path}")
            # 读取并显示部分内容
            content = tools.filesystem.read_file(report_path)
            lines = content.split('\n')
            print(f"\n📄 报告预览 (前 {min(10, len(lines))} 行):")
            for line in lines[:10]:
                print(f"   {line}")

    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()


async def test_copywriting_generation():
    """测试文案生成（使用真实 LLM）"""
    print("\n" + "="*60)
    print("✍️ 测试 CopywritingAgent (真实 LLM)")
    print("="*60)

    try:
        # CopywritingAgent 使用 ProviderFactory，不需要传递 tools
        agent = CopywritingAgent()

        workflow_id = f"test-copy-{uuid.uuid4()}"
        print(f"✅ 工作流 ID: {workflow_id}")

        print(f"\n✍️ 使用真实 LLM 生成文案...")
        print("⏳ 这可能需要 15-30 秒...")

        # CopywritingAgent.run() 需要 product_name 和 features
        result = await agent.run(
            product_name="高端无线降噪耳机",
            features=[
                "主动降噪技术，有效隔绝环境噪音",
                "30小时超长续航，满足全天使用",
                "快速充电功能，充电10分钟使用3小时",
                "40mm钕铁硼驱动单元，专业级音质",
                "记忆海绵耳罩，轻量化舒适佩戴"
            ],
            brand_guidelines="专业、现代、高端，突出科技感和品质",
            workflow_id=workflow_id
        )

        # 检查生成的各个阶段
        print(f"\n✅ 文案生成完成:")

        if result.get("plan"):
            print(f"  📋 计划: {len(result['plan'])} 字符")

        if result.get("draft"):
            print(f"  📝 草稿: {len(result['draft'])} 字符")
            # 显示草稿预览
            draft = result["draft"]
            preview = draft[:300] + "..." if len(draft) > 300 else draft
            print(f"\n  草稿预览:")
            print(f"    {preview}")

        if result.get("critique"):
            print(f"  🔍 评审: {len(result['critique'])} 字符")

        if result.get("final_copy"):
            print(f"  ✅ 最终文案: {len(result['final_copy'])} 字符")
            # 显示最终文案
            final = result["final_copy"]
            print(f"\n  最终文案:")
            print(f"    {final}")

    except Exception as e:
        print(f"❌ 文案生成失败: {e}")
        import traceback
        traceback.print_exc()


async def test_qa_with_llm():
    """测试 QA Agent（使用真实 LLM）"""
    print("\n" + "="*60)
    print("✅ 测试 QAAgent (真实 LLM)")
    print("="*60)

    try:
        llm = DeepSeekGenerator()
        tools = ToolRegistry.create_default(llm_client=llm)

        agent = QAAgent(tools)

        # 创建工作区
        workflow_id = f"test-qa-{uuid.uuid4()}"
        workspace = tools.filesystem.create_workspace(workflow_id)

        print(f"✅ 工作区创建成功")

        # 准备测试数据
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
            {
                "channel": "social_post",
                "content": "🎧 音乐发烧友必入！主动降噪 + 30小时续航，让音乐随时相伴。#高端耳机 #音乐推荐"
            }
        ]

        image_assets = [
            {"scene": "hero", "url": "https://example.com/hero.jpg"}
        ]

        video_asset = {
            "asset_id": "video-123",
            "url": "https://example.com/video.mp4",
            "is_fallback": False,
        }

        print(f"\n✅ 使用真实 LLM 进行 QA 检查...")
        print("⏳ 这可能需要 10-20 秒...")

        qa_report = await agent.run(
            analysis, copy_assets, image_assets, video_asset, workspace
        )

        print(f"\n✅ QA 检查完成:")
        print(f"  - 总分: {qa_report.get('score', 0):.2f}")
        print(f"  - 通过: {'✅' if qa_report.get('passed') else '❌'}")
        print(f"  - 问题数量: {len(qa_report.get('issues', []))}")
        print(f"  - 建议数量: {len(qa_report.get('suggestions', []))}")

        issues = qa_report.get('issues', [])
        if issues:
            print(f"\n⚠️  发现的问题:")
            for issue in issues[:3]:
                print(f"    - {issue}")

        suggestions = qa_report.get('suggestions', [])
        if suggestions:
            print(f"\n💡 改进建议:")
            for suggestion in suggestions[:3]:
                print(f"    - {suggestion}")

        # 检查生成的报告文件
        report_path = f"{workspace}/workspace/qa_report.md"
        if tools.filesystem.exists(report_path):
            print(f"\n✅ QA 报告已生成: {report_path}")

    except Exception as e:
        print(f"❌ QA 检查失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 Agent LLM 生成能力测试")
    print("="*60)

    # 检查 API Key
    if not check_api_key():
        return

    try:
        # 测试 LLM 连接
        if not await test_llm_connection():
            print("\n❌ LLM 连接失败，请检查 API Key 和网络连接")
            return

        # 测试文本生成
        await test_text_generation()

        # 测试产品分析 Agent
        await test_product_analysis_with_llm()

        # 测试文案生成 Agent
        await test_copywriting_generation()

        # 测试 QA Agent
        await test_qa_with_llm()

        print("\n" + "="*60)
        print("✅ 所有测试完成!")
        print("="*60)

        print("\n📊 测试总结:")
        print("  ✓ LLM 连接测试")
        print("  ✓ 基础文本生成测试")
        print("  ✓ ProductAnalysisAgent 测试")
        print("  ✓ CopywritingAgent 测试")
        print("  ✓ QAAgent 测试")
        print("\n💡 提示:")
        print("  - 查看生成的工作区: backend/projects/test-*/workspace/")
        print("  - 分析报告和 QA 报告保存在工作区中")
        print("  - 可以调整提示词来测试不同场景")

    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
