import asyncio
import os
import sys
import traceback

# Ensure we can import from app
sys.path.append(os.getcwd())

from app.core.config import settings
from app.core.factory import ProviderFactory
from app.domain.entities.generation import GenerationRequest
from app.infrastructure.generators import DeepSeekGenerator

async def main():
    print("Testing DeepSeek connection...")
    
    # Debug info
    print(f"CWD: {os.getcwd()}")
    print(f"Env file exists: {os.path.exists('.env')}")
    print(f"DEEPSEEK_API_KEY env var: {os.environ.get('DEEPSEEK_API_KEY')}")
    print(f"Settings DEEPSEEK_API_KEY: {settings.deepseek_api_key}")
    
    # Manually register the provider
    ProviderFactory.register("deepseek", DeepSeekGenerator)
    
    try:
        async with ProviderFactory.get_provider("deepseek") as generator:
            print(f"Generator initialized with key: {generator.api_key}")
            request = GenerationRequest(
                prompt="Say 'Hello, DeepSeek!'",
                model="deepseek-chat"
            )
            result = await generator.generate(request)
            print(f"✅ Success! Response: {result.content}")
    except Exception:
        print("❌ Failed:")
        print(traceback.format_exc())

if __name__ == "__main__":
    asyncio.run(main())
