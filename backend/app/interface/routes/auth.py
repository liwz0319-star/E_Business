"""
Auth API Routes

Authentication endpoints for user registration and login.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
from pydantic.alias_generators import to_camel
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.auth import (
    LoginUserUseCase,
    RegisterUserUseCase,
)
from app.core.config import settings
from app.infrastructure.database import get_async_session
from app.infrastructure.repositories.user_repository import UserRepository
from app.interface.dependencies.auth import get_current_user


router = APIRouter(prefix="/auth", tags=["auth"])


class UserRegisterRequest(BaseModel):
    """Request schema for user registration."""
    email: EmailStr
    password: str
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets strength requirements."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }
    )


class UserLoginRequest(BaseModel):
    """Request schema for user login."""
    email: EmailStr
    password: str
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }
    )


class TokenResponse(BaseModel):
    """Response schema for token endpoints."""
    access_token: str
    token_type: str = "bearer"
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )


class UserResponse(BaseModel):
    """Response schema for user data."""
    id: str
    email: str
    is_active: bool
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True
    )


class RegisterResponse(BaseModel):
    """Response schema for registration."""
    message: str
    user: UserResponse
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
async def register(
    request: UserRegisterRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Register a new user account.
    
    - **email**: User's email address (must be unique)
    - **password**: User's password (will be hashed)
    """
    repository = UserRepository(session)
    use_case = RegisterUserUseCase(repository)
    
    result = await use_case.execute(request.email, request.password)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.error,
        )
    
    return RegisterResponse(
        message="User registered successfully",
        user=UserResponse(
            id=str(result.user.id),
            email=result.user.email,
            is_active=result.user.is_active,
        ),
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and get access token",
)
async def login(
    request: UserLoginRequest,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Authenticate user and return JWT access token.
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns a Bearer token for API authentication.
    """
    repository = UserRepository(session)
    use_case = LoginUserUseCase(
        repository,
        token_expire_minutes=settings.access_token_expire_minutes,
    )
    
    result = await use_case.execute(request.email, request.password)
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.error,
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return TokenResponse(
        access_token=result.token.access_token,
        token_type=result.token.token_type,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user info",
)
async def get_current_user_info(
    current_user = Depends(get_current_user),
):
    """
    Get the current authenticated user's information.
    
    Requires valid JWT Bearer token in Authorization header.
    This endpoint validates AC 4: get_current_user correctly decodes the token.
    """
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        is_active=current_user.is_active,
    )
