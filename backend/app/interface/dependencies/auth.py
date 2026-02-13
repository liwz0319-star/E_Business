"""
Auth Dependencies

FastAPI dependencies for authentication and authorization.
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_token_subject
from app.domain.entities.user import User
from app.infrastructure.database import get_async_session
from app.infrastructure.repositories.user_repository import UserRepository


# HTTP Bearer token scheme
# auto_error=False 允许我们自定义 401 响应而不是默认的 403
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Dependency to get the current authenticated user.

    Decodes the JWT token from the Authorization header and
    fetches the corresponding user from the database.

    Args:
        credentials: Bearer token from Authorization header (may be None if not provided)
        session: Database session

    Returns:
        User entity

    Raises:
        HTTPException: 401 if token is missing, invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Handle missing credentials (return 401, not 403)
    if credentials is None:
        raise credentials_exception

    # Extract token from credentials
    token = credentials.credentials

    # Decode token and get user ID
    user_id_str = get_token_subject(token)
    if user_id_str is None:
        raise credentials_exception

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception

    # Fetch user from database
    repository = UserRepository(session)
    user = await repository.get_by_id(user_id)

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Dependency to get the current active user.
    
    Same as get_current_user but explicitly checks is_active flag.
    Use this when you need guaranteed active user access.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return current_user
