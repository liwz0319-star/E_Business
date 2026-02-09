"""
Direct workflow test to debug API key issue.
"""
import asyncio
import os
import sys

# 确保我们在正确的目录
os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
print(f"Working directory: {os.getcwd()}")

# 手动加载 .env
from pathlib import Path
env_file = Path(".env")
if env_file.exists():
    print(f".env file exists: {env_file.resolve()}")
    for line in env_file.read_text().splitlines():
        if line.strip() and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if key == "DEEPSEEK_API_KEY":
                print(f"Found DEEPSEEK_API_KEY in .env: {value[:10]}...")
                if not os.getenv(key):
                    os.environ[key] = value
                    print(f"Set environment variable: {key}")
else:
    print(f".env file NOT FOUND at: {env_file.resolve()}")

# 现在导入模块
print("\n--- Importing modules ---")
from app.core.config import get_settings
settings = get_settings()
print(f"Settings deepseek_api_key: {bool(settings.deepseek_api_key)}")
if settings.deepseek_api_key:
    print(f"Key prefix: {settings.deepseek_api_key[:10]}...")


print("\n--- Testing DeepSeekGenerator ---")
from app.infrastructure.generators.deepseek import DeepSeekGenerator
try:
    gen = DeepSeekGenerator()
    print(f"DeepSeekGenerator created successfully!")
    print(f"API key suffix: ***{gen.api_key[-4:]}")
except ValueError as e:
    print(f"ERROR creating DeepSeekGenerator: {e}")
    sys.exit(1)


print("\n--- Testing ProviderFactory ---")
from app.core.factory import ProviderFactory
ProviderFactory.register("deepseek", DeepSeekGenerator)

provider = ProviderFactory.get_provider("deepseek")
print(f"Provider from factory: {type(provider).__name__}")
print(f"Provider API key suffix: ***{provider.api_key[-4:]}")


print("\n--- Testing CopywritingAgent ---")
from app.application.agents.copywriting_agent import CopywritingAgent

async def test_workflow():
    agent = CopywritingAgent()
    print(f"CopywritingAgent created")
    
    # 测试一个简单的生成
    try:
        result = await agent._generate("Say 'Hello' in one word", "test-workflow-id")
        print(f"Generation result: {result[:50]}...")
    except Exception as e:
        print(f"Generation ERROR: {type(e).__name__}: {e}")

asyncio.run(test_workflow())

print("\n--- All tests passed! ---")
