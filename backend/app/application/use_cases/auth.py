"""
Auth Use Cases

Business logic for authentication operations.
"""

from dataclasses import dataclass
from datetime import timedelta
from typing import Optional

from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.domain.entities.user import User
from app.domain.interfaces.user_repository import IUserRepository


@dataclass
class TokenResponse:
    """Response containing access token."""
    access_token: str
    token_type: str = "bearer"


@dataclass
class AuthResult:
    """Result of authentication operation."""
    success: bool
    user: Optional[User] = None
    token: Optional[TokenResponse] = None
    error: Optional[str] = None


class RegisterUserUseCase:
    """
    Use case for registering a new user.
    """
    
    def __init__(self, user_repository: IUserRepository):
        self._user_repository = user_repository
    
    async def execute(self, email: str, password: str) -> AuthResult:
        """
        Register a new user.
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            AuthResult with success status and user/error
        """
        # Check if user already exists
        existing = await self._user_repository.get_by_email(email)
        if existing:
            return AuthResult(
                success=False,
                error="User with this email already exists"
            )
        
        # Hash password and create user
        hashed_password = get_password_hash(password)
        user = User.create(email=email, hashed_password=hashed_password)
        
        try:
            created_user = await self._user_repository.create(user)
            return AuthResult(success=True, user=created_user)
        except Exception as e:
            return AuthResult(success=False, error=str(e))


class LoginUserUseCase:
    """
    Use case for user login/authentication.
    """
    
    def __init__(
        self,
        user_repository: IUserRepository,
        token_expire_minutes: int = 30,
    ):
        self._user_repository = user_repository
        self._token_expire_minutes = token_expire_minutes
    
    async def execute(self, email: str, password: str) -> AuthResult:
        """
        Authenticate user and generate JWT token.
        
        Args:
            email: User's email address
            password: Plain text password
            
        Returns:
            AuthResult with success status and token/error
        """
        # Find user by email
        user = await self._user_repository.get_by_email(email)
        if user is None:
            return AuthResult(
                success=False,
                error="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(password, user.hashed_password):
            return AuthResult(
                success=False,
                error="Invalid email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            return AuthResult(
                success=False,
                error="User account is deactivated"
            )
        
        # Generate access token
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=self._token_expire_minutes),
        )
        
        return AuthResult(
            success=True,
            user=user,
            token=TokenResponse(access_token=access_token),
        )
