"""
E-Business Backend API

Main FastAPI application entry point.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.factory import ProviderFactory
from app.infrastructure.database import close_db, init_db
from app.infrastructure.generators import DeepSeekGenerator
from app.interface.routes import auth_router, copywriting_router
from app.interface.ws import socket_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    
    Handles startup and shutdown events.
    """
    # Startup
    await init_db()
    
    # Register AI providers
    ProviderFactory.register("deepseek", DeepSeekGenerator)
    
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title="E_Business API",
    description="AI-Powered E-Business Content Generation Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# Configure CORS
origins = settings.cors_origins_list
is_wildcard = "*" in origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=not is_wildcard,  # Disable creds for wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(copywriting_router, prefix="/api/v1")

# Mount Socket.IO at /ws path
app.mount("/ws", socket_manager.app)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

