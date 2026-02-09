"""
MinIO Storage Client.

Provides functionality for uploading images to MinIO object storage.
Used for converting Base64 images from MCP responses to URLs.
"""
import base64
import io
import logging
from typing import Optional
from uuid import uuid4
from datetime import datetime

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False


logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================

class MinIOError(Exception):
    """Base exception for MinIO operations."""
    pass


class MinIOUploadError(MinIOError):
    """Error during image upload."""
    pass


class MinIOConnectionError(MinIOError):
    """Failed to connect to MinIO."""
    pass


class MinIOSizeLimitError(MinIOError):
    """Upload size exceeds limit."""
    pass


# ============================================================================
# MinIO Client
# ============================================================================

class MinIOClient:
    """Client for MinIO object storage.
    
    Handles uploading Base64-encoded images to MinIO and returning
    accessible URLs.
    
    Example:
        client = MinIOClient(
            endpoint="localhost:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            bucket="e-business",
        )
        url = await client.upload_base64_image(
            base64_data="iVBORw0KGgo...",
            mime_type="image/png",
        )
    """
    
    # MIME type to file extension mapping
    MIME_EXTENSIONS = {
        "image/png": ".png",
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/gif": ".gif",
        "image/webp": ".webp",
        "image/bmp": ".bmp",
    }
    
    # Default maximum upload size (10MB)
    DEFAULT_MAX_SIZE_BYTES = 10 * 1024 * 1024
    
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        secure: bool = False,
        max_size_bytes: Optional[int] = None,
    ):
        """Initialize MinIO client.
        
        Args:
            endpoint: MinIO server endpoint (host:port)
            access_key: MinIO access key
            secret_key: MinIO secret key
            bucket: Bucket name for image storage
            secure: Use HTTPS connection
            max_size_bytes: Maximum upload size in bytes (default: 10MB)
        """
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.bucket = bucket
        self.secure = secure
        self.max_size_bytes = max_size_bytes or self.DEFAULT_MAX_SIZE_BYTES
        self._client: Optional["Minio"] = None
    
    def _get_minio_client(self) -> "Minio":
        """Get or create MinIO client instance.
        
        Returns:
            Minio client instance
            
        Raises:
            MinIOConnectionError: If minio package is not installed
        """
        if not MINIO_AVAILABLE:
            raise MinIOConnectionError(
                "minio package is not installed. "
                "Install it with: pip install minio"
            )
        
        if self._client is None:
            self._client = Minio(
                self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure,
            )
        
        return self._client
    
    def is_base64(self, data: str) -> bool:
        """Check if a string is Base64 encoded.
        
        Args:
            data: String to check
            
        Returns:
            True if data appears to be Base64 encoded
        """
        if not data:
            return False
        
        # If it starts with http, it's a URL
        if data.startswith(("http://", "https://")):
            return False
        
        # Try to decode it
        try:
            # Remove data URL prefix if present
            if "," in data:
                data = data.split(",", 1)[1]
            
            decoded = base64.b64decode(data, validate=True)
            return len(decoded) > 0
        except Exception:
            return False
    
    def generate_object_name(
        self,
        mime_type: str,
        prefix: str = "images",
    ) -> str:
        """Generate a unique object name for the image.
        
        Args:
            mime_type: MIME type of the image
            prefix: Path prefix in the bucket
            
        Returns:
            Unique object path like "images/2024-01-15/abc123.png"
        """
        ext = self.MIME_EXTENSIONS.get(mime_type, ".png")
        date_path = datetime.utcnow().strftime("%Y-%m-%d")
        unique_id = uuid4().hex[:12]
        
        return f"{prefix}/{date_path}/{unique_id}{ext}"
    
    async def upload_base64_image(
        self,
        base64_data: str,
        mime_type: str = "image/png",
        prefix: str = "images",
    ) -> str:
        """Upload a Base64-encoded image to MinIO.
        
        Args:
            base64_data: Base64-encoded image data
            mime_type: MIME type of the image
            prefix: Path prefix in the bucket
            
        Returns:
            URL where the image can be accessed
            
        Raises:
            MinIOUploadError: If upload fails
        """
        # Decode Base64 data
        try:
            # Remove data URL prefix if present (e.g., "data:image/png;base64,")
            if "," in base64_data:
                base64_data = base64_data.split(",", 1)[1]
            
            image_bytes = base64.b64decode(base64_data)
        except Exception as e:
            raise MinIOUploadError(f"Failed to decode Base64 data: {e}") from e
        
        # Check size limit
        data_size = len(image_bytes)
        if data_size > self.max_size_bytes:
            size_mb = data_size / (1024 * 1024)
            limit_mb = self.max_size_bytes / (1024 * 1024)
            raise MinIOSizeLimitError(
                f"Image size ({size_mb:.2f}MB) exceeds limit ({limit_mb:.2f}MB)"
            )
        
        # Generate object name
        object_name = self.generate_object_name(mime_type, prefix)
        
        # Upload to MinIO
        try:
            client = self._get_minio_client()
            
            # Create BytesIO stream from decoded data
            data_stream = io.BytesIO(image_bytes)
            data_length = len(image_bytes)
            
            client.put_object(
                bucket_name=self.bucket,
                object_name=object_name,
                data=data_stream,
                length=data_length,
                content_type=mime_type,
            )
            
            logger.info(f"Uploaded image to MinIO: {object_name}")
            
        except Exception as e:
            raise MinIOUploadError(f"Failed to upload image to MinIO: {e}") from e
        
        # Construct URL
        protocol = "https" if self.secure else "http"
        url = f"{protocol}://{self.endpoint}/{self.bucket}/{object_name}"
        
        return url
    
    async def ensure_bucket_exists(self) -> None:
        """Ensure the configured bucket exists, create if not.
        
        Raises:
            MinIOConnectionError: If bucket operations fail
        """
        try:
            client = self._get_minio_client()
            
            if not client.bucket_exists(self.bucket):
                client.make_bucket(self.bucket)
                logger.info(f"Created MinIO bucket: {self.bucket}")
            else:
                logger.debug(f"MinIO bucket exists: {self.bucket}")
                
        except Exception as e:
            raise MinIOConnectionError(
                f"Failed to ensure bucket exists: {e}"
            ) from e
