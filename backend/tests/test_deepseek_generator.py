"""
DeepSeek Generator Unit Tests.

Tests for DeepSeekGenerator including sync/stream generation,
error handling, and configuration.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.domain.entities.generation import GenerationRequest, GenerationResult, StreamChunk
from app.domain.exceptions import HTTPClientError
from app.infrastructure.generators.deepseek import DeepSeekGenerator


class TestDeepSeekGeneratorInit:
    """Tests for DeepSeekGenerator initialization."""

    def test_init_with_api_key(self):
        """Test initialization with explicit API key."""
        generator = DeepSeekGenerator(api_key="test-key")
        assert generator.api_key == "test-key"

    def test_init_without_api_key_raises(self, monkeypatch):
        """Test that missing API key raises ValueError."""
        monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
        with patch("app.infrastructure.generators.deepseek.settings") as mock_settings:
            mock_settings.deepseek_api_key = None
            with pytest.raises(ValueError, match="API key is required"):
                DeepSeekGenerator()

    def test_init_with_custom_model(self):
        """Test initialization with custom model."""
        generator = DeepSeekGenerator(api_key="test-key", model="custom-model")
        assert generator.model == "custom-model"

    def test_init_with_custom_max_tokens(self):
        """Test initialization with custom max_tokens."""
        generator = DeepSeekGenerator(api_key="test-key", max_tokens=4000)
        assert generator.max_tokens == 4000

    def test_init_with_custom_timeout(self):
        """Test initialization with custom timeout."""
        generator = DeepSeekGenerator(api_key="test-key", timeout=60)
        assert generator.timeout == 60


class TestDeepSeekGeneratorContextManager:
    """Tests for context manager behavior."""

    @pytest.mark.asyncio
    async def test_context_manager_initializes_client(self):
        """Test that context manager initializes HTTP client."""
        generator = DeepSeekGenerator(api_key="test-key")
        
        with patch("app.infrastructure.generators.deepseek.BaseHTTPClient") as MockClient:
            mock_client = AsyncMock()
            MockClient.return_value = mock_client
            
            async with generator:
                assert generator._client is not None
                mock_client.__aenter__.assert_called_once()

    @pytest.mark.asyncio
    async def test_context_manager_cleans_up(self):
        """Test that context manager cleans up resources."""
        generator = DeepSeekGenerator(api_key="test-key")
        
        with patch("app.infrastructure.generators.deepseek.BaseHTTPClient") as MockClient:
            mock_client = AsyncMock()
            MockClient.return_value = mock_client
            
            async with generator:
                pass
            
            mock_client.__aexit__.assert_called_once()


class TestDeepSeekGeneratorBuildPayload:
    """Tests for _build_payload method."""

    def test_build_payload_basic(self):
        """Test basic payload building."""
        generator = DeepSeekGenerator(api_key="test-key")
        request = GenerationRequest(
            prompt="Hello",
            model="deepseek-chat",
            temperature=0.7,
        )
        
        payload = generator._build_payload(request)
        
        assert payload["model"] == "deepseek-chat"
        assert payload["messages"][0]["content"] == "Hello"
        assert payload["temperature"] == 0.7
        assert payload["stream"] is False

    def test_build_payload_with_stream(self):
        """Test payload with streaming enabled."""
        generator = DeepSeekGenerator(api_key="test-key")
        request = GenerationRequest(prompt="Hello", model="deepseek-chat")
        
        payload = generator._build_payload(request, stream=True)
        
        assert payload["stream"] is True

    def test_build_payload_with_provider_config(self):
        """Test payload with provider-specific config."""
        generator = DeepSeekGenerator(api_key="test-key")
        request = GenerationRequest(
            prompt="Hello",
            model="deepseek-chat",
            provider_config={"top_p": 0.9, "presence_penalty": 0.5},
        )
        
        payload = generator._build_payload(request)
        
        assert payload["top_p"] == 0.9
        assert payload["presence_penalty"] == 0.5

    def test_build_payload_uses_request_max_tokens(self):
        """Test that request max_tokens overrides default."""
        generator = DeepSeekGenerator(api_key="test-key", max_tokens=2000)
        request = GenerationRequest(
            prompt="Hello",
            model="deepseek-chat",
            max_tokens=500,
        )
        
        payload = generator._build_payload(request)
        
        assert payload["max_tokens"] == 500


class TestDeepSeekGeneratorGenerate:
    """Tests for synchronous generate method."""

    @pytest.mark.asyncio
    async def test_generate_success(self):
        """Test successful generation."""
        generator = DeepSeekGenerator(api_key="test-key")
        request = GenerationRequest(prompt="Hello", model="deepseek-chat")
        
        mock_response = {
            "choices": [{"message": {"content": "Hello World"}}],
            "usage": {"prompt_tokens": 10, "completion_tokens": 5},
        }
        
        with patch("app.infrastructure.generators.deepseek.BaseHTTPClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.request.return_value = mock_response
            MockClient.return_value = mock_client
            
            async with generator:
                result = await generator.generate(request)
            
            assert isinstance(result, GenerationResult)
            assert result.content == "Hello World"
            assert result.usage == mock_response["usage"]

    @pytest.mark.asyncio
    async def test_generate_without_context_manager_raises(self):
        """Test that generate raises if not in context manager."""
        generator = DeepSeekGenerator(api_key="test-key")
        request = GenerationRequest(prompt="Hello", model="deepseek-chat")
        
        with pytest.raises(ValueError, match="not initialized"):
            await generator.generate(request)

    @pytest.mark.asyncio
    async def test_generate_http_error(self):
        """Test HTTP error handling in generate."""
        generator = DeepSeekGenerator(api_key="test-key")
        request = GenerationRequest(prompt="Hello", model="deepseek-chat")
        
        with patch("app.infrastructure.generators.deepseek.BaseHTTPClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.request.side_effect = HTTPClientError("HTTP 401: Unauthorized")
            MockClient.return_value = mock_client
            
            async with generator:
                with pytest.raises(HTTPClientError):
                    await generator.generate(request)


class TestDeepSeekGeneratorGenerateStream:
    """Tests for streaming generate_stream method."""

    @pytest.mark.asyncio
    async def test_generate_stream_success(self):
        """Test successful streaming generation."""
        generator = DeepSeekGenerator(api_key="test-key")
        request = GenerationRequest(prompt="Hello", model="deepseek-chat")
        
        async def mock_stream(*args, **kwargs):
            chunks = [
                {"choices": [{"delta": {"content": "Hello"}, "finish_reason": None}]},
                {"choices": [{"delta": {"content": " World"}, "finish_reason": None}]},
                {"choices": [{"delta": {}, "finish_reason": "stop"}]},
            ]
            for chunk in chunks:
                yield chunk
        
        with patch("app.infrastructure.generators.deepseek.BaseHTTPClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.stream_sse = mock_stream
            MockClient.return_value = mock_client
            
            async with generator:
                chunks = []
                async for chunk in generator.generate_stream(request):
                    chunks.append(chunk)
            
            assert len(chunks) == 3
            assert chunks[0].content == "Hello"
            assert chunks[1].content == " World"
            assert chunks[2].finish_reason == "stop"

    @pytest.mark.asyncio
    async def test_generate_stream_with_reasoning_content(self):
        """Test streaming with reasoning_content extraction."""
        generator = DeepSeekGenerator(api_key="test-key")
        request = GenerationRequest(prompt="Hello", model="deepseek-chat")
        
        async def mock_stream(*args, **kwargs):
            chunks = [
                {"choices": [{"delta": {"reasoning_content": "thinking..."}, "finish_reason": None}]},
                {"choices": [{"delta": {"content": "Answer"}, "finish_reason": "stop"}]},
            ]
            for chunk in chunks:
                yield chunk
        
        with patch("app.infrastructure.generators.deepseek.BaseHTTPClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.stream_sse = mock_stream
            MockClient.return_value = mock_client
            
            async with generator:
                chunks = []
                async for chunk in generator.generate_stream(request):
                    chunks.append(chunk)
            
            assert len(chunks) == 2
            assert chunks[0].reasoning_content == "thinking..."
            assert chunks[1].content == "Answer"

    @pytest.mark.asyncio
    async def test_generate_stream_without_context_manager_raises(self):
        """Test that generate_stream raises if not in context manager."""
        generator = DeepSeekGenerator(api_key="test-key")
        request = GenerationRequest(prompt="Hello", model="deepseek-chat")
        
        with pytest.raises(ValueError, match="not initialized"):
            async for _ in generator.generate_stream(request):
                pass

    @pytest.mark.asyncio
    async def test_generate_stream_http_error(self):
        """Test HTTP error handling in generate_stream."""
        generator = DeepSeekGenerator(api_key="test-key")
        request = GenerationRequest(prompt="Hello", model="deepseek-chat")
        
        async def mock_stream_error(*args, **kwargs):
            raise HTTPClientError("HTTP 429: Rate limit exceeded")
            yield  # Make it a generator
        
        with patch("app.infrastructure.generators.deepseek.BaseHTTPClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.stream_sse = mock_stream_error
            MockClient.return_value = mock_client
            
            async with generator:
                with pytest.raises(HTTPClientError):
                    async for _ in generator.generate_stream(request):
                        pass


class TestDeepSeekGeneratorIntegration:
    """Integration tests for ProviderFactory registration."""

    def test_provider_factory_registration(self):
        """Test DeepSeekGenerator can be registered with ProviderFactory."""
        from app.core.factory import ProviderFactory
        
        # Clear any existing registration
        ProviderFactory._registry.pop("deepseek", None)
        
        # Register
        ProviderFactory.register("deepseek", DeepSeekGenerator)
        
        # Verify
        assert "deepseek" in ProviderFactory._registry
        assert ProviderFactory._registry["deepseek"] == DeepSeekGenerator

    def test_provider_factory_get_instance(self):
        """Test getting DeepSeekGenerator instance from ProviderFactory."""
        from app.core.factory import ProviderFactory
        
        ProviderFactory.register("deepseek", DeepSeekGenerator)
        
        generator = ProviderFactory.get_provider("deepseek", api_key="test-key")
        
        assert isinstance(generator, DeepSeekGenerator)
        assert generator.api_key == "test-key"

    def test_provider_factory_case_insensitive(self):
        """Test case-insensitive key lookup."""
        from app.core.factory import ProviderFactory
        
        ProviderFactory.register("deepseek", DeepSeekGenerator)
        
        generator = ProviderFactory.get_provider("DEEPSEEK", api_key="test-key")
        
        assert isinstance(generator, DeepSeekGenerator)
