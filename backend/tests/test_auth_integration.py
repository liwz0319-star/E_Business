"""
Auth Integration Tests

Tests the complete authentication flow:
- Register → Login → Access Protected Endpoint
- Invalid credentials return 401
- Expired/invalid tokens return 401
"""

from datetime import timedelta

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token


class TestAuthIntegrationFlow:
    """Integration tests for complete auth flow (AC 2-5)."""

    @pytest.mark.asyncio
    async def test_register_login_access_protected_flow(self, async_client: AsyncClient):
        """
        Test complete register → login → access protected endpoint flow.
        
        AC 2: POST /auth/register creates user with hashed password
        AC 3: POST /auth/login returns JWT Bearer token
        AC 4: get_current_user correctly decodes the token
        """
        # Step 1: Register a new user (AC 2)
        register_data = {
            "email": "testuser@example.com",
            "password": "SecurePassword123!"
        }
        register_response = await async_client.post("/auth/register", json=register_data)
        
        assert register_response.status_code == 201
        register_json = register_response.json()
        assert register_json["message"] == "User registered successfully"
        assert register_json["user"]["email"] == register_data["email"]
        assert register_json["user"]["isActive"] is True
        assert "id" in register_json["user"]
        
        # Step 2: Login with the registered user (AC 3)
        login_data = {
            "email": "testuser@example.com",
            "password": "SecurePassword123!"
        }
        login_response = await async_client.post("/auth/login", json=login_data)
        
        assert login_response.status_code == 200
        login_json = login_response.json()
        assert "accessToken" in login_json
        assert login_json["tokenType"] == "bearer"
        access_token = login_json["accessToken"]
        
        # Step 3: Access protected endpoint /auth/me (AC 4)
        headers = {"Authorization": f"Bearer {access_token}"}
        me_response = await async_client.get("/auth/me", headers=headers)
        
        assert me_response.status_code == 200
        me_json = me_response.json()
        assert me_json["email"] == register_data["email"]
        assert me_json["isActive"] is True
        assert "id" in me_json

    @pytest.mark.asyncio
    async def test_login_with_invalid_credentials_returns_401(self, async_client: AsyncClient):
        """
        Test that invalid credentials return proper 401 Unauthorized error.
        
        AC 5: Invalid credentials return proper 401 Unauthorized error
        """
        # First register a user
        register_data = {
            "email": "validuser@example.com",
            "password": "CorrectPassword123!"
        }
        await async_client.post("/auth/register", json=register_data)
        
        # Try to login with wrong password
        login_data = {
            "email": "validuser@example.com",
            "password": "WrongPassword456!"
        }
        response = await async_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == "Bearer"

    @pytest.mark.asyncio
    async def test_login_with_nonexistent_user_returns_401(self, async_client: AsyncClient):
        """
        Test that login with non-existent email returns 401.
        
        AC 5: Invalid credentials return proper 401 Unauthorized error
        """
        login_data = {
            "email": "nonexistent@example.com",
            "password": "SomePassword123!"
        }
        response = await async_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers

    @pytest.mark.asyncio
    async def test_invalid_token_returns_401(self, async_client: AsyncClient):
        """
        Test that invalid token returns 401 when accessing protected resources.
        
        AC 5: Invalid/expired tokens return proper 401 Unauthorized error
        """
        # Create a request with an invalid token
        headers = {"Authorization": "Bearer invalid.token.string"}
        
        # Access protected endpoint /auth/me with invalid token
        response = await async_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == "Bearer"

    @pytest.mark.asyncio
    async def test_expired_token_returns_401(self, async_client: AsyncClient):
        """
        Test that expired token returns 401.
        
        AC 5: Invalid/expired tokens return proper 401 Unauthorized error
        """
        # Create a token that's already expired
        expired_token = create_access_token(
            data={"sub": "some-user-id"},
            expires_delta=timedelta(seconds=-10)  # Already expired
        )
        
        # Access protected endpoint /auth/me with expired token
        headers = {"Authorization": f"Bearer {expired_token}"}
        response = await async_client.get("/auth/me", headers=headers)
        
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers


class TestAuthEndpointValidation:
    """Tests for auth endpoint input validation."""

    @pytest.mark.asyncio
    async def test_register_duplicate_email_returns_400(self, async_client: AsyncClient):
        """Test that registering with existing email returns 400."""
        register_data = {
            "email": "duplicate@example.com",
            "password": "Password123!"
        }
        
        # First registration should succeed
        response1 = await async_client.post("/auth/register", json=register_data)
        assert response1.status_code == 201
        
        # Second registration with same email should fail
        response2 = await async_client.post("/auth/register", json=register_data)
        assert response2.status_code == 400
        assert "already" in response2.json()["detail"].lower()

    @pytest.mark.asyncio
    async def test_register_invalid_email_format(self, async_client: AsyncClient):
        """Test that invalid email format is rejected."""
        register_data = {
            "email": "not-an-email",
            "password": "Password123!"
        }
        
        response = await async_client.post("/auth/register", json=register_data)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_login_invalid_email_format(self, async_client: AsyncClient):
        """Test that invalid email format is rejected for login."""
        login_data = {
            "email": "not-an-email",
            "password": "Password123!"
        }
        
        response = await async_client.post("/auth/login", json=login_data)
        assert response.status_code == 422  # Validation error
