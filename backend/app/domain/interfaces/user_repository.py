"""
User Repository Interface

Defines the contract for user data access operations.
Implementations should handle the actual database operations.
"""

from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from app.domain.entities.user import User


class IUserRepository(ABC):
    """
    Interface for User repository operations.
    
    This defines the contract that infrastructure layer implementations
    must fulfill. It allows the application layer to work with user data
    without knowing the specific storage mechanism.
    """
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """
        Create a new user in the repository.
        
        Args:
            user: User entity to persist
            
        Returns:
            Created User entity with any updates (e.g., generated ID)
            
        Raises:
            ValueError: If user with email already exists
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """
        Retrieve a user by their unique ID.
        
        Args:
            user_id: The user's UUID
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user by their email address.
        
        Args:
            email: The user's email address
            
        Returns:
            User entity if found, None otherwise
        """
        pass
    
    @abstractmethod
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
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """
        Delete a user by their ID.
        
        Args:
            user_id: The user's UUID
            
        Returns:
            True if deleted, False if user not found
        """
        pass
