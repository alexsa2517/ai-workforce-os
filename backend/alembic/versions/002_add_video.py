"""Add video generation tables

Revision ID: 002
Revises: 001
Create Date: 2026-08-08 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Video Projects
    op.create_table(
        'video_projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.String(255), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('goal', sa.Text(), nullable=True),
        sa.Column('target_audience', sa.Text(), nullable=True),
        sa.Column('duration_target', sa.Integer(), nullable=True),
        sa.Column('aspect_ratio', sa.String(20), nullable=True),
        sa.Column('visual_style', sa.Text(), nullable=True),
        sa.Column('language', sa.String(50), nullable=True),
        sa.Column('style_spec', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('voice_profiles', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('bgm_source', sa.String(50), nullable=True),
        sa.Column('bgm_properties', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('current_phase', sa.String(50), nullable=True),
        sa.Column('progress_percent', sa.Integer(), nullable=True),
        sa.Column('output_url', sa.String(1000), nullable=True),
        sa.Column('output_path', sa.String(1000), nullable=True),
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('project_id'),
    )
    op.create_index('idx_video_project_status', 'video_projects', ['status'])
    op.create_index('idx_video_project_created', 'video_projects', ['created_at'])

    # Video Clips
    op.create_table(
        'video_clips',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('clip_id', sa.String(255), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('sequence_number', sa.Integer(), nullable=False),
        sa.Column('narrative_purpose', sa.String(50), nullable=True),
        sa.Column('pacing', sa.String(20), nullable=True),
        sa.Column('scene', sa.Text(), nullable=True),
        sa.Column('content_action', sa.Text(), nullable=True),
        sa.Column('transition_description', sa.Text(), nullable=True),
        sa.Column('target_duration', sa.Float(), nullable=True),
        sa.Column('camera_movement', sa.String(50), nullable=True),
        sa.Column('first_keyframe_framing', sa.Text(), nullable=True),
        sa.Column('first_keyframe_visible_content', sa.Text(), nullable=True),
        sa.Column('inter_clip_boundary', sa.String(20), nullable=True),
        sa.Column('first_keyframe_reuse', sa.Boolean(), nullable=True),
        sa.Column('on_screen_dialogue', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('sound_effects', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('bgm_cue', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('narration_cue', sa.Text(), nullable=True),
        sa.Column('narration_budget', sa.Float(), nullable=True),
        sa.Column('status', sa.String(50), nullable=True),
        sa.Column('video_url', sa.String(1000), nullable=True),
        sa.Column('video_path', sa.String(1000), nullable=True),
        sa.Column('actual_duration', sa.Float(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('clip_id'),
        sa.ForeignKeyConstraint(['project_id'], ['video_projects.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_video_clip_project', 'video_clips', ['project_id', 'sequence_number'])
    op.create_index('idx_video_clip_status', 'video_clips', ['status'])

    # Video Assets
    op.create_table(
        'video_assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asset_id', sa.String(255), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('clip_id', sa.Integer(), nullable=True),
        sa.Column('asset_type', sa.String(50), nullable=False),
        sa.Column('asset_role', sa.String(50), nullable=True),
        sa.Column('url', sa.String(1000), nullable=True),
        sa.Column('local_path', sa.String(1000), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=True),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('prompt_used', sa.Text(), nullable=True),
        sa.Column('generation_params', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('asset_id'),
        sa.ForeignKeyConstraint(['project_id'], ['video_projects.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['clip_id'], ['video_clips.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_video_asset_project', 'video_assets', ['project_id', 'asset_type'])
    op.create_index('idx_video_asset_clip', 'video_assets', ['clip_id', 'asset_type'])


def downgrade() -> None:
    op.drop_table('video_assets')
    op.drop_table('video_clips')
    op.drop_table('video_projects')
