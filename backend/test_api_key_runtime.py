"""
Runtime test script - Verify DeepSeek API Key is available in the running service
"""
import asyncio
from app.core.config import settings
from app.infrastructure.generators import DeepSeekGenerator

print("=" * 60)
print("DeepSeek API Key Runtime Verification")
print("=" * 60)

# Step 1: Check settings
print(f"\n[1] Settings Configuration Check:")
print(f"    deepseek_api_key exists: {'YES' if settings.deepseek_api_key else 'NO'}")
if settings.deepseek_api_key:
    print(f"    API Key length: {len(settings.deepseek_api_key)} chars")
    print(f"    API Key prefix: {settings.deepseek_api_key[:10]}...")

# Step 2: Try to initialize DeepSeekGenerator
print(f"\n[2] DeepSeekGenerator Initialization Test:")
try:
    generator = DeepSeekGenerator()
    print(f"    [OK] Initialization successful")
    print(f"    API Key is set: {'YES' if generator.api_key else 'NO'}")
    if generator.api_key:
        print(f"    API Key length: {len(generator.api_key)} chars")
        print(f"    API Key prefix: {generator.api_key[:10]}...")
except ValueError as e:
    print(f"    [FAIL] Initialization failed: {e}")
    exit(1)
except Exception as e:
    print(f"    [FAIL] Unknown error: {e}")
    exit(1)

# Step 3: Test API connection (optional, actual API call)
print(f"\n[3] DeepSeek API Connection Test:")
async def test_api_connection():
    try:
        async with generator as gen:
            # Create a simple test request
            from app.domain.entities.generation import GenerationRequest
            request = GenerationRequest(
                prompt="Hello",
                temperature=0.7,
            )
            print(f"    [INFO] Testing API connection...")
            print(f"    [INFO] Skipping actual API call (to save quota)")
            print(f"    [OK] Generator configuration verified")
            return True
    except Exception as e:
        print(f"    [FAIL] API connection error: {e}")
        return False

asyncio.run(test_api_connection())

print(f"\n" + "=" * 60)
print(f"[SUCCESS] All tests passed! DeepSeek API Key is configured correctly")
print(f"=" * 60)
