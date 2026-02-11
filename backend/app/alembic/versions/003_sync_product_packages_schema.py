"""sync product_packages schema

Revision ID: 003
Revises: 002
Create Date: 2026-02-10

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Check if table exists
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'product_packages' not in tables:
        # Create table from scratch
        op.create_table(
            'product_packages',
            sa.Column('id', postgresql.UUID(), nullable=False),
            sa.Column('workflow_id', sa.String(length=255), nullable=False),
            sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
            sa.Column('stage', sa.String(length=50), nullable=False, server_default='init'),
            sa.Column('progress', sa.JSON(), nullable=True),
            sa.Column('input_data', sa.JSON(), nullable=True),
            sa.Column('analysis_data', sa.JSON(), nullable=True),
            sa.Column('artifacts', sa.JSON(), nullable=False, server_default='{}'),
            sa.Column('approval_status', sa.String(length=50), nullable=False, server_default='pending'),
            sa.Column('qa_report', sa.JSON(), nullable=True),
            sa.Column('user_id', postgresql.UUID(), nullable=False),
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('workflow_id')
        )
        op.create_index(op.f('ix_product_packages_workflow_id'), 'product_packages', ['workflow_id'], unique=True)
        op.create_index(op.f('ix_product_packages_user_id'), 'product_packages', ['user_id'], unique=False)
        op.create_index('ix_product_packages_status', 'product_packages', ['status'], unique=False)
    else:
        # Table exists - align schema
        # Add missing columns if they don't exist
        columns = [col['name'] for col in inspector.get_columns('product_packages')]

        if 'error_message' not in columns:
            op.add_column('product_packages', sa.Column('error_message', sa.Text(), nullable=True))

        if 'completed_at' not in columns:
            op.add_column('product_packages', sa.Column('completed_at', sa.DateTime(), nullable=True))

        # Ensure indexes exist
        indexes = inspector.get_indexes('product_packages')
        index_names = [idx['name'] for idx in indexes]

        if 'ix_product_packages_workflow_id' not in index_names:
            op.create_index(op.f('ix_product_packages_workflow_id'), 'product_packages', ['workflow_id'], unique=True)

        if 'ix_product_packages_user_id' not in index_names:
            op.create_index(op.f('ix_product_packages_user_id'), 'product_packages', ['user_id'], unique=False)

        # Note: user_id type migration would require custom migration script
        # This is a simplified version - in production you'd need to:
        # 1. Add new column user_id_new as UUID
        # 2. Migrate data from user_id (string) to user_id_new (UUID)
        # 3. Drop old column and rename new one


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if 'product_packages' in inspector.get_table_names():
        op.drop_index('ix_product_packages_status', table_name='product_packages')
        op.drop_index(op.f('ix_product_packages_user_id'), table_name='product_packages')
        op.drop_index(op.f('ix_product_packages_workflow_id'), table_name='product_packages')
        op.drop_table('product_packages')
