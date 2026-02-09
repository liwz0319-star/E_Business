#!/bin/bash
# Complete cleanup and restart script for backend

echo "=== Step 1: Kill all Python processes ==="
taskkill //F //IM python.exe 2>/dev/null
sleep 2

echo "=== Step 2: Clear all Python caches ==="
cd "F:\AAA Work\AIproject\E_Business\backend"
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
rm -f backend_startup.log
echo "Caches cleared"

echo "=== Step 3: Verify modified files ==="
echo "Checking deepseek.py for get_settings import:"
grep "from app.core.config import get_settings" app/infrastructure/generators/deepseek.py && echo "✅ deepseek.py is correct" || echo "❌ deepseek.py NOT modified"

echo "Checking copywriting_agent.py for get_settings:"
grep "from app.core.config import get_settings" app/application/agents/copywriting_agent.py && echo "✅ copywriting_agent.py is correct" || echo "❌ copywriting_agent.py NOT modified"

echo "=== Step 4: Start backend with fresh process ==="
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > backend_startup.log 2>&1 &
BACKEND_PID=$!
echo "Backend started with PID: $BACKEND_PID"

echo "=== Step 5: Wait for startup and verify ==="
sleep 8
tail -20 backend_startup.log

echo ""
echo "=== Setup Complete ==="
echo "Backend is running at http://localhost:8000"
echo "Please test E2E workflow now"
