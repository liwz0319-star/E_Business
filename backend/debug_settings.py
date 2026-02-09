
import sys
from pathlib import Path
import os

# Add the current directory to sys.path so we can import app
sys.path.append(str(Path.cwd()))

try:
    from app.core.config import settings
    print(f"DeepSeek API Key from settings: '{settings.deepseek_api_key}'")
    
    # Check if .env file exists where config expects it
    config_file = Path("app/core/config.py").resolve()
    expected_env = config_file.parent.parent.parent / ".env"
    print(f"Config file path: {config_file}")
    print(f"Expected .env path: {expected_env}")
    print(f"Does .env exist there? {expected_env.exists()}")
    
    if expected_env.exists():
        with open(expected_env, "r") as f:
            content = f.read()
            print("First few lines of .env:")
            print("\n".join(content.splitlines()[:5]))
            
except Exception as e:
    print(f"Error: {e}")
