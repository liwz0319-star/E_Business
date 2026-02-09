#!/usr/bin/env python
"""Test DeepSeekGenerator initialization."""
import sys
print("[TEST] Starting DeepSeekGenerator test...", flush=True)

try:
    from app.infrastructure.generators import DeepSeekGenerator
    print("[TEST] Import successful", flush=True)

    print("[TEST] Creating DeepSeekGenerator instance...", flush=True)
    gen = DeepSeekGenerator()

    print(f"[TEST] SUCCESS: API key = {gen.api_key[:8]}...{gen.api_key[-4:]}", flush=True)
    print(f"[TEST] Model: {gen.model}", flush=True)
    print(f"[TEST] Max tokens: {gen.max_tokens}", flush=True)

except ValueError as e:
    print(f"[TEST] ERROR (ValueError): {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

except Exception as e:
    print(f"[TEST] ERROR (Exception): {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("[TEST] Test completed successfully", flush=True)
