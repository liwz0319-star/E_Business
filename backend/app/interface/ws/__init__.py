"""
Socket.IO WebSocket Interface Package

Provides real-time WebSocket communication for agent events.
"""

from app.interface.ws.socket_manager import socket_manager, SocketManager
from app.interface.ws.rate_limiter import connection_rate_limiter, ConnectionRateLimiter

__all__ = ["socket_manager", "SocketManager", "connection_rate_limiter", "ConnectionRateLimiter"]

