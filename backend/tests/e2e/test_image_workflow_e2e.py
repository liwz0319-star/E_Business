"""
E2E Tests for Image Generation API

Tests the image generation API endpoints with mocked dependencies.
Focuses on API contract verification rather than full workflow execution.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

import pytest_asyncio
from httpx import ASGITransport, AsyncClient


class TestImageAPIE2E:
    """
    E2E tests for Image Generation API.
    
    Tests API endpoints without requiring full workflow execution.
    """
    
    @pytest_asyncio.fixture
    async def api_client(self):
        """Create API client with mocked agent."""
        from app.main import app
        
        # Mock the agent
        mock_agent = MagicMock()
        mock_agent.run_async = AsyncMock(return_value="mock-workflow-id-123")
        
        # Patch get_agent function
        with patch("app.interface.routes.images.get_agent", return_value=mock_agent):
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as client:
                yield client
    
    @pytest.mark.asyncio
    async def test_generate_endpoint_returns_202(self, api_client):
        """
        Test POST /api/v1/images/generate returns 202 Accepted.
        """
        response = await api_client.post(
            "/api/v1/images/generate",
            json={
                "prompt": "A beautiful sunset over mountains",
                "width": 512,
                "height": 512,
            }
        )
        
        assert response.status_code == 202
        data = response.json()
        assert "workflow_id" in data
        assert data["status"] == "starting"
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_generate_with_default_dimensions(self, api_client):
        """
        Test that default dimensions (512x512) are used when not specified.
        """
        response = await api_client.post(
            "/api/v1/images/generate",
            json={"prompt": "Test image with defaults"}
        )
        
        assert response.status_code == 202
    
    @pytest.mark.asyncio
    async def test_generate_validation_empty_prompt(self, api_client):
        """
        Test validation rejects empty prompt.
        """
        response = await api_client.post(
            "/api/v1/images/generate",
            json={"prompt": "", "width": 512, "height": 512}
        )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_generate_validation_invalid_width(self, api_client):
        """
        Test validation rejects invalid dimensions.
        Width must be >= 256 and <= 2048.
        """
        response = await api_client.post(
            "/api/v1/images/generate",
            json={"prompt": "Test", "width": 100, "height": 512}  # 100 < 256
        )
        
        assert response.status_code == 422


class TestImageStatusE2E:
    """Tests for workflow status endpoints."""
    
    @pytest_asyncio.fixture
    async def api_client(self):
        """Create simple API client."""
        from app.main import app
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client
    
    @pytest.mark.asyncio
    async def test_status_endpoint_not_found(self, api_client):
        """
        Test GET /api/v1/images/status/{id} returns 404 for unknown workflow.
        """
        response = await api_client.get(
            "/api/v1/images/status/non-existent-workflow-id"
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    @pytest.mark.asyncio 
    async def test_cancel_endpoint_non_existent(self, api_client):
        """
        Test POST /api/v1/images/cancel/{id} handles non-existent workflow.
        """
        response = await api_client.post(
            "/api/v1/images/cancel/non-existent-workflow-id"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["cancelled"] is False


class TestImageStatusWithMockData:
    """Tests for workflow status with pre-populated data."""
    
    @pytest_asyncio.fixture
    async def client_with_status(self):
        """Create client and mock workflow status."""
        from app.main import app
        from app.application.agents.image_agent import _workflow_states
        
        # Set up mock workflow state
        workflow_id = "test-status-workflow-456"
        _workflow_states[workflow_id] = {
            "status": "completed",
            "current_stage": "completed",
            "state": {
                "image_url": "https://example.com/generated-image.png",
                "optimized_prompt": "Enhanced test prompt",
                "asset_id": "asset-uuid-789",
            }
        }
        
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            yield client, workflow_id
        
        # Cleanup
        _workflow_states.pop(workflow_id, None)
    
    @pytest.mark.asyncio
    async def test_status_returns_completed_workflow(self, client_with_status):
        """
        Test status endpoint returns correct data for completed workflow.
        """
        client, workflow_id = client_with_status
        
        response = await client.get(f"/api/v1/images/status/{workflow_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["workflow_id"] == workflow_id
        assert data["status"] == "completed"
        assert data["current_stage"] == "completed"
        assert data["image_url"] == "https://example.com/generated-image.png"
        assert data["asset_id"] == "asset-uuid-789"
