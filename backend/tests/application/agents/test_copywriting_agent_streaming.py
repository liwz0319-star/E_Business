"""
Tests for CopywritingAgent streaming functionality.

Story 2-3: Thinking Stream Integration
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import time as time_module

from app.application.agents.copywriting_agent import CopywritingAgent, GraphState
from app.domain.entities.generation import StreamChunk, GenerationResult


@pytest.fixture
def mock_socket_manager():
    """Mock socket_manager for all tests."""
    with patch("app.application.agents.copywriting_agent.socket_manager") as mock:
        mock.emit_thought = AsyncMock()
        mock.emit_tool_call = AsyncMock()
        mock.emit_result = AsyncMock()
        mock.emit_error = AsyncMock()
        yield mock


@pytest.fixture
def mock_provider_factory_streaming():
    """Mock ProviderFactory with streaming support."""
    with patch("app.application.agents.copywriting_agent.ProviderFactory") as mock_factory:
        mock_generator = MagicMock()
        mock_generator.__aenter__ = AsyncMock(return_value=mock_generator)
        mock_generator.__aexit__ = AsyncMock(return_value=None)
        
        # Mock both generate and generate_stream_with_callback
        mock_generator.generate = AsyncMock()
        mock_generator.generate_stream_with_callback = AsyncMock()
        
        mock_factory.get_provider.return_value = mock_generator
        yield mock_factory, mock_generator


@pytest.fixture
def sample_state() -> GraphState:
    """Sample workflow state for testing."""
    return {
        "product_name": "Smart Watch Pro",
        "features": ["Heart rate monitoring", "GPS tracking", "7-day battery"],
        "workflow_id": "test-workflow-123",
        "current_stage": None,
        "plan": None,
        "draft": None,
        "critique": None,
        "final_copy": None,
        "brand_guidelines": "Professional and modern tone",
    }


class TestStreamingGeneration:
    """Tests for streaming generation functionality."""
    
    @pytest.mark.asyncio
    async def test_generate_with_streaming_emits_reasoning_content(
        self,
        mock_socket_manager,
        mock_provider_factory_streaming,
    ):
        """Test that _generate_with_streaming emits reasoning_content."""
        mock_factory, mock_generator = mock_provider_factory_streaming
        
        # Setup streaming callback to capture chunks
        async def mock_stream_with_callback(request, callback):
            # Simulate streaming reasoning chunks
            chunks = [
                StreamChunk(content="", reasoning_content="Thinking step 1..."),
                StreamChunk(content="", reasoning_content="Analyzing..."),
                StreamChunk(content="Final output", reasoning_content=None),
            ]
            for chunk in chunks:
                await callback(chunk)
            return GenerationResult(content="Final output", raw_response={})
        
        mock_generator.generate_stream_with_callback = mock_stream_with_callback
        
        agent = CopywritingAgent()
        result = await agent._generate_with_streaming(
            prompt="Test prompt",
            workflow_id="test-wf-123",
            node_name="plan"
        )
        
        assert result == "Final output"
        
        # Verify emit_thought was called for reasoning content
        # Should be called twice (for the two chunks with reasoning_content)
        assert mock_socket_manager.emit_thought.call_count == 2
        
        # Verify first call
        first_call = mock_socket_manager.emit_thought.call_args_list[0]
        assert first_call.kwargs["content"] == "Thinking step 1..."
        assert first_call.kwargs["node_name"] == "plan"
    
    @pytest.mark.asyncio
    async def test_generate_with_streaming_fallback_on_error(
        self,
        mock_socket_manager,
        mock_provider_factory_streaming,
    ):
        """Test that streaming falls back to non-streaming on error."""
        mock_factory, mock_generator = mock_provider_factory_streaming
        
        # Make streaming fail
        mock_generator.generate_stream_with_callback = AsyncMock(
            side_effect=Exception("Streaming not supported")
        )
        
        # But regular generate should work
        mock_response = MagicMock()
        mock_response.content = "Fallback content"
        mock_generator.generate = AsyncMock(return_value=mock_response)
        
        agent = CopywritingAgent()
        result = await agent._generate_with_streaming(
            prompt="Test prompt",
            workflow_id="test-wf-123",
            node_name="plan"
        )
        
        # Should fallback to regular generate
        assert result == "Fallback content"
        mock_generator.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_stream_callback_handles_emit_error_gracefully(
        self,
        mock_socket_manager,
        mock_provider_factory_streaming,
    ):
        """Test that stream callback handles emit errors without crashing."""
        mock_factory, mock_generator = mock_provider_factory_streaming
        
        # Make emit_thought fail
        mock_socket_manager.emit_thought = AsyncMock(
            side_effect=Exception("Socket error")
        )
        
        async def mock_stream_with_callback(request, callback):
            chunks = [
                StreamChunk(content="", reasoning_content="Thinking..."),
                StreamChunk(content="Output", reasoning_content=None),
            ]
            for chunk in chunks:
                await callback(chunk)
            return GenerationResult(content="Output", raw_response={})
        
        mock_generator.generate_stream_with_callback = mock_stream_with_callback
        
        agent = CopywritingAgent()
        
        # Should not raise, despite emit_thought failures
        result = await agent._generate_with_streaming(
            prompt="Test prompt",
            workflow_id="test-wf-123",
            node_name="plan"
        )
        
        assert result == "Output"


class TestNodeStreamingIntegration:
    """Tests for streaming integration in workflow nodes."""
    
    @pytest.mark.asyncio
    async def test_plan_node_uses_streaming(
        self,
        mock_socket_manager,
        mock_provider_factory_streaming,
        sample_state,
    ):
        """Test that plan_node uses streaming generation."""
        mock_factory, mock_generator = mock_provider_factory_streaming
        
        async def mock_stream_with_callback(request, callback):
            # Simulate reasoning content
            await callback(StreamChunk(content="", reasoning_content="Planning..."))
            return GenerationResult(content="Marketing plan", raw_response={})
        
        mock_generator.generate_stream_with_callback = mock_stream_with_callback
        
        agent = CopywritingAgent()
        result = await agent.plan_node(sample_state)
        
        assert result["plan"] == "Marketing plan"
        
        # Verify streaming was used (emit_thought called for reasoning)
        # First call is node entry, second is streaming content, third is completion
        assert mock_socket_manager.emit_thought.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_draft_node_uses_streaming(
        self,
        mock_socket_manager,
        mock_provider_factory_streaming,
        sample_state,
    ):
        """Test that draft_node uses streaming generation."""
        mock_factory, mock_generator = mock_provider_factory_streaming
        
        async def mock_stream_with_callback(request, callback):
            await callback(StreamChunk(content="", reasoning_content="Drafting..."))
            return GenerationResult(content="Draft content", raw_response={})
        
        mock_generator.generate_stream_with_callback = mock_stream_with_callback
        
        sample_state["plan"] = "Some plan"
        
        agent = CopywritingAgent()
        result = await agent.draft_node(sample_state)
        
        assert result["draft"] == "Draft content"
    
    @pytest.mark.asyncio
    async def test_critique_node_uses_streaming(
        self,
        mock_socket_manager,
        mock_provider_factory_streaming,
        sample_state,
    ):
        """Test that critique_node uses streaming generation."""
        mock_factory, mock_generator = mock_provider_factory_streaming
        
        async def mock_stream_with_callback(request, callback):
            await callback(StreamChunk(content="", reasoning_content="Critiquing..."))
            return GenerationResult(content="Critique content", raw_response={})
        
        mock_generator.generate_stream_with_callback = mock_stream_with_callback
        
        sample_state["draft"] = "Some draft"
        
        agent = CopywritingAgent()
        result = await agent.critique_node(sample_state)
        
        assert result["critique"] == "Critique content"
    
    @pytest.mark.asyncio
    async def test_finalize_node_uses_streaming(
        self,
        mock_socket_manager,
        mock_provider_factory_streaming,
        sample_state,
    ):
        """Test that finalize_node uses streaming generation."""
        mock_factory, mock_generator = mock_provider_factory_streaming
        
        async def mock_stream_with_callback(request, callback):
            await callback(StreamChunk(content="", reasoning_content="Finalizing..."))
            return GenerationResult(content="Final copy", raw_response={})
        
        mock_generator.generate_stream_with_callback = mock_stream_with_callback
        
        sample_state["draft"] = "Some draft"
        sample_state["critique"] = "Some critique"
        
        agent = CopywritingAgent()
        result = await agent.finalize_node(sample_state)
        
        assert result["final_copy"] == "Final copy"


class TestRateLimitedErrorLogging:
    """Tests for rate-limited error logging."""
    
    @pytest.mark.asyncio
    async def test_should_log_error_first_time(self):
        """Test that first error is always logged."""
        # Reset class-level state
        CopywritingAgent._error_log_times.clear()
        
        result = await CopywritingAgent._should_log_error("test_error_key")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_should_not_log_error_within_cooldown(self):
        """Test that errors within cooldown period are not logged."""
        # Reset and set first log
        CopywritingAgent._error_log_times.clear()
        
        # First call should log
        first_result = await CopywritingAgent._should_log_error("test_error_key")
        assert first_result is True
        
        # Immediate second call should not log
        second_result = await CopywritingAgent._should_log_error("test_error_key")
        assert second_result is False
    
    @pytest.mark.asyncio
    async def test_should_log_error_after_cooldown(self):
        """Test that errors after cooldown period are logged."""
        # Reset class-level state
        CopywritingAgent._error_log_times.clear()
        
        # First call
        await CopywritingAgent._should_log_error("test_error_key")
        
        # Simulate time passing beyond cooldown
        from app.core.config import settings
        CopywritingAgent._error_log_times["test_error_key"] = (
            time_module.time() - settings.error_log_cooldown_seconds - 1
        )
        
        # Should log again
        result = await CopywritingAgent._should_log_error("test_error_key")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_different_error_keys_logged_independently(self):
        """Test that different error keys are tracked independently."""
        # Reset class-level state
        CopywritingAgent._error_log_times.clear()
        
        # Both should log
        result1 = await CopywritingAgent._should_log_error("error_key_1")
        result2 = await CopywritingAgent._should_log_error("error_key_2")
        
        assert result1 is True
        assert result2 is True
        
        # Second call to first key should not log
        result3 = await CopywritingAgent._should_log_error("error_key_1")
        assert result3 is False


class TestSocketDisconnectionHandling:
    """Tests for socket disconnection handling during streaming (L2)."""
    
    @pytest.mark.asyncio
    async def test_socket_disconnect_during_streaming_handled_gracefully(
        self,
        mock_socket_manager,
        mock_provider_factory_streaming,
    ):
        """Test that socket disconnect during streaming is handled gracefully."""
        mock_factory, mock_generator = mock_provider_factory_streaming
        
        # Make emit_thought raise an exception simulating disconnect
        disconnect_error = ConnectionError("Socket disconnected")
        mock_socket_manager.emit_thought = AsyncMock(side_effect=disconnect_error)
        mock_socket_manager.emit_tool_call = AsyncMock()
        
        async def mock_stream_with_callback(request, callback):
            # Simulate streaming that triggers emit_thought (which will fail)
            await callback(StreamChunk(content="", reasoning_content="Thinking..."))
            await callback(StreamChunk(content="Output", reasoning_content=None))
            return GenerationResult(content="Output", raw_response={})
        
        mock_generator.generate_stream_with_callback = mock_stream_with_callback
        
        agent = CopywritingAgent()
        
        # Should NOT raise despite socket disconnection
        result = await agent._generate_with_streaming(
            prompt="Test prompt",
            workflow_id="test-disconnect-123",
            node_name="plan"
        )
        
        # Streaming should complete successfully despite emit failures
        assert result == "Output"
    
    @pytest.mark.asyncio
    async def test_socket_disconnect_error_is_logged_with_rate_limit(
        self,
        mock_socket_manager,
        mock_provider_factory_streaming,
    ):
        """Test that socket disconnect errors are logged with rate limiting."""
        mock_factory, mock_generator = mock_provider_factory_streaming
        
        # Reset error log times to ensure fresh state
        CopywritingAgent._error_log_times.clear()
        
        # Make emit_thought fail with socket error
        mock_socket_manager.emit_thought = AsyncMock(
            side_effect=ConnectionError("Socket disconnected")
        )
        mock_socket_manager.emit_tool_call = AsyncMock()
        
        async def mock_stream_with_callback(request, callback):
            # Multiple chunks to trigger multiple emit failures
            for i in range(5):
                await callback(StreamChunk(content="", reasoning_content=f"Step {i}"))
            return GenerationResult(content="Done", raw_response={})
        
        mock_generator.generate_stream_with_callback = mock_stream_with_callback
        
        agent = CopywritingAgent()
        
        # Execute - should handle all errors gracefully
        with patch("app.application.agents.copywriting_agent.logger") as mock_logger:
            result = await agent._generate_with_streaming(
                prompt="Test prompt",
                workflow_id="test-rate-limit-123",
                node_name="plan"
            )
            
            # Should complete
            assert result == "Done"
            
            # Due to rate limiting, logger.warning should be called only once
            # (subsequent errors within cooldown are suppressed)
            warning_calls = [
                c for c in mock_logger.warning.call_args_list 
                if "emit thought" in str(c).lower()
            ]
            assert len(warning_calls) <= 1


class TestEmitThoughtNodeNameInAgent:
    """Tests to verify node_name is passed correctly in agent emit_thought calls."""
    
    @pytest.mark.asyncio
    async def test_plan_node_emits_thought_with_node_name(
        self,
        mock_socket_manager,
        mock_provider_factory_streaming,
        sample_state,
    ):
        """Test that plan_node passes node_name='plan' to emit_thought."""
        mock_factory, mock_generator = mock_provider_factory_streaming
        
        async def mock_stream_with_callback(request, callback):
            return GenerationResult(content="Plan", raw_response={})
        
        mock_generator.generate_stream_with_callback = mock_stream_with_callback
        
        agent = CopywritingAgent()
        await agent.plan_node(sample_state)
        
        # Check all emit_thought calls have correct node_name
        for call in mock_socket_manager.emit_thought.call_args_list:
            assert call.kwargs.get("node_name") == "plan"
    
    @pytest.mark.asyncio
    async def test_draft_node_emits_thought_with_node_name(
        self,
        mock_socket_manager,
        mock_provider_factory_streaming,
        sample_state,
    ):
        """Test that draft_node passes node_name='draft' to emit_thought."""
        mock_factory, mock_generator = mock_provider_factory_streaming
        
        async def mock_stream_with_callback(request, callback):
            return GenerationResult(content="Draft", raw_response={})
        
        mock_generator.generate_stream_with_callback = mock_stream_with_callback
        
        sample_state["plan"] = "Some plan"
        
        agent = CopywritingAgent()
        await agent.draft_node(sample_state)
        
        # Check all emit_thought calls have correct node_name
        for call in mock_socket_manager.emit_thought.call_args_list:
            assert call.kwargs.get("node_name") == "draft"

