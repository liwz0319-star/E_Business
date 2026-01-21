"""
User Repository Implementation

SQLAlchemy-based implementation of the User repository interface.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.interfaces.user_repository import IUserRepository
from app.infrastructure.database.models import UserModel


class UserRepository(IUserRepository):
    """
    SQLAlchemy implementation of IUserRepository.
    
    Handles user data persistence using async SQLAlchemy.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session: Async SQLAlchemy session
        """
        self._session = session
    
    def _model_to_entity(self, model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        return User(
            id=model.id,
            email=model.email,
            hashed_password=model.hashed_password,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_active=model.is_active,
        )
    
    def _entity_to_model(self, entity: User) -> UserModel:
        """Convert domain entity to SQLAlchemy model."""
        return UserModel(
            id=entity.id,
            email=entity.email,
            hashed_password=entity.hashed_password,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_active=entity.is_active,
        )
    
    async def create(self, user: User) -> User:
        """
        Create a new user in the database.
        
        Args:
            user: User entity to persist
            
        Returns:
            Created User entity
            
        Note:
            Email uniqueness should be checked at UseCase layer for better error messages.
            Database constraint will catch race conditions.
        """
        model = self._entity_to_model(user)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        
        return self._model_to_entity(model)
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user by their unique ID.
        
        Args:
            user_id: The user's UUID
            
        Returns:
            User entity if found, None otherwise
        """
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        
        if model is None:
            return None
        
        return self._model_to_entity(model)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.
        
        Args:
            email: The user's email address
            
        Returns:
            User entity if found, None otherwise
        """
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        
        if model is None:
            return None
        
        return self._model_to_entity(model)
    
    async def update(self, user: User) -> User:
        """
        Update an existing user.
        
        Args:
            user: User entity with updated fields
            
        Returns:
            Updated User entity
            
        Raises:
            ValueError: If user does not exist
        """
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        model = result.scalar_one_or_none()
        
        if model is None:
            raise ValueError(f"User with id {user.id} does not exist")
        
        model.email = user.email
        model.hashed_password = user.hashed_password
        model.is_active = user.is_active
        model.updated_at = user.updated_at
        
        await self._session.flush()
        await self._session.refresh(model)
        
        return self._model_to_entity(model)
    
    async def delete(self, user_id: UUID) -> bool:
        """
        Delete a user by their ID.
        
        Args:
            user_id: The user's UUID
            
        Returns:
            True if deleted, False if user not found
        """
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        
        if model is None:
            return False
        
        await self._session.delete(model)
        await self._session.flush()
        
        return True
