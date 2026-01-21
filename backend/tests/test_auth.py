"""
Auth Unit Tests

Tests for authentication functionality.
"""

import pytest
from app.core.security import (
    create_access_token,
    decode_access_token,
    get_password_hash,
    get_token_subject,
    verify_password,
)


class TestPasswordHashing:
    """Tests for password hashing functions."""
    
    def test_hash_password(self):
        """Test that password hashing produces valid hash."""
        password = "securepassword123"
        hashed = get_password_hash(password)
        
        assert hashed != password
        assert hashed.startswith("$5$")  # sha256_crypt prefix
        assert len(hashed) > 50  # Ensure hash has reasonable length
    
    def test_verify_correct_password(self):
        """Test that correct password verifies successfully."""
        password = "securepassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_wrong_password(self):
        """Test that wrong password fails verification."""
        password = "securepassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_different_passwords_different_hashes(self):
        """Test that different passwords produce different hashes."""
        hash1 = get_password_hash("password1")
        hash2 = get_password_hash("password2")
        
        assert hash1 != hash2


class TestJWT:
    """Tests for JWT token functions."""
    
    def test_create_access_token(self):
        """Test creating access token."""
        data = {"sub": "user-123"}
        token = create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        user_id = "user-123"
        data = {"sub": user_id}
        token = create_access_token(data)
        
        payload = decode_access_token(token)
        
        assert payload is not None
        assert payload["sub"] == user_id
    
    def test_decode_invalid_token(self):
        """Test that invalid token returns None."""
        invalid_token = "invalid.token.string"
        
        payload = decode_access_token(invalid_token)
        
        assert payload is None
    
    def test_get_token_subject(self):
        """Test extracting subject from token."""
        user_id = "user-123"
        data = {"sub": user_id}
        token = create_access_token(data)
        
        subject = get_token_subject(token)
        
        assert subject == user_id
    
    def test_get_token_subject_invalid(self):
        """Test that invalid token returns None for subject."""
        invalid_token = "invalid.token.string"
        
        subject = get_token_subject(invalid_token)
        
        assert subject is None
