"""
Tests for MinIO Client.

Tests Base64 image upload functionality for MCP integration.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
import base64

from app.infrastructure.storage.minio_client import (
    MinIOClient,
    MinIOUploadError,
    MinIOSizeLimitError,
)


class TestMinIOClient:
    """Test MinIO storage client."""
    
    @pytest.fixture
    def client(self):
        """Create MinIO client instance."""
        return MinIOClient(
            endpoint="localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            bucket="e-business",
        )
    
    def test_init_with_defaults(self, client):
        """Test client initialization with default values."""
        assert client.endpoint == "localhost:9000"
        assert client.bucket == "e-business"
        assert client.secure is False
        assert client.max_size_bytes == 10 * 1024 * 1024  # 10MB default
    
    def test_init_with_secure(self):
        """Test client initialization with secure connection."""
        client = MinIOClient(
            endpoint="minio.example.com",
            access_key="access",
            secret_key="secret",
            bucket="bucket",
            secure=True,
        )
        assert client.secure is True
    
    def test_init_with_custom_max_size(self):
        """Test client initialization with custom max size."""
        client = MinIOClient(
            endpoint="localhost:9000",
            access_key="access",
            secret_key="secret",
            bucket="bucket",
            max_size_bytes=5 * 1024 * 1024,  # 5MB
        )
        assert client.max_size_bytes == 5 * 1024 * 1024
    
    def test_is_base64(self, client):
        """Test Base64 detection."""
        # Valid Base64
        valid_b64 = base64.b64encode(b"test data").decode()
        assert client.is_base64(valid_b64) is True
        
        # URL (not Base64)
        assert client.is_base64("http://example.com/image.png") is False
        assert client.is_base64("https://example.com/image.png") is False
        
        # Empty string
        assert client.is_base64("") is False
        
        # Invalid Base64
        assert client.is_base64("not valid base64!!!") is False
    
    def test_generate_object_name(self, client):
        """Test object name generation."""
        name = client.generate_object_name("image/png")
        
        assert name.startswith("images/")
        assert name.endswith(".png")
        assert "/" in name
    
    def test_generate_object_name_jpeg(self, client):
        """Test object name generation for JPEG."""
        name = client.generate_object_name("image/jpeg")
        
        assert name.endswith(".jpg")
    
    @pytest.mark.asyncio
    async def test_upload_base64_image_success(self, client):
        """Test successful Base64 image upload."""
        # Create test image data
        test_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        b64_data = base64.b64encode(test_data).decode()
        
        with patch.object(client, '_get_minio_client') as mock_get_client:
            mock_minio = MagicMock()
            mock_get_client.return_value = mock_minio
            mock_minio.put_object.return_value = MagicMock()
            
            url = await client.upload_base64_image(
                b64_data,
                mime_type="image/png",
            )
            
            assert url.startswith("http://localhost:9000/e-business/images/")
            assert url.endswith(".png")
            mock_minio.put_object.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_upload_base64_image_with_secure(self):
        """Test URL generation with secure connection."""
        client = MinIOClient(
            endpoint="minio.example.com",
            access_key="access",
            secret_key="secret",
            bucket="bucket",
            secure=True,
        )
        
        test_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        b64_data = base64.b64encode(test_data).decode()
        
        with patch.object(client, '_get_minio_client') as mock_get_client:
            mock_minio = MagicMock()
            mock_get_client.return_value = mock_minio
            mock_minio.put_object.return_value = MagicMock()
            
            url = await client.upload_base64_image(b64_data, "image/png")
            
            assert url.startswith("https://")
    
    @pytest.mark.asyncio
    async def test_upload_base64_image_decode_error(self, client):
        """Test error handling for invalid Base64."""
        with pytest.raises(MinIOUploadError) as exc_info:
            await client.upload_base64_image(
                "not valid base64 content!!!",
                mime_type="image/png",
            )
        
        assert "decode" in str(exc_info.value).lower()
    
    @pytest.mark.asyncio
    async def test_upload_base64_image_upload_error(self, client):
        """Test error handling for upload failure."""
        test_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        b64_data = base64.b64encode(test_data).decode()
        
        with patch.object(client, '_get_minio_client') as mock_get_client:
            mock_minio = MagicMock()
            mock_get_client.return_value = mock_minio
            mock_minio.put_object.side_effect = Exception("Connection refused")
            
            with pytest.raises(MinIOUploadError) as exc_info:
                await client.upload_base64_image(b64_data, "image/png")
            
            assert "upload" in str(exc_info.value).lower()


class TestMinIOSizeLimit:
    """Test MinIO upload size limit functionality."""
    
    @pytest.fixture
    def small_limit_client(self):
        """Create MinIO client with small size limit for testing."""
        return MinIOClient(
            endpoint="localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            bucket="e-business",
            max_size_bytes=1024,  # 1KB limit for testing
        )
    
    @pytest.mark.asyncio
    async def test_upload_exceeds_size_limit(self, small_limit_client):
        """Test that upload exceeding size limit raises error."""
        # Create data larger than 1KB limit
        large_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 2000  # ~2KB
        b64_data = base64.b64encode(large_data).decode()
        
        with pytest.raises(MinIOSizeLimitError) as exc_info:
            await small_limit_client.upload_base64_image(
                b64_data,
                mime_type="image/png",
            )
        
        assert "exceeds limit" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_upload_within_size_limit(self, small_limit_client):
        """Test that upload within size limit succeeds."""
        # Create data smaller than 1KB limit
        small_data = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # ~100 bytes
        b64_data = base64.b64encode(small_data).decode()
        
        with patch.object(small_limit_client, '_get_minio_client') as mock_get_client:
            mock_minio = MagicMock()
            mock_get_client.return_value = mock_minio
            mock_minio.put_object.return_value = MagicMock()
            
            url = await small_limit_client.upload_base64_image(
                b64_data,
                mime_type="image/png",
            )
            
            assert url.startswith("http://")
            mock_minio.put_object.assert_called_once()
    
    def test_default_size_limit(self):
        """Test default size limit is 10MB."""
        client = MinIOClient(
            endpoint="localhost:9000",
            access_key="access",
            secret_key="secret",
            bucket="bucket",
        )
        assert client.max_size_bytes == 10 * 1024 * 1024


class TestMinIOExceptions:
    """Test MinIO exceptions."""
    
    def test_minio_upload_error(self):
        """Test MinIOUploadError."""
        error = MinIOUploadError("Failed to upload image")
        assert "Failed to upload" in str(error)
    
    def test_minio_size_limit_error(self):
        """Test MinIOSizeLimitError."""
        error = MinIOSizeLimitError("Image size exceeds limit")
        assert "exceeds limit" in str(error)
