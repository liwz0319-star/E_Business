"""
Tests for copywriting API endpoints.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient

from app.main import app


@pytest.fixture
def mock_copywriting_agent():
    """Mock CopywritingAgent."""
    with patch("app.interface.routes.copywriting.CopywritingAgent") as mock_cls:
        mock_instance = MagicMock()
        mock_instance.run_async = AsyncMock(return_value="test-workflow-id-123")
        mock_cls.return_value = mock_instance
        yield mock_cls, mock_instance


class TestCopywritingGenerateEndpoint:
    """Tests for POST /api/v1/copywriting/generate endpoint."""
    
    @pytest.mark.asyncio
    async def test_generate_success(self, mock_copywriting_agent):
        """Test successful copywriting generation request."""
        mock_cls, mock_instance = mock_copywriting_agent
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/copywriting/generate",
                json={
                    "productName": "Smart Watch Pro",
                    "features": ["GPS", "Heart rate"],
                    "brandGuidelines": "Professional tone"
                }
            )
        
        assert response.status_code == 202
        data = response.json()
        assert "workflowId" in data
        assert data["status"] == "started"
        assert "workflow initiated" in data["message"].lower()
    
    @pytest.mark.asyncio
    async def test_generate_validates_product_name_required(self):
        """Test that productName is required."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/copywriting/generate",
                json={
                    "features": ["Feature 1"]
                }
            )
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_generate_validates_features_required(self):
        """Test that features list is required."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/copywriting/generate",
                json={
                    "productName": "Test Product"
                }
            )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_generate_validates_features_not_empty(self):
        """Test that features list cannot be empty."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/copywriting/generate",
                json={
                    "productName": "Test Product",
                    "features": []
                }
            )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_generate_without_brand_guidelines(self, mock_copywriting_agent):
        """Test generation without optional brand guidelines."""
        mock_cls, mock_instance = mock_copywriting_agent
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/copywriting/generate",
                json={
                    "productName": "Test Product",
                    "features": ["Feature 1"]
                }
            )
        
        assert response.status_code == 202
        
        # Verify agent was called without brand_guidelines
        mock_instance.run_async.assert_called_once()
        call_kwargs = mock_instance.run_async.call_args.kwargs
        assert call_kwargs["brand_guidelines"] is None
    
    @pytest.mark.asyncio
    async def test_generate_calls_agent_with_correct_params(self, mock_copywriting_agent):
        """Test that endpoint passes correct parameters to agent."""
        mock_cls, mock_instance = mock_copywriting_agent
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            await client.post(
                "/api/v1/copywriting/generate",
                json={
                    "productName": "Smart Watch Pro",
                    "features": ["GPS", "Heart rate", "Battery"],
                    "brandGuidelines": "Modern style"
                }
            )
        
        mock_instance.run_async.assert_called_once()
        call_kwargs = mock_instance.run_async.call_args.kwargs
        assert call_kwargs["product_name"] == "Smart Watch Pro"
        assert call_kwargs["features"] == ["GPS", "Heart rate", "Battery"]
        assert call_kwargs["brand_guidelines"] == "Modern style"
    
    @pytest.mark.asyncio
    async def test_generate_returns_camel_case_response(self, mock_copywriting_agent):
        """Test that response uses camelCase."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/copywriting/generate",
                json={
                    "productName": "Test",
                    "features": ["F1"]
                }
            )
        
        data = response.json()
        assert "workflowId" in data  # camelCase, not workflow_id
        assert "status" in data
        assert "message" in data


class TestCopywritingDTOValidation:
    """Tests for DTO validation."""
    
    @pytest.mark.asyncio
    async def test_product_name_max_length(self):
        """Test product name max length validation."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/copywriting/generate",
                json={
                    "productName": "A" * 201,  # Over 200 chars
                    "features": ["F1"]
                }
            )
        
        assert response.status_code == 422
    
    @pytest.mark.asyncio
    async def test_brand_guidelines_max_length(self):
        """Test brand guidelines max length validation."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/copywriting/generate",
                json={
                    "productName": "Test",
                    "features": ["F1"],
                    "brandGuidelines": "B" * 1001  # Over 1000 chars
                }
            )
        
        assert response.status_code == 422
