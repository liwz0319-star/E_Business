"""
Unit tests for ImageAgent workflow.

Tests the image generation agent's workflow stages and state management.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.application.agents.image_agent import (
    ImageAgent,
    ImageAgentState,
)
from app.domain.entities.image_artifact import ImageArtifact
from app.domain.entities.image_request import ImageGenerationRequest


class TestImageAgentState:
    """Tests for ImageAgentState TypedDict structure."""
    
    def test_state_has_required_fields(self):
        """State should have all required fields."""
        state: ImageAgentState = {
            "prompt": "A red car",
            "optimized_prompt": "",
            "workflow_id": str(uuid4()),
            "current_stage": None,
            "image_url": "",
            "asset_id": None,
            "width": 512,
            "height": 512,
            "error": None,
        }
        
        assert state["prompt"] == "A red car"
        assert state["width"] == 512
        assert state["height"] == 512


class TestImageAgentInitialization:
    """Tests for ImageAgent initialization."""
    
    def test_default_initialization(self):
        """Agent should initialize with default settings."""
        agent = ImageAgent()
        
        assert agent.model == "deepseek-chat"
        assert agent.temperature == 0.7
        assert agent.max_tokens == 500
    
    def test_custom_initialization(self):
        """Agent should accept custom settings."""
        agent = ImageAgent(
            model="custom-model",
            temperature=0.5,
            max_tokens=300,
        )
        
        assert agent.model == "custom-model"
        assert agent.temperature == 0.5
        assert agent.max_tokens == 300
    
    def test_graph_is_built(self):
        """Agent should build LangGraph workflow on init."""
        agent = ImageAgent()
        
        assert agent._graph is not None
        assert agent._checkpointer is not None


class TestImageAgentWorkflowStatus:
    """Tests for workflow status management."""
    
    def test_get_workflow_status_not_found(self):
        """Should return None for unknown workflow ID."""
        status = ImageAgent.get_workflow_status("unknown-id")
        
        assert status is None
    
    def test_cancel_workflow_not_found(self):
        """Should return False for unknown workflow ID."""
        cancelled = ImageAgent.cancel_workflow("unknown-id")
        
        assert cancelled is False


class TestOptimizePromptNode:
    """Tests for optimize_prompt_node."""
    
    @pytest.mark.asyncio
    async def test_optimize_prompt_updates_state(self):
        """optimize_prompt_node should update state with optimized prompt."""
        agent = ImageAgent()
        workflow_id = str(uuid4())
        
        initial_state: ImageAgentState = {
            "prompt": "A red sports car",
            "optimized_prompt": "",
            "workflow_id": workflow_id,
            "current_stage": None,
            "image_url": "",
            "asset_id": None,
            "width": 512,
            "height": 512,
            "error": None,
        }
        
        # Mock the generator and socket_manager
        mock_response = MagicMock()
        mock_response.content = "A photorealistic red sports car with dramatic lighting"
        
        mock_generator = AsyncMock()
        mock_generator.generate = AsyncMock(return_value=mock_response)
        mock_generator.__aenter__ = AsyncMock(return_value=mock_generator)
        mock_generator.__aexit__ = AsyncMock(return_value=None)
        
        with patch("app.core.factory.ProviderFactory.get_provider", return_value=mock_generator):
            with patch("app.interface.ws.socket_manager.socket_manager.emit_thought", new_callable=AsyncMock):
                with patch("app.interface.ws.socket_manager.socket_manager.emit_tool_call", new_callable=AsyncMock):
                    result = await agent.optimize_prompt_node(initial_state)
        
        assert result["optimized_prompt"] == "A photorealistic red sports car with dramatic lighting"
        assert result["current_stage"] == "optimize_prompt"


class TestGenerateImageNode:
    """Tests for generate_image_node."""
    
    @pytest.mark.asyncio
    async def test_generate_image_updates_state(self):
        """generate_image_node should update state with image URL."""
        agent = ImageAgent()
        workflow_id = str(uuid4())
        
        # Set up workflow state (normally done by optimize_prompt_node)
        from app.application.agents.image_agent import _workflow_states
        _workflow_states[workflow_id] = {
            "status": "running",
            "current_stage": "optimize_prompt",
            "state": {},
        }
        
        initial_state: ImageAgentState = {
            "prompt": "A red sports car",
            "optimized_prompt": "A photorealistic red sports car",
            "workflow_id": workflow_id,
            "current_stage": "optimize_prompt",
            "image_url": "",
            "asset_id": None,
            "width": 512,
            "height": 512,
            "error": None,
        }
        
        with patch("app.interface.ws.socket_manager.socket_manager.emit_thought", new_callable=AsyncMock):
            with patch("app.interface.ws.socket_manager.socket_manager.emit_tool_call", new_callable=AsyncMock):
                result = await agent.generate_image_node(initial_state)
        
        assert result["image_url"] != ""
        assert result["current_stage"] == "generate_image"
        assert "picsum" in result["image_url"] or "placeholder" in result["image_url"]


class TestMockMCPImageGenerator:
    """Tests for MockMCPImageGenerator."""
    
    @pytest.mark.asyncio
    async def test_generate_returns_artifact(self):
        """Mock generator should return valid ImageArtifact."""
        from app.infrastructure.mcp import MockMCPImageGenerator
        
        generator = MockMCPImageGenerator(delay_seconds=0.1)
        request = ImageGenerationRequest(
            prompt="Test prompt",
            width=512,
            height=512,
        )
        
        async with generator:
            artifact = await generator.generate(request)
        
        assert isinstance(artifact, ImageArtifact)
        assert artifact.url != ""
        assert artifact.prompt == "Test prompt"
        assert artifact.width == 512
        assert artifact.height == 512
        assert artifact.provider == "mock"
    
    @pytest.mark.asyncio
    async def test_generate_respects_dimensions(self):
        """Generated URL should include requested dimensions."""
        from app.infrastructure.mcp import MockMCPImageGenerator
        
        generator = MockMCPImageGenerator(delay_seconds=0.1, placeholder_service=0)
        request = ImageGenerationRequest(
            prompt="Test",
            width=1024,
            height=768,
        )
        
        async with generator:
            artifact = await generator.generate(request)
        
        assert "1024" in artifact.url
        assert "768" in artifact.url


class TestImageArtifactEntity:
    """Tests for ImageArtifact domain entity."""
    
    def test_to_dict_serialization(self):
        """ImageArtifact should serialize to dict correctly."""
        artifact = ImageArtifact(
            url="https://example.com/image.png",
            prompt="Test prompt",
            original_prompt="Original",
            provider="test",
            width=512,
            height=512,
        )
        
        data = artifact.to_dict()
        
        assert data["url"] == "https://example.com/image.png"
        assert data["prompt"] == "Test prompt"
        assert data["original_prompt"] == "Original"
        assert data["provider"] == "test"
        assert "id" in data
        assert "created_at" in data
    
    def test_from_dict_deserialization(self):
        """ImageArtifact should deserialize from dict correctly."""
        data = {
            "url": "https://example.com/image.png",
            "prompt": "Test prompt",
            "width": 1024,
            "height": 768,
        }
        
        artifact = ImageArtifact.from_dict(data)
        
        assert artifact.url == "https://example.com/image.png"
        assert artifact.prompt == "Test prompt"
        assert artifact.width == 1024
        assert artifact.height == 768


class TestImageGenerationRequest:
    """Tests for ImageGenerationRequest domain entity."""
    
    def test_default_values(self):
        """Request should have sensible defaults."""
        request = ImageGenerationRequest(prompt="Test")
        
        assert request.width == 512
        assert request.height == 512
        assert request.num_inference_steps == 50
        assert request.guidance_scale == 7.5
    
    def test_to_dict(self):
        """Request should serialize to dict."""
        request = ImageGenerationRequest(
            prompt="Test",
            width=1024,
            height=768,
            style="photorealistic",
        )
        
        data = request.to_dict()
        
        assert data["prompt"] == "Test"
        assert data["width"] == 1024
        assert data["height"] == 768
        assert data["style"] == "photorealistic"
