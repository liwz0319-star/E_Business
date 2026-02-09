
import sys
import os
from pathlib import Path

# Add current directory to sys.path to mimic running from root
sys.path.append(os.getcwd())

print(f"Current Working Directory: {os.getcwd()}")
print(f"Python Executable: {sys.executable}")

try:
    from app.core.config import settings
    print(f"\n[Config Status]")
    print(f"DeepSeek API Key in Settings: '{settings.deepseek_api_key}'")
    
    # Check where pydantic thinks the .env file is
    env_file_path = settings.model_config.get('env_file')
    print(f"Pydantic config 'env_file' path: {env_file_path}")
    
    if env_file_path:
        path = Path(env_file_path)
        print(f"Does this file exist? {path.exists()}")
        if path.exists():
            print(f"File absolute path: {path.resolve()}")
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
                print("--- Content Preview (First 5 lines) ---")
                print('\n'.join(content.splitlines()[:5]))
                print("---------------------------------------")
        else:
            print("❌ The file configured in settings DOES NOT EXIST.")
            
            # Proactive check: where IS the .env file?
            potential_paths = [
                Path("backend/.env"),
                Path(".env"),
                Path("app/core/../.env"), # faulty logic check
            ]
            print("\nSearching for .env in common locations:")
            for p in potential_paths:
                print(f"  - {p.resolve()}: {'FOUND' if p.exists() else 'Missing'}")

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Ensure you are running this from 'f:\\AAA Work\\AIproject\\E_Business\\backend' or equivalent.")
except Exception as e:
    print(f"❌ Unexpected Error: {e}")
