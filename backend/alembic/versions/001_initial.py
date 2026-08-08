"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2026-08-08 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # AI Agents
    op.create_table(
        'ai_agents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('agent_id', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('role', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('capabilities', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('config', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_active', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('agent_id'),
    )
    op.create_index('idx_agent_status', 'ai_agents', ['status'])
    op.create_index('idx_agent_created', 'ai_agents', ['created_at'])

    # AI Tasks
    op.create_table(
        'ai_tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.String(255), nullable=False),
        sa.Column('agent_id', sa.String(255), nullable=False),
        sa.Column('task_type', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('priority', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('parameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id'),
        sa.ForeignKeyConstraint(['agent_id'], ['ai_agents.agent_id'], ondelete='CASCADE'),
    )
    op.create_index('idx_task_status_agent', 'ai_tasks', ['status', 'agent_id'])

    # Conversations
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(255), nullable=False),
        sa.Column('agent_id', sa.String(255), nullable=True),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('provider', sa.String(50), nullable=True),
        sa.Column('model', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['agent_id'], ['ai_agents.agent_id'], ondelete='SET NULL'),
    )
    op.create_index('idx_conv_session', 'conversations', ['session_id', 'created_at'])

    # Chat Sessions
    op.create_table(
        'chat_sessions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(255), nullable=False),
        sa.Column('title', sa.String(500), nullable=True),
        sa.Column('agent_id', sa.String(255), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('session_id'),
        sa.ForeignKeyConstraint(['agent_id'], ['ai_agents.agent_id'], ondelete='SET NULL'),
    )

    # LLM Usage Logs
    op.create_table(
        'llm_usage_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('prompt_tokens', sa.Integer(), nullable=True),
        sa.Column('completion_tokens', sa.Integer(), nullable=True),
        sa.Column('total_tokens', sa.Integer(), nullable=True),
        sa.Column('estimated_cost_usd', sa.Float(), nullable=True),
        sa.Column('request_duration_ms', sa.Float(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_llm_usage_provider', 'llm_usage_logs', ['provider', 'created_at'])

    # System Metrics
    op.create_table(
        'system_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('metric_name', sa.String(255), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('labels', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('idx_metric_name_time', 'system_metrics', ['metric_name', 'created_at'])


def downgrade() -> None:
    op.drop_table('system_metrics')
    op.drop_table('llm_usage_logs')
    op.drop_table('chat_sessions')
    op.drop_table('conversations')
    op.drop_table('ai_tasks')
    op.drop_table('ai_agents')
