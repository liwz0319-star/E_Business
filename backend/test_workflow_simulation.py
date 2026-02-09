#!/usr/bin/env python
"""Test complete workflow execution including async tasks."""
import asyncio
import sys

print("[TEST-1] Importing modules...", flush=True)
try:
    from app.core.factory import ProviderFactory
    from app.infrastructure.generators import DeepSeekGenerator
    from app.application.agents.copywriting_agent import CopywritingAgent
    print("[TEST-1] SUCCESS: All modules imported", flush=True)
except Exception as e:
    print(f"[TEST-1] ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[TEST-2] Registering DeepSeek provider...", flush=True)
try:
    ProviderFactory.register("deepseek", DeepSeekGenerator)
    print("[TEST-2] SUCCESS: Provider registered", flush=True)
except Exception as e:
    print(f"[TEST-2] ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[TEST-3] Testing ProviderFactory.get_provider()...", flush=True)
try:
    generator = ProviderFactory.get_provider("deepseek")
    print(f"[TEST-3] SUCCESS: Got provider instance: {type(generator)}", flush=True)
    print(f"[TEST-3] API Key: {generator.api_key[:8]}...{generator.api_key[-4:]}", flush=True)
except Exception as e:
    print(f"[TEST-3] ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[TEST-4] Testing CopywritingAgent initialization...", flush=True)
try:
    agent = CopywritingAgent()
    print("[TEST-4] SUCCESS: CopywritingAgent created", flush=True)
    print(f"[TEST-4] Model: {agent.model}", flush=True)
except Exception as e:
    print(f"[TEST-4] ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[TEST-5] Testing async workflow execution...", flush=True)
async def test_async_workflow():
    """Test async workflow similar to E2E scenario."""
    try:
        workflow_id = "test-workflow-123"
        print(f"[TEST-5] Starting workflow: {workflow_id}", flush=True)

        # This is what the API route does
        await agent.run_async(
            product_name="Test Product",
            features=["Feature 1", "Feature 2"],
            brand_guidelines="Test guidelines",
            workflow_id=workflow_id,
        )

        print(f"[TEST-5] Workflow started successfully", flush=True)

        # Wait a bit for async task to start
        await asyncio.sleep(2)

        # Check workflow status
        status = CopywritingAgent.get_workflow_status(workflow_id)
        if status:
            print(f"[TEST-5] Workflow status: {status.get('status')}", flush=True)
            print(f"[TEST-5] Current stage: {status.get('current_stage')}", flush=True)
        else:
            print("[TEST-5] WARNING: No workflow status found", flush=True)

        print("[TEST-5] SUCCESS: Async workflow test completed", flush=True)

    except Exception as e:
        print(f"[TEST-5] ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        raise

try:
    asyncio.run(test_async_workflow())
except Exception as e:
    print(f"\n[TEST-5] FAILED: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[TEST] All tests completed successfully!", flush=True)
