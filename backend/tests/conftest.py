"""
Test Configuration and Fixtures

Provides shared fixtures for all tests including async client and database setup.
"""

import asyncio
import os
from collections.abc import AsyncGenerator
from typing import Generator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.infrastructure.database import Base, get_async_session
from app.main import fastapi_app


# Use PostgreSQL test database
TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/e_business_test"
)


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for async tests."""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Create async HTTP client for integration tests.

    Creates a fresh engine and tables for each test to avoid connection pool conflicts.
    """
    # Create a fresh engine for each test
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )

    test_async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Hold a session for the test duration
    test_session: AsyncSession | None = None

    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        """Override dependency to use test database session."""
        nonlocal test_session
        # Create or reuse the session
        if test_session is None:
            test_session = test_async_session_maker()
        try:
            yield test_session
            await test_session.commit()
        except Exception:
            await test_session.rollback()
            raise

    # Override the dependency
    fastapi_app.dependency_overrides[get_async_session] = override_get_async_session

    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create client
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Close the test session
    if test_session is not None:
        await test_session.close()

    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Clear overrides
    fastapi_app.dependency_overrides.clear()

    # Properly dispose the engine
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_client_with_session() -> AsyncGenerator[tuple[AsyncClient, AsyncSession], None]:
    """
    Create async HTTP client with a shared database session.

    This fixture returns both the client and a session that can be used
    to create test data that will be visible to the API.
    """
    # Create a fresh engine for each test
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )

    test_async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Create a shared session
    shared_session = test_async_session_maker()

    async def override_get_async_session() -> AsyncGenerator[AsyncSession, None]:
        """Override dependency to use shared test database session."""
        try:
            yield shared_session
            await shared_session.commit()
        except Exception:
            await shared_session.rollback()
            raise

    # Override the dependency
    fastapi_app.dependency_overrides[get_async_session] = override_get_async_session

    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create client
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, shared_session

    # Close the session
    await shared_session.close()

    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Clear overrides
    fastapi_app.dependency_overrides.clear()

    # Properly dispose the engine
    await test_engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create database session for direct database access in tests.
    """
    # Create a fresh engine for each test
    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )
    
    test_async_session_maker = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with test_async_session_maker() as session:
        yield session
    
    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    # Properly dispose the engine
    await test_engine.dispose()


# Alias for backward compatibility
async_session = db_session
