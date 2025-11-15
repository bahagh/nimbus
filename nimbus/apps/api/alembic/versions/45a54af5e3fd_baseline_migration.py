"""baseline migration

Revision ID: 45a54af5e3fd
Revises: 
Create Date: 2025-11-13 15:42:27.590908

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '45a54af5e3fd'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('email', sa.String(length=200), nullable=False),
        sa.Column('hashed_password', sa.LargeBinary(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('api_key_id', sa.String(length=128), nullable=False),
        sa.Column('api_key_hash', sa.LargeBinary(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('api_key_id')
    )

    # Create events table
    op.create_table(
        'events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('project_id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('ts', sa.DateTime(timezone=False), nullable=False),
        sa.Column('props', sa.JSON(), nullable=False),
        sa.Column('user_id', sa.String(length=200), nullable=True),
        sa.Column('seq', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_events_project_id', 'events', ['project_id'])
    op.create_index('ix_events_name', 'events', ['name'])
    op.create_index('ix_events_ts', 'events', ['ts'])
    op.create_index('ix_events_user_id', 'events', ['user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_events_user_id', table_name='events')
    op.drop_index('ix_events_ts', table_name='events')
    op.drop_index('ix_events_name', table_name='events')
    op.drop_index('ix_events_project_id', table_name='events')
    op.drop_table('events')
    op.drop_table('projects')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
