"""
Socket.IO End-to-End Tests

Real Socket.IO client tests that connect to an actual server.
Tests AC: 1, 2 from Story 1.3 with real connections.
"""

import asyncio
from datetime import timedelta

import pytest
import socketio

from app.core.security import create_access_token


class TestSocketIOE2E:
    """
    End-to-end tests for Socket.IO with real connections.
    
    These tests start a real ASGI server and connect to it using
    a real Socket.IO client.
    """
    
    @pytest.fixture
    def valid_token(self):
        """Create a valid JWT token for testing."""
        return create_access_token(data={"sub": "test-user-e2e-123"})
    
    @pytest.fixture
    def expired_token(self):
        """Create an expired JWT token for testing."""
        return create_access_token(
            data={"sub": "test-user-e2e-123"},
            expires_delta=timedelta(seconds=-10)
        )
    
    @pytest.fixture
    def socket_client(self):
        """Create an async Socket.IO client."""
        return socketio.AsyncClient(
            reconnection=False,
            logger=False,
            engineio_logger=False,
        )
    
    @pytest.fixture
    async def server_url(self):
        """
        Start a test server and return its URL.
        
        Uses uvicorn to run the actual FastAPI app with Socket.IO.
        """
        import uvicorn
        from app.main import app
        
        config = uvicorn.Config(
            app,
            host="127.0.0.1",
            port=0,  # Random available port
            log_level="error",
        )
        server = uvicorn.Server(config)
        
        # Start server in background
        task = asyncio.create_task(server.serve())
        
        # Wait for server to start and get the actual port
        await asyncio.sleep(0.5)
        
        # Get the actual port from the server
        if server.servers:
            for srv in server.servers:
                for sock in srv.sockets:
                    addr = sock.getsockname()
                    port = addr[1]
                    yield f"http://127.0.0.1:{port}"
                    break
                break
        
        # Cleanup
        server.should_exit = True
        await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
    
    @pytest.mark.asyncio
    async def test_connect_with_valid_jwt(self, socket_client, valid_token, server_url):
        """
        AC 1: Given a running API server
             When a client connects to /ws with a valid JWT in the handshake auth
             Then the connection is accepted and the socket ID is logged
        """
        connected = False
        
        @socket_client.event
        async def connect():
            nonlocal connected
            connected = True
        
        try:
            await socket_client.connect(
                f"{server_url}/ws",
                auth={"token": valid_token},
                wait_timeout=5,
            )
            
            assert connected, "Should have connected successfully"
            assert socket_client.connected, "Client should be connected"
            
        finally:
            if socket_client.connected:
                await socket_client.disconnect()
    
    @pytest.mark.asyncio
    async def test_connection_rejected_without_token(self, socket_client, server_url):
        """
        AC 2: Given a running API server
             When a client connects to /ws without a token
             Then the connection is rejected (401)
        """
        with pytest.raises(socketio.exceptions.ConnectionError):
            await socket_client.connect(
                f"{server_url}/ws",
                auth=None,  # No token
                wait_timeout=5,
            )
    
    @pytest.mark.asyncio
    async def test_connection_rejected_without_auth_object(self, socket_client, server_url):
        """
        AC 2: Connection rejected when no auth object provided.
        """
        with pytest.raises(socketio.exceptions.ConnectionError):
            await socket_client.connect(
                f"{server_url}/ws",
                wait_timeout=5,
            )
    
    @pytest.mark.asyncio
    async def test_connection_rejected_with_invalid_token(self, socket_client, server_url):
        """
        AC 2: Connection rejected with invalid token.
        """
        with pytest.raises(socketio.exceptions.ConnectionError):
            await socket_client.connect(
                f"{server_url}/ws",
                auth={"token": "invalid.token.here"},
                wait_timeout=5,
            )
    
    @pytest.mark.asyncio
    async def test_connection_rejected_with_expired_token(self, socket_client, expired_token, server_url):
        """
        AC 2: Connection rejected with expired token.
        """
        with pytest.raises(socketio.exceptions.ConnectionError):
            await socket_client.connect(
                f"{server_url}/ws",
                auth={"token": expired_token},
                wait_timeout=5,
            )


class TestSocketIOEventEmission:
    """
    E2E tests for Socket.IO event emission.
    
    Tests that events are properly received by connected clients.
    """
    
    @pytest.fixture
    def valid_token(self):
        """Create a valid JWT token for testing."""
        return create_access_token(data={"sub": "test-user-event-123"})
    
    @pytest.fixture
    def socket_client(self):
        """Create an async Socket.IO client."""
        return socketio.AsyncClient(
            reconnection=False,
            logger=False,
            engineio_logger=False,
        )
    
    @pytest.fixture
    async def connected_client(self, socket_client, valid_token):
        """
        Return a connected Socket.IO client.
        
        Note: This requires a running server. In most CI environments,
        you would use a separate test server or mock.
        """
        # For now, this is a placeholder - actual E2E tests would need
        # a real server running.
        yield socket_client
    
    @pytest.mark.asyncio
    async def test_receive_thought_event(self, connected_client):
        """
        Test that client receives agent:thought events.
        
        Note: This test is a placeholder for full E2E event testing.
        Real implementation would require a running server and event emission.
        """
        # Placeholder - actual implementation would:
        # 1. Connect to server
        # 2. Trigger event emission (via API call)
        # 3. Verify event received
        pass
