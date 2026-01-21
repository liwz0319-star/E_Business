"""
User Domain Entity

Represents the core User entity in the domain layer.
This is a pure Python class with no external dependencies.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class User:
    """
    User domain entity.
    
    Represents a user in the system with authentication credentials.
    This is used across all layers for user-related operations.
    """
    
    id: UUID
    email: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    @classmethod
    def create(
        cls,
        email: str,
        hashed_password: str,
        user_id: Optional[UUID] = None,
    ) -> "User":
        """
        Factory method to create a new User entity.
        
        Args:
            email: User's email address
            hashed_password: Bcrypt hashed password
            user_id: Optional UUID, generated if not provided
            
        Returns:
            New User instance
        """
        now = datetime.utcnow()
        return cls(
            id=user_id or uuid4(),
            email=email,
            hashed_password=hashed_password,
            created_at=now,
            updated_at=now,
            is_active=True,
        )
    
    def update_password(self, new_hashed_password: str) -> None:
        """Update user's password hash and timestamp."""
        self.hashed_password = new_hashed_password
        self.updated_at = datetime.utcnow()
    
    def deactivate(self) -> None:
        """Deactivate the user account."""
        self.is_active = False
        self.updated_at = datetime.utcnow()
