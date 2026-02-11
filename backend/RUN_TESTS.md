"""
快速测试运行脚本

一键运行所有测试并生成报告
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """运行命令并显示输出"""
    print(f"\n{'='*70}")
    print(f"🔧 {description}")
    print(f"{'='*70}")
    print(f"命令: {' '.join(cmd)}\n")

    result = subprocess.run(cmd, capture_output=False)

    if result.returncode != 0:
        print(f"\n❌ {description} 失败")
        return False
    else:
        print(f"\n✅ {description} 成功")
        return True


def main():
    """运行测试套件"""
    print("\n" + "="*70)
    print("🧪 DeepAgents 测试套件")
    print("="*70)

    backend_dir = Path(__file__).parent
    tests_passed = []

    # 1. 代码语法检查
    if run_command(
        ["python", "-m", "pytest", "tests/test_health.py", "-v"],
        "1. 健康检查测试"
    ):
        tests_passed.append("健康检查")

    # 2. 工具层测试
    if run_command(
        ["python", "-m", "pytest", "tests/application/tools/test_filesystem_tools.py", "-v"],
        "2. 文件系统工具测试"
    ):
        tests_passed.append("文件系统工具")

    # 3. 仓储层测试
    if run_command(
        ["python", "-m", "pytest", "tests/infrastructure/repositories/test_product_package_repo_async.py", "-v"],
        "3. 产品包仓储测试"
    ):
        tests_passed.append("产品包仓储")

    # 4. 集成测试
    if run_command(
        ["python", "-m", "pytest", "tests/integration/test_product_package_workflow.py", "-v", "-s"],
        "4. 产品包工作流集成测试"
    ):
        tests_passed.append("工作流集成")

    # 5. 手动 Agent 测试
    print(f"\n{'='*70}")
    print(f"🔧 5. 手动 Agent 能力测试")
    print(f"{'='*70}")
    print("\n提示: 运行以下命令进行交互式测试:")
    print(f"  python scripts/test_agents_manual.py")

    # 总结
    print("\n" + "="*70)
    print("📊 测试总结")
    print("="*70)
    print(f"通过: {len(tests_passed)}/{4}")
    for test in tests_passed:
        print(f"  ✓ {test}")

    if len(tests_passed) == 4:
        print("\n🎉 所有核心测试通过!")
        return 0
    else:
        print(f"\n⚠️  部分测试失败，请检查日志")
        return 1


if __name__ == "__main__":
    sys.exit(main())
