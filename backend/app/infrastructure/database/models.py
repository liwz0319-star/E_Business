"""
SQLAlchemy ORM Models

Database models that map to PostgreSQL tables.
"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Integer, String, Text, JSON, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.connection import Base


class UserModel(Base):
    """
    SQLAlchemy model for users table.
    
    Maps to the 'users' table in PostgreSQL.
    """
    
    __tablename__ = "users"
    
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.utcnow(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"


class VideoAssetModel(Base):
    """
    SQLAlchemy model for video_assets table.
    
    Stores metadata for generated images and videos.
    Despite the name "video_assets", this table stores both
    image and video assets as specified in the architecture.
    """
    
    __tablename__ = "video_assets"
    
    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    asset_uuid: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid4,
        server_default=text("gen_random_uuid()"),
        unique=True,
        index=True,
        nullable=False,
    )
    user_id: Mapped[Optional[UUID]] = mapped_column(
        UUID(as_uuid=True),
        nullable=True,
        index=True,
    )
    workflow_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        nullable=True,
        index=True,
    )
    asset_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="image",
    )
    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    original_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    provider: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="unknown",
    )
    width: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=512,
    )
    height: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=512,
    )
    metadata_json: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.utcnow(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<VideoAsset(id={self.id}, type={self.asset_type}, url={self.url[:50]}...)>"


class ProductPackageModel(Base):
    """产品包聚合根 - 工作流执行主记录"""
    __tablename__ = "product_packages"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )
    workflow_id: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )  # pending/running/completed/failed/approval_required
    stage: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="analysis",
    )  # analysis/copywriting/image_generation/video_generation/qa_review
    progress: Mapped[Optional[dict]] = mapped_column(
        JSON,
        default=lambda: {"percentage": 0, "current_step": "init"},
        nullable=True,
    )

    # 输入数据
    input_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )  # {image_url/background/options}

    # 分析结果
    analysis_data: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )  # {product_category/target_audience/key_selling_points}

    # 生成的工件引用
    artifacts: Mapped[dict] = mapped_column(
        JSON,
        default=lambda: {},
        nullable=False,
    )  # {copywriting: [], images: [], video: video_id}

    # HITL 相关
    approval_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )  # pending/approved/rejected
    qa_report: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )  # {score: 0.9, issues: [], suggestions: []}

    # 审计字段
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.utcnow(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
        nullable=False,
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
    )

    def __repr__(self) -> str:
        return f"<ProductPackage(id={self.id}, workflow_id={self.workflow_id}, status={self.status})>"

