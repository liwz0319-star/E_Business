import asyncio
import os
from app.core.factory import ProviderFactory
from app.domain.entities.generation import GenerationRequest

# 确保在运行前设置了环境变量，或者依靠 .env 文件
# os.environ["DEEPSEEK_API_KEY"] = "sk-..."

async def main():
print("Testing DeepSeek connection...")
try:
async with ProviderFactory.get_provider("deepseek") as generator:
request = GenerationRequest(
prompt="Say 'Hello, DeepSeek!'",
model="deepseek-chat"
)
result = await generator.generate(request)
print(f"✅ Success! Response: {result.content}")
except Exception as e:
print(f"❌ Failed: {e}")

if __name__ == "__main__":
asyncio.run(main())