"""Add title and content columns to video_assets for Asset Gallery

Revision ID: 005
Revises: 004
Create Date: 2026-02-13

Story: 6-2 Asset Gallery API
- Add title column (String(255), nullable) for asset titles
- Add content column (Text, nullable) for text/copy assets
- Modify url column to nullable to support text-only assets

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add title column for asset display names
    op.add_column(
        'video_assets',
        sa.Column('title', sa.String(length=255), nullable=True)
    )

    # Add content column for text/copy assets
    op.add_column(
        'video_assets',
        sa.Column('content', sa.Text(), nullable=True)
    )

    # Modify url column to nullable to support text-only assets
    op.alter_column(
        'video_assets',
        'url',
        existing_type=sa.Text(),
        nullable=True
    )


def downgrade() -> None:
    # Revert url to non-nullable (warning: may fail if null urls exist)
    op.alter_column(
        'video_assets',
        'url',
        existing_type=sa.Text(),
        nullable=False
    )

    # Remove content column
    op.drop_column('video_assets', 'content')

    # Remove title column
    op.drop_column('video_assets', 'title')
