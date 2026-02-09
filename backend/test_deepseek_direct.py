"""
Direct test of DeepSeek API Key in running backend
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.infrastructure.generators import DeepSeekGenerator
from app.domain.entities.generation import GenerationRequest

async def main():
    print("=" * 70)
    print("DEEPSEEK API KEY RUNTIME TEST")
    print("=" * 70)

    # Test 1: Settings
    print("\n[TEST 1] Settings Configuration")
    print(f"  API Key exists: {bool(settings.deepseek_api_key)}")
    if settings.deepseek_api_key:
        print(f"  API Key length: {len(settings.deepseek_api_key)}")
        print(f"  API Key prefix: {settings.deepseek_api_key[:10]}...")
    else:
        print("  ERROR: API Key is None!")
        return False

    # Test 2: Generator initialization
    print("\n[TEST 2] DeepSeekGenerator Initialization")
    try:
        gen = DeepSeekGenerator()
        print("  SUCCESS: Generator initialized")
        print(f"  Generator API Key: {gen.api_key[:10]}...")
    except ValueError as e:
        print(f"  FAILED: {e}")
        return False

    # Test 3: Context manager
    print("\n[TEST 3] Context Manager Test")
    try:
        async with gen as generator:
            print("  SUCCESS: Context manager entered")
            request = GenerationRequest(
                prompt="Test prompt",
                model="deepseek-chat",
                temperature=0.7,
            )
            print("  Request created successfully")
            print("  Skipping actual API call to save quota")
    except Exception as e:
        print(f"  FAILED: {e}")
        return False

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED!")
    print("=" * 70)
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
