"""
LangSmith 集成测试脚本

用于验证 LangSmith 是否正确配置。
"""
import os
import sys

# 设置 UTF-8 编码输出（Windows 兼容）
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 添加 backend 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.langchain_init import init_langsmith, get_langsmith_config


def test_langsmith_config():
    """测试 LangSmith 配置读取"""
    print("="*60)
    print("LangSmith 配置测试")
    print("="*60)

    config = get_langsmith_config()

    print(f"\n当前配置:")
    print(f"  启用状态: {config['enabled']}")
    print(f"  项目名称: {config['project']}")
    print(f"  API 端点: {config['endpoint']}")
    print(f"  API Key 已配置: {config['api_key_configured']}")
    print(f"  追踪环境变量: {config['tracing_env_var']}")

    if not config['enabled']:
        print("\n⚠️  LangSmith 追踪未启用")
        print("请在 .env 文件中设置: LANGCHAIN_TRACING_V2=true")
        return False

    if not config['api_key_configured']:
        print("\n⚠️  LangSmith API Key 未配置")
        print("请在 .env 文件中设置: LANGCHAIN_API_KEY=your-api-key")
        return False

    print("\n✅ 配置检查通过")
    return True


def test_langsmith_init():
    """测试 LangSmith 初始化"""
    print("\n" + "="*60)
    print("LangSmith 初始化测试")
    print("="*60)

    success = init_langsmith()

    if success:
        print("\n✅ LangSmith 初始化成功")
        print(f"环境变量已设置:")
        print(f"  LANGCHAIN_TRACING_V2={os.getenv('LANGCHAIN_TRACING_V2')}")
        print(f"  LANGCHAIN_PROJECT={os.getenv('LANGCHAIN_PROJECT')}")
        print(f"  LANGCHAIN_ENDPOINT={os.getenv('LANGCHAIN_ENDPOINT')}")
        return True
    else:
        print("\n❌ LangSmith 初始化失败")
        print("请检查配置和 API Key")
        return False


def test_imports():
    """测试必要的包导入"""
    print("\n" + "="*60)
    print("依赖包测试")
    print("="*60)

    try:
        import langsmith
        print(f"✅ langsmith 包已安装 (版本: {langsmith.__version__})")
    except ImportError as e:
        print(f"❌ langsmith 包未安装: {e}")
        return False

    try:
        from langchain_core import runnables
        print("✅ langchain-core 包已安装")
    except ImportError as e:
        print(f"❌ langchain-core 包未安装: {e}")
        return False

    try:
        from langgraph.graph import StateGraph
        print("✅ langgraph 包已安装")
    except ImportError as e:
        print(f"❌ langgraph 包未安装: {e}")
        return False

    return True


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("LangSmith 集成测试")
    print("="*60)

    # 测试依赖
    deps_ok = test_imports()

    # 测试配置
    config_ok = test_langsmith_config()

    # 测试初始化
    init_ok = test_langsmith_init() if config_ok else False

    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    print(f"依赖包: {'✅ 通过' if deps_ok else '❌ 失败'}")
    print(f"配置检查: {'✅ 通过' if config_ok else '❌ 失败'}")
    print(f"初始化: {'✅ 通过' if init_ok else '❌ 失败'}")

    if deps_ok and config_ok and init_ok:
        print("\n🎉 所有测试通过！LangSmith 已正确配置。")
        print("\n下一步:")
        print("1. 启动应用: python -m uvicorn app.main:app --reload")
        print("2. 访问 LangSmith: https://smith.langchain.com")
        print("3. 查看 'Runs' 页面追踪您的 Agent 执行")
        return 0
    else:
        print("\n❌ 部分测试失败，请检查配置。")
        print("\n常见问题:")
        print("1. 确保已安装: pip install langsmith langchain-core langgraph")
        print("2. 确保 .env 文件中配置了 LANGCHAIN_API_KEY")
        print("3. 确保 .env 文件中设置了 LANGCHAIN_TRACING_V2=true")
        return 1


if __name__ == "__main__":
    sys.exit(main())
