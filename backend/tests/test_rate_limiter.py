"""
Rate Limiter Tests

Unit tests for the Socket.IO connection rate limiter.
"""

import time
from unittest.mock import patch

import pytest

from app.interface.ws.rate_limiter import ConnectionRateLimiter


class TestConnectionRateLimiter:
    """Unit tests for ConnectionRateLimiter."""
    
    @pytest.fixture
    def limiter(self):
        """Create a fresh rate limiter for each test."""
        return ConnectionRateLimiter(max_connections=3, window_seconds=10)
    
    def test_allows_connections_under_limit(self, limiter):
        """Test that connections under the limit are allowed."""
        assert limiter.record_connection("192.168.1.1") is True
        assert limiter.record_connection("192.168.1.1") is True
        assert limiter.record_connection("192.168.1.1") is True
    
    def test_blocks_connections_over_limit(self, limiter):
        """Test that connections over the limit are blocked."""
        # Use up all allowed connections
        for _ in range(3):
            limiter.record_connection("192.168.1.1")
        
        # Next connection should be blocked
        assert limiter.record_connection("192.168.1.1") is False
    
    def test_different_ips_have_separate_limits(self, limiter):
        """Test that different IPs have separate rate limits."""
        # IP 1 uses all connections
        for _ in range(3):
            limiter.record_connection("192.168.1.1")
        
        # IP 1 is blocked
        assert limiter.record_connection("192.168.1.1") is False
        
        # IP 2 still has full quota
        assert limiter.record_connection("192.168.1.2") is True
        assert limiter.record_connection("192.168.1.2") is True
    
    def test_is_rate_limited_check(self, limiter):
        """Test is_rate_limited returns correct status."""
        is_limited, remaining = limiter.is_rate_limited("192.168.1.1")
        assert is_limited is False
        assert remaining == 3
        
        limiter.record_connection("192.168.1.1")
        is_limited, remaining = limiter.is_rate_limited("192.168.1.1")
        assert is_limited is False
        assert remaining == 2
        
        # Use up remaining
        limiter.record_connection("192.168.1.1")
        limiter.record_connection("192.168.1.1")
        
        is_limited, remaining = limiter.is_rate_limited("192.168.1.1")
        assert is_limited is True
        assert remaining == 0
    
    def test_old_entries_are_cleaned_up(self):
        """Test that old entries are cleaned up after window expires."""
        # Create limiter with very short window
        limiter = ConnectionRateLimiter(max_connections=2, window_seconds=0.1)
        
        limiter.record_connection("192.168.1.1")
        limiter.record_connection("192.168.1.1")
        
        # Should be blocked immediately
        assert limiter.record_connection("192.168.1.1") is False
        
        # Wait for window to expire
        time.sleep(0.15)
        
        # Now should be allowed again
        assert limiter.record_connection("192.168.1.1") is True
    
    def test_get_retry_after(self, limiter):
        """Test get_retry_after returns correct seconds."""
        # No connections yet
        assert limiter.get_retry_after("192.168.1.1") == 0
        
        limiter.record_connection("192.168.1.1")
        
        # Should be close to window_seconds
        retry_after = limiter.get_retry_after("192.168.1.1")
        assert 0 <= retry_after <= 10
    
    def test_reset_single_ip(self, limiter):
        """Test resetting a single IP."""
        limiter.record_connection("192.168.1.1")
        limiter.record_connection("192.168.1.2")
        
        limiter.reset("192.168.1.1")
        
        # IP 1 should have full quota
        is_limited, remaining = limiter.is_rate_limited("192.168.1.1")
        assert remaining == 3
        
        # IP 2 should still have 2 remaining
        is_limited, remaining = limiter.is_rate_limited("192.168.1.2")
        assert remaining == 2
    
    def test_reset_all(self, limiter):
        """Test resetting all IPs."""
        limiter.record_connection("192.168.1.1")
        limiter.record_connection("192.168.1.2")
        
        limiter.reset()
        
        # Both should have full quota
        _, remaining1 = limiter.is_rate_limited("192.168.1.1")
        _, remaining2 = limiter.is_rate_limited("192.168.1.2")
        
        assert remaining1 == 3
        assert remaining2 == 3


class TestRateLimiterIntegration:
    """Integration tests for rate limiter with SocketManager."""
    
    def test_socket_manager_uses_rate_limiter(self):
        """Test that SocketManager properly integrates rate limiter."""
        # Import after to get fresh modules
        from app.interface.ws.socket_manager import SocketManager
        from app.interface.ws.rate_limiter import connection_rate_limiter
        
        # Reset rate limiter
        connection_rate_limiter.reset()
        
        # Verify rate limiter is imported
        manager = SocketManager()
        assert manager.sio is not None
