"""create video_assets table

Revision ID: 002
Revises: 001
Create Date: 2026-02-07

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'video_assets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('asset_uuid', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=True),
        sa.Column('workflow_id', sa.String(length=36), nullable=True),
        sa.Column('asset_type', sa.String(length=50), nullable=False, server_default='image'),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('prompt', sa.Text(), nullable=False),
        sa.Column('original_prompt', sa.Text(), nullable=True),
        sa.Column('provider', sa.String(length=100), nullable=False, server_default='unknown'),
        sa.Column('width', sa.Integer(), nullable=False, server_default='512'),
        sa.Column('height', sa.Integer(), nullable=False, server_default='512'),
        sa.Column('metadata_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_uuid')
    )
    op.create_index(op.f('ix_video_assets_asset_uuid'), 'video_assets', ['asset_uuid'], unique=True)
    op.create_index(op.f('ix_video_assets_user_id'), 'video_assets', ['user_id'], unique=False)
    op.create_index(op.f('ix_video_assets_workflow_id'), 'video_assets', ['workflow_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_video_assets_workflow_id'), table_name='video_assets')
    op.drop_index(op.f('ix_video_assets_user_id'), table_name='video_assets')
    op.drop_index(op.f('ix_video_assets_asset_uuid'), table_name='video_assets')
    op.drop_table('video_assets')
