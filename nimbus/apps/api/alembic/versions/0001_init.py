"""init schema

Revision ID: 0001_init
Revises:
Create Date: 2025-01-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa

revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'projects',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('api_key_id', sa.String(length=128), nullable=False, unique=True),
        sa.Column('api_key_hash', sa.LargeBinary(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_table(
        'events',
        sa.Column('id', sa.Uuid(), primary_key=True),
        sa.Column('project_id', sa.Uuid(), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('ts', sa.DateTime(timezone=False), nullable=False),
        sa.Column('props', sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column('user_id', sa.String(length=200), nullable=True),
        sa.Column('seq', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('ix_events_project_ts', 'events', ['project_id', 'ts'])
    op.create_index('ix_events_project_seq', 'events', ['project_id', 'seq'])

def downgrade():
    op.drop_index('ix_events_project_seq', table_name='events')
    op.drop_index('ix_events_project_ts', table_name='events')
    op.drop_table('events')
    op.drop_table('projects')
