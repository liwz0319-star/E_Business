"""Create user_settings table for User Settings & Profile feature

Revision ID: 006
Revises: 005
Create Date: 2026-02-14

Story: 6-3 User Settings & Profile
- Create user_settings table with One-to-One relationship to users
- Store AI preferences (language, tone, aspect_ratio)
- Store integration status (shopify_config, amazon_config, tiktok_config)
- Cascade delete when user is deleted

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_settings table."""
    op.create_table(
        'user_settings',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False, server_default='en-US'),
        sa.Column('tone', sa.String(length=50), nullable=False, server_default='professional'),
        sa.Column('aspect_ratio', sa.String(length=10), nullable=False, server_default='1:1'),
        sa.Column('shopify_config', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{"connected": false}'),
        sa.Column('amazon_config', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{"connected": false}'),
        sa.Column('tiktok_config', postgresql.JSON(astext_type=sa.Text()), nullable=False, server_default='{"connected": false}'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('user_id')
    )

    # Create index on user_id for efficient lookups
    op.create_index(op.f('ix_user_settings_user_id'), 'user_settings', ['user_id'], unique=False)


def downgrade() -> None:
    """Drop user_settings table."""
    op.drop_index(op.f('ix_user_settings_user_id'), table_name='user_settings')
    op.drop_table('user_settings')
