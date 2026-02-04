"""
Tests for CopywritingAgent workflow.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.application.agents.copywriting_agent import CopywritingAgent, GraphState
from app.domain.entities.agent_state import CopywritingStage


@pytest.fixture
def mock_socket_manager():
    """Mock socket_manager for all tests."""
    with patch("app.application.agents.copywriting_agent.socket_manager") as mock:
        mock.emit_thought = AsyncMock()
        mock.emit_result = AsyncMock()
        mock.emit_error = AsyncMock()
        mock.emit_tool_call = AsyncMock()
        yield mock


@pytest.fixture
def mock_provider_factory():
    """Mock ProviderFactory and generator."""
    with patch("app.application.agents.copywriting_agent.ProviderFactory") as mock_factory:
        mock_generator = MagicMock()
        mock_generator.__aenter__ = AsyncMock(return_value=mock_generator)
        mock_generator.__aexit__ = AsyncMock(return_value=None)
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


class TestCopywritingAgentInit:
    """Tests for CopywritingAgent initialization."""
    
    def test_default_initialization(self):
        """Test agent with default parameters."""
        agent = CopywritingAgent()
        assert agent.model == "deepseek-chat"
        assert agent.temperature == 0.7
        assert agent.max_tokens == 2000
    
    def test_custom_initialization(self):
        """Test agent with custom parameters."""
        agent = CopywritingAgent(
            model="deepseek-reasoner",
            temperature=0.5,
            max_tokens=3000,
        )
        assert agent.model == "deepseek-reasoner"
        assert agent.temperature == 0.5
        assert agent.max_tokens == 3000


class TestPlanNode:
    """Tests for plan_node method."""
    
    @pytest.mark.asyncio
    async def test_plan_node_success(
        self,
        mock_socket_manager,
        mock_provider_factory,
        sample_state,
    ):
        """Test successful plan generation."""
        mock_factory, mock_generator = mock_provider_factory
        
        # Mock generate response
        mock_response = MagicMock()
        mock_response.content = "Marketing outline for Smart Watch Pro..."
        mock_generator.generate = AsyncMock(return_value=mock_response)
        
        agent = CopywritingAgent()
        result = await agent.plan_node(sample_state)
        
        # Verify plan was generated
        assert result["plan"] == "Marketing outline for Smart Watch Pro..."
        assert result["current_stage"] == CopywritingStage.PLAN.value
        
        # Verify socket events were emitted
        assert mock_socket_manager.emit_thought.call_count == 2
    
    @pytest.mark.asyncio
    async def test_plan_node_emits_thought_on_start(
        self,
        mock_socket_manager,
        mock_provider_factory,
        sample_state,
    ):
        """Test that plan_node emits thought event on start."""
        mock_factory, mock_generator = mock_provider_factory
        mock_response = MagicMock()
        mock_response.content = "Plan content"
        mock_generator.generate = AsyncMock(return_value=mock_response)
        
        agent = CopywritingAgent()
        await agent.plan_node(sample_state)
        
        # First emit_thought should contain product name
        first_call = mock_socket_manager.emit_thought.call_args_list[0]
        assert "Smart Watch Pro" in first_call.kwargs["content"]
        assert first_call.kwargs["workflow_id"] == "test-workflow-123"


class TestDraftNode:
    """Tests for draft_node method."""
    
    @pytest.mark.asyncio
    async def test_draft_node_success(
        self,
        mock_socket_manager,
        mock_provider_factory,
        sample_state,
    ):
        """Test successful draft generation."""
        mock_factory, mock_generator = mock_provider_factory
        
        mock_response = MagicMock()
        mock_response.content = "初稿：Smart Watch Pro，您的健康伙伴..."
        mock_generator.generate = AsyncMock(return_value=mock_response)
        
        # Add plan to state
        sample_state["plan"] = "Marketing outline..."
        
        agent = CopywritingAgent()
        result = await agent.draft_node(sample_state)
        
        assert result["draft"] == "初稿：Smart Watch Pro，您的健康伙伴..."
        assert result["current_stage"] == CopywritingStage.DRAFT.value


class TestCritiqueNode:
    """Tests for critique_node method."""
    
    @pytest.mark.asyncio
    async def test_critique_node_success(
        self,
        mock_socket_manager,
        mock_provider_factory,
        sample_state,
    ):
        """Test successful critique generation."""
        mock_factory, mock_generator = mock_provider_factory
        
        mock_response = MagicMock()
        mock_response.content = "审核意见：1. 标题可以更吸引人..."
        mock_generator.generate = AsyncMock(return_value=mock_response)
        
        sample_state["draft"] = "Initial draft..."
        
        agent = CopywritingAgent()
        result = await agent.critique_node(sample_state)
        
        assert result["critique"] == "审核意见：1. 标题可以更吸引人..."
        assert result["current_stage"] == CopywritingStage.CRITIQUE.value


class TestFinalizeNode:
    """Tests for finalize_node method."""
    
    @pytest.mark.asyncio
    async def test_finalize_node_success(
        self,
        mock_socket_manager,
        mock_provider_factory,
        sample_state,
    ):
        """Test successful finalize generation."""
        mock_factory, mock_generator = mock_provider_factory
        
        mock_response = MagicMock()
        mock_response.content = "最终版：Smart Watch Pro - 重新定义智能穿戴..."
        mock_generator.generate = AsyncMock(return_value=mock_response)
        
        sample_state["draft"] = "Draft..."
        sample_state["critique"] = "Critique..."
        
        agent = CopywritingAgent()
        result = await agent.finalize_node(sample_state)
        
        assert result["final_copy"] == "最终版：Smart Watch Pro - 重新定义智能穿戴..."
        assert result["current_stage"] == CopywritingStage.COMPLETED.value
    
    @pytest.mark.asyncio
    async def test_finalize_node_emits_result(
        self,
        mock_socket_manager,
        mock_provider_factory,
        sample_state,
    ):
        """Test that finalize_node emits result event."""
        mock_factory, mock_generator = mock_provider_factory
        mock_response = MagicMock()
        mock_response.content = "Final copy"
        mock_generator.generate = AsyncMock(return_value=mock_response)
        
        sample_state["draft"] = "Draft..."
        sample_state["critique"] = "Critique..."
        
        agent = CopywritingAgent()
        await agent.finalize_node(sample_state)
        
        # Verify emit_result was called
        mock_socket_manager.emit_result.assert_called_once()
        call_kwargs = mock_socket_manager.emit_result.call_args.kwargs
        assert call_kwargs["workflow_id"] == "test-workflow-123"
        assert call_kwargs["result_data"]["finalCopy"] == "Final copy"


class TestFullWorkflow:
    """Tests for complete workflow execution."""
    
    @pytest.mark.asyncio
    async def test_run_full_workflow(
        self,
        mock_socket_manager,
        mock_provider_factory,
    ):
        """Test complete workflow execution from start to finish."""
        mock_factory, mock_generator = mock_provider_factory
        
        # Mock different responses for each stage
        responses = [
            "Plan: Marketing outline...",
            "Draft: Initial copy...",
            "Critique: Suggestions...",
            "Final: Polished copy...",
        ]
        mock_response = MagicMock()
        mock_generator.generate = AsyncMock(
            side_effect=[
                MagicMock(content=r) for r in responses
            ]
        )
        
        agent = CopywritingAgent()
        result = await agent.run(
            product_name="Test Product",
            features=["Feature 1", "Feature 2"],
            workflow_id="full-test-123",
        )
        
        # Verify all stages completed
        assert result["plan"] == "Plan: Marketing outline..."
        assert result["draft"] == "Draft: Initial copy..."
        assert result["critique"] == "Critique: Suggestions..."
        assert result["final_copy"] == "Final: Polished copy..."
        assert result["current_stage"] == CopywritingStage.COMPLETED.value
    
    @pytest.mark.asyncio
    async def test_run_generates_workflow_id_if_not_provided(
        self,
        mock_socket_manager,
        mock_provider_factory,
    ):
        """Test that run() generates a workflow_id if not provided."""
        mock_factory, mock_generator = mock_provider_factory
        mock_response = MagicMock()
        mock_response.content = "Content"
        mock_generator.generate = AsyncMock(return_value=mock_response)
        
        agent = CopywritingAgent()
        result = await agent.run(
            product_name="Test",
            features=["F1"],
            # No workflow_id provided
        )
        
        # Verify workflow_id was generated
        assert result["workflow_id"] != ""
        assert len(result["workflow_id"]) == 36  # UUID format


class TestAsyncRun:
    """Tests for asynchronous workflow execution."""
    
    @pytest.mark.asyncio
    async def test_run_async_returns_workflow_id_immediately(
        self,
        mock_socket_manager,
        mock_provider_factory,
    ):
        """Test that run_async returns workflow_id without waiting."""
        mock_factory, mock_generator = mock_provider_factory
        
        # Make generate very slow to ensure we return before it completes
        async def slow_generate(*args, **kwargs):
            import asyncio
            await asyncio.sleep(10)  # Very slow
            return MagicMock(content="content")
        
        mock_generator.generate = slow_generate
        
        agent = CopywritingAgent()
        workflow_id = await agent.run_async(
            product_name="Test",
            features=["F1"],
        )
        
        # Verify workflow_id returned immediately
        assert workflow_id != ""
        assert len(workflow_id) == 36


class TestErrorHandling:
    """Tests for error handling in workflow."""
    
    @pytest.mark.asyncio
    async def test_plan_node_emits_error_on_failure(
        self,
        mock_socket_manager,
        mock_provider_factory,
        sample_state,
    ):
        """Test that plan_node emits error event on failure."""
        from app.domain.exceptions import HTTPClientError
        
        mock_factory, mock_generator = mock_provider_factory
        mock_generator.generate = AsyncMock(
            side_effect=HTTPClientError("API request failed")
        )
        
        agent = CopywritingAgent()
        
        with pytest.raises(HTTPClientError):
            await agent.plan_node(sample_state)
        
        # Verify error was emitted
        mock_socket_manager.emit_error.assert_called_once()
        call_kwargs = mock_socket_manager.emit_error.call_args.kwargs
        assert call_kwargs["error_code"] == "PLAN_FAILED"


class TestSocketIOEvents:
    """Tests for Socket.io event emissions (CR-3 fix)."""
    
    @pytest.mark.asyncio
    async def test_emit_thought_includes_node_name(
        self,
        mock_socket_manager,
        mock_provider_factory,
        sample_state,
    ):
        """Verify emit_thought is called with correct node_name parameter."""
        mock_factory, mock_generator = mock_provider_factory
        mock_response = MagicMock()
        mock_response.content = "Plan content"
        mock_generator.generate = AsyncMock(return_value=mock_response)
        
        agent = CopywritingAgent()
        await agent.plan_node(sample_state)
        
        # Verify node_name is passed to emit_thought
        emit_thought_calls = mock_socket_manager.emit_thought.call_args_list
        assert len(emit_thought_calls) >= 1
        
        # All emit_thought calls should have node_name="plan"
        for call in emit_thought_calls:
            assert call.kwargs.get("node_name") == "plan"
    
    @pytest.mark.asyncio
    async def test_emit_tool_call_events_for_plan_node(
        self,
        mock_socket_manager,
        mock_provider_factory,
        sample_state,
    ):
        """Verify emit_tool_call is called with in_progress and completed status."""
        mock_factory, mock_generator = mock_provider_factory
        mock_response = MagicMock()
        mock_response.content = "Plan content"
        # Mock streaming method to avoid fallback
        mock_generator.generate_stream_with_callback = AsyncMock(return_value=mock_response)
        
        agent = CopywritingAgent()
        await agent.plan_node(sample_state)
        
        # Verify emit_tool_call was called with in_progress and completed
        tool_call_calls = mock_socket_manager.emit_tool_call.call_args_list
        assert len(tool_call_calls) >= 2
        
        # Check for in_progress call
        in_progress_calls = [
            c for c in tool_call_calls 
            if c.kwargs.get("status") == "in_progress"
        ]
        assert len(in_progress_calls) >= 1
        assert in_progress_calls[0].kwargs["tool_name"] == "deepseek_generate"
        assert in_progress_calls[0].kwargs["workflow_id"] == "test-workflow-123"
        
        # Check for completed call
        completed_calls = [
            c for c in tool_call_calls 
            if c.kwargs.get("status") == "completed"
        ]
        assert len(completed_calls) >= 1
    
    @pytest.mark.asyncio
    async def test_emit_tool_call_error_on_streaming_failure(
        self,
        mock_socket_manager,
        mock_provider_factory,
        sample_state,
    ):
        """Verify emit_tool_call emits error status when streaming fails."""
        mock_factory, mock_generator = mock_provider_factory
        
        # Mock streaming to fail, but regular generate to succeed (fallback)
        mock_generator.generate_stream_with_callback = AsyncMock(
            side_effect=Exception("Streaming failed")
        )
        mock_response = MagicMock()
        mock_response.content = "Fallback content"
        mock_generator.generate = AsyncMock(return_value=mock_response)
        
        agent = CopywritingAgent()
        result = await agent.plan_node(sample_state)
        
        # Verify plan was generated via fallback
        assert result["plan"] == "Fallback content"
        
        # Verify emit_tool_call was called with error status
        tool_call_calls = mock_socket_manager.emit_tool_call.call_args_list
        error_calls = [
            c for c in tool_call_calls 
            if c.kwargs.get("status") == "error"
        ]
        assert len(error_calls) >= 1
        assert "failed" in error_calls[0].kwargs["message"].lower()
    
    @pytest.mark.asyncio
    async def test_each_node_uses_correct_node_name(
        self,
        mock_socket_manager,
        mock_provider_factory,
    ):
        """Verify each node emits thought with its own node_name."""
        mock_factory, mock_generator = mock_provider_factory
        
        # Each node needs 2 responses: streaming fails (triggers fallback) + fallback succeeds
        responses = [
            "Plan content",
            "Plan content",  # fallback retry
            "Draft content",
            "Draft content",  # fallback retry
            "Critique content",
            "Critique content",  # fallback retry
            "Final content",
            "Final content",  # fallback retry
        ]
        mock_generator.generate = AsyncMock(
            side_effect=[MagicMock(content=r) for r in responses]
        )
        
        agent = CopywritingAgent()
        result = await agent.run(
            product_name="Test Product",
            features=["Feature 1"],
            workflow_id="node-name-test"
        )
        
        # Collect all emit_thought calls
        thought_calls = mock_socket_manager.emit_thought.call_args_list
        
        # Extract unique node_names
        node_names = set(c.kwargs.get("node_name") for c in thought_calls)
        
        # Should have all 4 node names
        assert "plan" in node_names
        assert "draft" in node_names
        assert "critique" in node_names
        assert "finalize" in node_names


class TestStreamingFallback:
    """Tests for streaming fallback mechanism (MD-6 fix)."""
    
    @pytest.mark.asyncio
    async def test_streaming_fallback_on_failure(
        self,
        mock_socket_manager,
        mock_provider_factory,
        sample_state,
    ):
        """Test that streaming failure falls back to regular generation."""
        mock_factory, mock_generator = mock_provider_factory
        
        # Streaming fails
        mock_generator.generate_stream_with_callback = AsyncMock(
            side_effect=Exception("Streaming not available")
        )
        
        # Regular generation succeeds
        mock_response = MagicMock()
        mock_response.content = "Fallback plan content"
        mock_generator.generate = AsyncMock(return_value=mock_response)
        
        agent = CopywritingAgent()
        result = await agent.plan_node(sample_state)
        
        # Verify fallback was used
        assert result["plan"] == "Fallback plan content"
        mock_generator.generate.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_streaming_success_uses_streaming_method(
        self,
        mock_socket_manager,
        mock_provider_factory,
        sample_state,
    ):
        """Test that successful streaming uses streaming method."""
        mock_factory, mock_generator = mock_provider_factory
        
        mock_response = MagicMock()
        mock_response.content = "Streamed content"
        mock_generator.generate_stream_with_callback = AsyncMock(return_value=mock_response)
        
        agent = CopywritingAgent()
        result = await agent.plan_node(sample_state)
        
        # Verify streaming method was called
        mock_generator.generate_stream_with_callback.assert_called_once()
        assert result["plan"] == "Streamed content"

