"""
HTTP Client Unit Tests.

Tests for BaseHTTPClient including SSE streaming support.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.http_client import BaseHTTPClient
from app.domain.exceptions import HTTPClientError


class AsyncIteratorMock:
    """Helper class to create async iterators from lists."""
    
    def __init__(self, items):
        self.items = items
        self.index = 0
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.index >= len(self.items):
            raise StopAsyncIteration
        item = self.items[self.index]
        self.index += 1
        return item


class TestBaseHTTPClientStreamSSE:
    """Tests for stream_sse method."""

    @pytest.mark.asyncio
    async def test_stream_sse_parses_json_chunks(self):
        """Test that stream_sse correctly parses SSE JSON chunks."""
        sse_lines = [
            b'data: {"choices":[{"delta":{"content":"Hello"}}]}\n',
            b'data: {"choices":[{"delta":{"content":" World"}}]}\n',
            b'data: [DONE]\n',
        ]
        
        mock_response = MagicMock()
        mock_response.content = AsyncIteratorMock(sse_lines)
        mock_response.raise_for_status = MagicMock()
        
        async with BaseHTTPClient(base_url="https://api.test.com") as client:
            with patch.object(client._session, 'request') as mock_request:
                mock_cm = AsyncMock()
                mock_cm.__aenter__.return_value = mock_response
                mock_cm.__aexit__.return_value = None
                mock_request.return_value = mock_cm
                
                chunks = []
                async for chunk in client.stream_sse("POST", "/v1/chat", json={"test": True}):
                    chunks.append(chunk)
                
                assert len(chunks) == 2
                assert chunks[0]["choices"][0]["delta"]["content"] == "Hello"
                assert chunks[1]["choices"][0]["delta"]["content"] == " World"

    @pytest.mark.asyncio
    async def test_stream_sse_handles_done_sentinel(self):
        """Test that stream_sse stops on [DONE] sentinel."""
        sse_lines = [
            b'data: {"content":"first"}\n',
            b'data: [DONE]\n',
            b'data: {"content":"should not appear"}\n',
        ]
        
        mock_response = MagicMock()
        mock_response.content = AsyncIteratorMock(sse_lines)
        mock_response.raise_for_status = MagicMock()
        
        async with BaseHTTPClient(base_url="https://api.test.com") as client:
            with patch.object(client._session, 'request') as mock_request:
                mock_cm = AsyncMock()
                mock_cm.__aenter__.return_value = mock_response
                mock_cm.__aexit__.return_value = None
                mock_request.return_value = mock_cm
                
                chunks = []
                async for chunk in client.stream_sse("POST", "/v1/chat"):
                    chunks.append(chunk)
                
                assert len(chunks) == 1
                assert chunks[0]["content"] == "first"

    @pytest.mark.asyncio
    async def test_stream_sse_skips_empty_lines(self):
        """Test that stream_sse skips empty lines."""
        sse_lines = [
            b'\n',
            b'data: {"content":"valid"}\n',
            b'\n',
            b'data: [DONE]\n',
        ]
        
        mock_response = MagicMock()
        mock_response.content = AsyncIteratorMock(sse_lines)
        mock_response.raise_for_status = MagicMock()
        
        async with BaseHTTPClient(base_url="https://api.test.com") as client:
            with patch.object(client._session, 'request') as mock_request:
                mock_cm = AsyncMock()
                mock_cm.__aenter__.return_value = mock_response
                mock_cm.__aexit__.return_value = None
                mock_request.return_value = mock_cm
                
                chunks = []
                async for chunk in client.stream_sse("POST", "/v1/chat"):
                    chunks.append(chunk)
                
                assert len(chunks) == 1
                assert chunks[0]["content"] == "valid"

    @pytest.mark.asyncio
    async def test_stream_sse_handles_malformed_json(self):
        """Test that stream_sse logs warning for malformed JSON and continues."""
        sse_lines = [
            b'data: {"valid":"json"}\n',
            b'data: {invalid json}\n',
            b'data: {"also":"valid"}\n',
            b'data: [DONE]\n',
        ]
        
        mock_response = MagicMock()
        mock_response.content = AsyncIteratorMock(sse_lines)
        mock_response.raise_for_status = MagicMock()
        
        async with BaseHTTPClient(base_url="https://api.test.com") as client:
            with patch.object(client._session, 'request') as mock_request:
                mock_cm = AsyncMock()
                mock_cm.__aenter__.return_value = mock_response
                mock_cm.__aexit__.return_value = None
                mock_request.return_value = mock_cm
                
                chunks = []
                async for chunk in client.stream_sse("POST", "/v1/chat"):
                    chunks.append(chunk)
                
                assert len(chunks) == 2
                assert chunks[0]["valid"] == "json"
                assert chunks[1]["also"] == "valid"

    @pytest.mark.asyncio
    async def test_stream_sse_raises_on_http_error(self):
        """Test that stream_sse raises HTTPClientError on HTTP errors."""
        import aiohttp
        
        async with BaseHTTPClient(base_url="https://api.test.com") as client:
            with patch.object(client._session, 'request') as mock_request:
                mock_response = MagicMock()
                mock_response.raise_for_status.side_effect = aiohttp.ClientResponseError(
                    request_info=MagicMock(),
                    history=(),
                    status=401,
                    message="Unauthorized"
                )
                
                mock_cm = AsyncMock()
                mock_cm.__aenter__.return_value = mock_response
                mock_cm.__aexit__.return_value = None
                mock_request.return_value = mock_cm
                
                with pytest.raises(HTTPClientError):
                    async for _ in client.stream_sse("POST", "/v1/chat"):
                        pass

    @pytest.mark.asyncio
    async def test_stream_sse_auto_initializes_session(self):
        """Test that stream_sse auto-initializes session if not in context manager."""
        sse_lines = [
            b'data: {"content":"auto-init"}\n',
            b'data: [DONE]\n',
        ]
        
        client = BaseHTTPClient(base_url="https://api.test.com")
        
        mock_response = MagicMock()
        mock_response.content = AsyncIteratorMock(sse_lines)
        mock_response.raise_for_status = MagicMock()
        
        with patch('aiohttp.ClientSession') as MockSession:
            mock_session = MagicMock()
            MockSession.return_value = mock_session
            
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = mock_response
            mock_cm.__aexit__.return_value = None
            mock_session.request.return_value = mock_cm
            
            chunks = []
            async for chunk in client.stream_sse("POST", "/v1/chat"):
                chunks.append(chunk)
            
            assert len(chunks) == 1
            assert chunks[0]["content"] == "auto-init"
