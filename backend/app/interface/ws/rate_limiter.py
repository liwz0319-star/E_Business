"""
Rate Limiter for Socket.IO Connections

Simple in-memory rate limiter to prevent connection abuse.
"""

import time
from collections import defaultdict
from typing import Dict, List, Tuple

import logging

logger = logging.getLogger(__name__)


class ConnectionRateLimiter:
    """
    Simple in-memory rate limiter for Socket.IO connections.
    
    Tracks connection attempts per IP address and rejects connections
    that exceed the configured rate limit.
    
    Attributes:
        max_connections: Maximum connections allowed per time window
        window_seconds: Time window in seconds
    """
    
    def __init__(self, max_connections: int = 10, window_seconds: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            max_connections: Maximum connections allowed per time window (default: 10)
            window_seconds: Time window in seconds (default: 60)
        """
        self.max_connections = max_connections
        self.window_seconds = window_seconds
        
        # Store connection timestamps per IP: {ip: [timestamp1, timestamp2, ...]}
        self._connection_attempts: Dict[str, List[float]] = defaultdict(list)
    
    def _cleanup_old_entries(self, ip: str, current_time: float) -> None:
        """Remove entries older than the time window."""
        cutoff = current_time - self.window_seconds
        self._connection_attempts[ip] = [
            ts for ts in self._connection_attempts[ip] if ts > cutoff
        ]
        
        # Remove empty entries to prevent memory leaks
        if not self._connection_attempts[ip]:
            del self._connection_attempts[ip]
    
    def is_rate_limited(self, ip: str) -> Tuple[bool, int]:
        """
        Check if an IP is rate limited.
        
        Args:
            ip: Client IP address
            
        Returns:
            Tuple of (is_limited, remaining_connections)
        """
        current_time = time.time()
        self._cleanup_old_entries(ip, current_time)
        
        attempts = self._connection_attempts.get(ip, [])
        remaining = self.max_connections - len(attempts)
        
        return (remaining <= 0, max(0, remaining))
    
    def record_connection(self, ip: str) -> bool:
        """
        Record a connection attempt and check if it's allowed.
        
        Args:
            ip: Client IP address
            
        Returns:
            True if connection is allowed, False if rate limited
        """
        current_time = time.time()
        self._cleanup_old_entries(ip, current_time)
        
        attempts = self._connection_attempts.get(ip, [])
        
        if len(attempts) >= self.max_connections:
            logger.warning(f"Rate limit exceeded for IP: {ip}")
            return False
        
        self._connection_attempts[ip].append(current_time)
        return True
    
    def get_retry_after(self, ip: str) -> int:
        """
        Get the number of seconds until rate limit resets.
        
        Args:
            ip: Client IP address
            
        Returns:
            Seconds until oldest entry expires (0 if not rate limited)
        """
        current_time = time.time()
        attempts = self._connection_attempts.get(ip, [])
        
        if not attempts:
            return 0
        
        oldest = min(attempts)
        retry_after = max(0, int(oldest + self.window_seconds - current_time))
        return retry_after
    
    def reset(self, ip: str = None) -> None:
        """
        Reset rate limit tracking.
        
        Args:
            ip: Optional IP to reset. If None, resets all.
        """
        if ip:
            self._connection_attempts.pop(ip, None)
        else:
            self._connection_attempts.clear()


# Default rate limiter instance
# 10 connections per 60 seconds per IP
connection_rate_limiter = ConnectionRateLimiter(max_connections=10, window_seconds=60)
