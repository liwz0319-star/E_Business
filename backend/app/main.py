"""
E-Business Backend API

Main FastAPI application entry point.
"""

from contextlib import asynccontextmanager
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.factory import ProviderFactory
from app.infrastructure.database import close_db, init_db
from app.infrastructure.generators import DeepSeekGenerator
from app.interface.routes import auth_router, copywriting_router, images_router
from app.interface.routes.debug import router as debug_router
from app.interface.ws import socket_manager


def _candidate_env_files() -> list[Path]:
    """Return .env lookup candidates in priority order."""
    backend_dir = Path(__file__).resolve().parents[1]
    project_dir = backend_dir.parent
    cwd = Path.cwd().resolve()
    return [
        backend_dir / ".env",
        project_dir / ".env",
        cwd / ".env",
        cwd / "backend" / ".env",
    ]


def _promote_env_to_os_environ() -> Optional[Path]:
    """Load the first existing .env file into os.environ."""
    for env_file in _candidate_env_files():
        if env_file.exists():
            # Keep explicit OS env values (prod/runtime overrides) as highest priority.
            load_dotenv(env_file, override=False)
            return env_file
    return None


def _ensure_provider_registration() -> None:
    """Register providers once even if lifespan hooks are skipped."""
    if "deepseek" not in ProviderFactory._registry:
        ProviderFactory.register("deepseek", DeepSeekGenerator)


# Promote .env and register providers at import time as a safety net.
# Some ASGI wrappers may bypass FastAPI lifespan events.
_promote_env_to_os_environ()
_ensure_provider_registration()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    print("\n" + "="*50)
    print("BACKEND STARTUP CHECK")
    print("="*50)

    loaded_env_file = _promote_env_to_os_environ()
    print("Checking .env paths:")
    print(f" - CWD: {os.getcwd()}")
    print(f" - Candidates: {_candidate_env_files()}")
    print(f" - Loaded: {loaded_env_file if loaded_env_file else 'NONE'}")

    # Refresh settings after promoting .env keys into os.environ.
    runtime_settings = get_settings()
    api_key = os.getenv("DEEPSEEK_API_KEY") or runtime_settings.deepseek_api_key
    has_key = bool(api_key and len(api_key) > 10)
    masked_key = f"{api_key[:8]}...{api_key[-4:]}" if has_key else "MISSING/EMPTY"

    # Use ASCII-safe characters for Windows console compatibility
    status_symbol = "[OK]" if has_key else "[FAIL]"
    print(f"DeepSeek API Key Status: {status_symbol} {'LOADED' if has_key else 'MISSING'}")
    print(f"Key Value (Masked): {masked_key}")

    if not has_key:
        print("\n[CRITICAL ERROR] DeepSeek API Key is missing!")
        print("Please check your .env file or environment variables.")
        print("Expected variable: DEEPSEEK_API_KEY")
        # Fail fast to prevent runtime errors later
        raise ValueError("DeepSeek API key is required but not found in settings!")

    print("="*50 + "\n")

    await init_db()
    _ensure_provider_registration()
    
    yield
    # Shutdown
    await close_db()


# Create FastAPI application
settings = get_settings()
fastapi_app = FastAPI(
    title="E_Business API",
    description="AI-Powered E-Business Content Generation Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
origins = settings.cors_origins_list
is_wildcard = "*" in origins

fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=not is_wildcard,  # Disable creds for wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
fastapi_app.include_router(auth_router, prefix="/api/v1")
fastapi_app.include_router(copywriting_router, prefix="/api/v1")
fastapi_app.include_router(images_router, prefix="/api/v1")
fastapi_app.include_router(debug_router, prefix="/api/v1")


@fastapi_app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


# Wrap FastAPI with Socket.IO (official recommended way)
# Socket.IO will handle /socket.io path, FastAPI handles everything else
# Export as 'app' for uvicorn compatibility: uvicorn app.main:app
app = socket_manager.wrap_app(fastapi_app)
