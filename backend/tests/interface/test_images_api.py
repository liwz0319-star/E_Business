"""
Integration tests for Image Generation API.

Tests the /api/v1/images endpoints.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient, ASGITransport

from app.main import fastapi_app


@pytest.fixture
async def client():
    """Create async test client."""
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


class TestImageGenerateEndpoint:
    """Tests for POST /api/v1/images/generate."""
    
    @pytest.mark.asyncio
    async def test_generate_returns_workflow_id(self, client):
        """Generate endpoint should return workflow ID."""
        with patch("app.interface.routes.images.get_agent") as mock_get_agent:
            mock_agent = MagicMock()
            mock_agent.run_async = AsyncMock(return_value="test-workflow-id")
            mock_get_agent.return_value = mock_agent
            
            response = await client.post(
                "/api/v1/images/generate",
                json={"prompt": "A beautiful sunset"}
            )
        
        assert response.status_code == 202
        data = response.json()
        assert data["workflow_id"] == "test-workflow-id"
        assert data["status"] == "starting"
    
    @pytest.mark.asyncio
    async def test_generate_with_dimensions(self, client):
        """Generate endpoint should accept custom dimensions."""
        with patch("app.interface.routes.images.get_agent") as mock_get_agent:
            mock_agent = MagicMock()
            mock_agent.run_async = AsyncMock(return_value="test-id")
            mock_get_agent.return_value = mock_agent
            
            response = await client.post(
                "/api/v1/images/generate",
                json={
                    "prompt": "Test",
                    "width": 1024,
                    "height": 768
                }
            )
        
        assert response.status_code == 202
        mock_agent.run_async.assert_called_once_with(
            prompt="Test",
            width=1024,
            height=768,
        )
    
    @pytest.mark.asyncio
    async def test_generate_validates_prompt(self, client):
        """Generate endpoint should require prompt."""
        response = await client.post(
            "/api/v1/images/generate",
            json={}
        )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_generate_validates_dimensions(self, client):
        """Generate endpoint should validate dimension bounds."""
        # Width too small
        response = await client.post(
            "/api/v1/images/generate",
            json={"prompt": "Test", "width": 100}
        )
        assert response.status_code == 422
        
        # Height too large
        response = await client.post(
            "/api/v1/images/generate",
            json={"prompt": "Test", "height": 5000}
        )
        assert response.status_code == 422


class TestImageStatusEndpoint:
    """Tests for GET /api/v1/images/status/{workflow_id}."""
    
    @pytest.mark.asyncio
    async def test_status_not_found(self, client):
        """Status endpoint should return 404 for unknown workflow."""
        with patch("app.application.agents.image_agent.ImageAgent.get_workflow_status", return_value=None):
            response = await client.get("/api/v1/images/status/unknown-id")
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_status_returns_running(self, client):
        """Status endpoint should return running status."""
        mock_status = {
            "status": "running",
            "current_stage": "optimize_prompt",
            "state": {
                "image_url": "",
                "optimized_prompt": "",
                "asset_id": None,
            }
        }
        
        with patch("app.application.agents.image_agent.ImageAgent.get_workflow_status", return_value=mock_status):
            response = await client.get("/api/v1/images/status/test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert data["current_stage"] == "optimize_prompt"
    
    @pytest.mark.asyncio
    async def test_status_returns_completed(self, client):
        """Status endpoint should return completed status with results."""
        mock_status = {
            "status": "completed",
            "current_stage": "completed",
            "state": {
                "image_url": "https://example.com/image.png",
                "optimized_prompt": "Optimized prompt",
                "asset_id": "asset-uuid",
            }
        }
        
        with patch("app.application.agents.image_agent.ImageAgent.get_workflow_status", return_value=mock_status):
            response = await client.get("/api/v1/images/status/test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["image_url"] == "https://example.com/image.png"
        assert data["optimized_prompt"] == "Optimized prompt"
        assert data["asset_id"] == "asset-uuid"


class TestImageCancelEndpoint:
    """Tests for POST /api/v1/images/cancel/{workflow_id}."""
    
    @pytest.mark.asyncio
    async def test_cancel_success(self, client):
        """Cancel endpoint should cancel running workflow."""
        with patch("app.application.agents.image_agent.ImageAgent.cancel_workflow", return_value=True):
            response = await client.post("/api/v1/images/cancel/test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["cancelled"] is True
        assert data["workflow_id"] == "test-id"
    
    @pytest.mark.asyncio
    async def test_cancel_not_found(self, client):
        """Cancel endpoint should handle unknown workflow gracefully."""
        with patch("app.application.agents.image_agent.ImageAgent.cancel_workflow", return_value=False):
            response = await client.post("/api/v1/images/cancel/unknown-id")
        
        assert response.status_code == 200
        data = response.json()
        assert data["cancelled"] is False
