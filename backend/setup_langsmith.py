"""
LangSmith 快速设置脚本

交互式地引导用户配置 LangSmith。
"""
import os
import sys

# 设置 UTF-8 编码输出（Windows 兼容）
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def print_header(text):
    """打印标题"""
    print("\n" + "="*60)
    print(text)
    print("="*60)


def print_info(text):
    """打印信息"""
    print(f"\nℹ️  {text}")


def print_success(text):
    """打印成功消息"""
    print(f"\n✅ {text}")


def print_warning(text):
    """打印警告"""
    print(f"\n⚠️  {text}")


def get_user_input(prompt, default=None):
    """获取用户输入"""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    return input(full_prompt).strip() or default


def main():
    print_header("LangSmith 快速设置向导")

    print("""
本向导将帮助您配置 LangSmith 用于追踪和监控您的 AI Agent。

您需要：
1. 一个 LangSmith 账号（免费注册：https://smith.langchain.com）
2. LangSmith API Key

如果没有账号，请先注册，获取 API Key 后再运行此脚本。
    """)

    # 询问是否继续
    continue_setup = get_user_input("是否继续设置？(y/n)", "y").lower()
    if continue_setup != 'y':
        print("\n设置已取消。")
        return 1

    # 获取配置
    print_header("步骤 1: 输入 LangSmith 配置")

    api_key = get_user_input("请输入您的 LangSmith API Key (格式: lsv2_pt_...)")
    if not api_key:
        print_warning("未输入 API Key，无法继续设置。")
        return 1

    project_name = get_user_input("项目名称", "e-business")
    enable_tracing = get_user_input("启用追踪？(y/n)", "y").lower() == 'y'

    # 更新 .env 文件
    print_header("步骤 2: 更新 .env 文件")

    env_file = os.path.join(os.path.dirname(__file__), '.env')

    # 读取现有 .env 内容
    existing_lines = []
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()

    # 移除旧的 LangSmith 配置
    filtered_lines = [line for line in existing_lines
                      if not line.strip().startswith(('LANGCHAIN_TRACING_V2',
                                                      'LANGCHAIN_API_KEY',
                                                      'LANGCHAIN_PROJECT',
                                                      'LANGCHAIN_ENDPOINT'))]

    # 添加新的 LangSmith 配置
    new_config = f"""

# =============================================================================
# LangSmith 追踪配置
# =============================================================================
LANGCHAIN_TRACING_V2={"true" if enable_tracing else "false"}
LANGCHAIN_API_KEY={api_key}
LANGCHAIN_PROJECT={project_name}
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
"""

    # 写入 .env 文件
    with open(env_file, 'w', encoding='utf-8') as f:
        f.writelines(filtered_lines)
        f.write(new_config)

    print_success(f".env 文件已更新: {env_file}")

    # 显示配置摘要
    print_header("步骤 3: 配置摘要")
    print(f"""
LangSmith 配置：
  追踪启用: {enable_tracing}
  项目名称: {project_name}
  API Key: {api_key[:12]}...{api_key[-6:]}
  端点: https://api.smith.langchain.com
    """)

    # 验证配置
    print_header("步骤 4: 验证配置")

    print("\n正在验证配置...")

    # 重新加载环境变量
    from dotenv import load_dotenv
    load_dotenv(env_file, override=True)

    # 检查配置
    if os.getenv('LANGCHAIN_TRACING_V2') == 'true':
        print_success("追踪已启用")
    else:
        print_warning("追踪未启用")

    if os.getenv('LANGCHAIN_API_KEY'):
        print_success("API Key 已配置")
    else:
        print_warning("API Key 未配置")

    if os.getenv('LANGCHAIN_PROJECT'):
        print_success(f"项目名称: {os.getenv('LANGCHAIN_PROJECT')}")
    else:
        print_warning("项目名称未配置")

    # 下一步
    print_header("下一步")

    print("""
1. 启动应用：
   python -m uvicorn app.main:app --reload

2. 检查启动日志，确认 LangSmith 初始化成功

3. 触发一个 API 请求（例如文案生成）

4. 访问 LangSmith 查看追踪记录：
   https://smith.langchain.com

5. 在项目中，您会看到所有 LLM 调用的详细追踪
    """)

    print_success("设置完成！")

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n设置已取消。")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
