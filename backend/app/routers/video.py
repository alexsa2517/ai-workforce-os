"""
Video Router - API endpoints for AI Video Generation (REAL)
Supports full 5-phase video production with DALL-E 3, TTS, and ffmpeg.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.core.schemas import (
    VideoProjectCreate, VideoProjectUpdate, VideoProjectResponse,
    VideoProjectGlobalDef, VideoClipResponse, VideoAssetInfo,
    VideoGenerateRequest, VideoGenerationStatus,
)
from app.core.config import settings
from app.middleware.error_handler import APIError
from app.middleware.rate_limit import limiter
from app.database.session import get_db
from app.database.models import VideoProject, VideoClip, VideoAsset
from app.services.video.pipeline import VideoPipeline

logger = logging.getLogger("ai_workforce.routers.video")

router = APIRouter(prefix="/api/v1/video", tags=["Video Generation"])
pipeline = VideoPipeline()


# ============================================================
# Project Management
# ============================================================

@router.post("/projects", response_model=VideoProjectResponse, status_code=201)
@limiter.limit(settings.RATE_LIMIT)
async def create_project(
    request_data: VideoProjectCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create a new video project (Phase 1: Initial)."""
    try:
        project = await pipeline.create_project(
            db=db,
            title=request_data.title,
            description=request_data.description,
            goal=request_data.goal,
            target_audience=request_data.target_audience,
            duration_target=request_data.duration_target,
            aspect_ratio=request_data.aspect_ratio,
            visual_style=request_data.visual_style,
            language=request_data.language,
        )
        return await _project_to_response(db, project)
    except Exception as e:
        logger.error(f"Failed to create project: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create project: {str(e)}")


@router.get("/projects", response_model=List[VideoProjectResponse])
async def list_projects(
    db: AsyncSession = Depends(get_db),
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
):
    """List all video projects."""
    query = select(VideoProject).offset(skip).limit(limit).order_by(desc(VideoProject.created_at))

    if status:
        query = query.where(VideoProject.status == status)

    result = await db.execute(query)
    projects = result.scalars().all()

    return [await _project_to_response(db, p) for p in projects]


@router.get("/projects/{project_id}", response_model=VideoProjectResponse)
async def get_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Get video project details."""
    result = await db.execute(select(VideoProject).where(VideoProject.project_id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise APIError(
            message=f"Project '{project_id}' not found",
            status_code=404,
            error_code="project_not_found",
        )

    return await _project_to_response(db, project)


@router.put("/projects/{project_id}", response_model=VideoProjectResponse)
async def update_project(
    project_id: str,
    update: VideoProjectUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update video project requirements."""
    result = await db.execute(select(VideoProject).where(VideoProject.project_id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise APIError(
            message=f"Project '{project_id}' not found",
            status_code=404,
            error_code="project_not_found",
        )

    update_data = update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    await db.commit()
    await db.refresh(project)

    return await _project_to_response(db, project)


@router.delete("/projects/{project_id}", status_code=204)
async def delete_project(project_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a video project and all associated data."""
    result = await db.execute(select(VideoProject).where(VideoProject.project_id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise APIError(
            message=f"Project '{project_id}' not found",
            status_code=404,
            error_code="project_not_found",
        )

    await db.delete(project)
    await db.commit()

    logger.info(f"Deleted video project: {project_id}")
    return None


# ============================================================
# Phase 2: Global Definitions
# ============================================================

@router.post("/projects/{project_id}/global-def", response_model=VideoProjectResponse)
async def set_global_definitions(
    project_id: str,
    global_def: VideoProjectGlobalDef,
    db: AsyncSession = Depends(get_db),
):
    """Set global style definitions (Phase 2)."""
    try:
        project = await pipeline.set_global_definitions(db, project_id, global_def)
        return await _project_to_response(db, project)
    except ValueError as e:
        raise APIError(message=str(e), status_code=404, error_code="project_not_found")
    except Exception as e:
        logger.error(f"Failed to set global definitions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Phase 3: Clip Planning
# ============================================================

@router.post("/projects/{project_id}/plan-clips", response_model=VideoProjectResponse)
async def plan_clips(
    project_id: str,
    provider: Optional[str] = "openai",
    db: AsyncSession = Depends(get_db),
):
    """Generate clip plans using LLM (Phase 3)."""
    try:
        await pipeline.plan_clips(db, project_id, provider)

        result = await db.execute(select(VideoProject).where(VideoProject.project_id == project_id))
        project = result.scalar_one()
        return await _project_to_response(db, project)

    except ValueError as e:
        raise APIError(message=str(e), status_code=400, error_code="planning_error")
    except Exception as e:
        logger.error(f"Failed to plan clips: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/bgm-blueprint")
async def generate_bgm_blueprint(
    project_id: str,
    provider: Optional[str] = "openai",
    db: AsyncSession = Depends(get_db),
):
    """Generate BGM emotional arc blueprint."""
    try:
        blueprint = await pipeline.generate_bgm_blueprint(db, project_id, provider)
        return blueprint.model_dump()
    except ValueError as e:
        raise APIError(message=str(e), status_code=400, error_code="bgm_error")
    except Exception as e:
        logger.error(f"Failed to generate BGM blueprint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Phase 4: Reference Images (REAL - DALL-E 3)
# ============================================================

@router.post("/projects/{project_id}/reference-images")
async def generate_reference_images(
    project_id: str,
    elements: List[dict],
    db: AsyncSession = Depends(get_db),
):
    """Generate reference images using DALL-E 3 (Phase 4)."""
    try:
        assets = await pipeline.generate_reference_images(db, project_id, elements)
        return {
            "project_id": project_id,
            "assets_generated": len(assets),
            "assets": [
                {
                    "asset_id": a.asset_id,
                    "asset_type": a.asset_type,
                    "asset_role": a.asset_role,
                    "url": a.url,
                    "local_path": a.local_path,
                    "prompt_used": a.prompt_used,
                }
                for a in assets
            ],
        }
    except ValueError as e:
        raise APIError(message=str(e), status_code=404, error_code="project_not_found")
    except Exception as e:
        logger.error(f"Failed to generate reference images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Phase 5: REAL Execution & Assembly
# ============================================================

@router.post("/projects/{project_id}/generate", response_model=VideoGenerationStatus)
async def execute_generation(
    project_id: str,
    provider: Optional[str] = "openai",
    db: AsyncSession = Depends(get_db),
):
    """
    Execute REAL video generation for all clips (Phase 5).
    Uses DALL-E 3 for images, OpenAI TTS for audio, ffmpeg for video.
    """
    try:
        status = await pipeline.execute_generation(db, project_id, provider)
        return status
    except ValueError as e:
        raise APIError(message=str(e), status_code=404, error_code="project_not_found")
    except Exception as e:
        logger.error(f"Failed to execute generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/assemble", response_model=VideoProjectResponse)
async def assemble_video(project_id: str, db: AsyncSession = Depends(get_db)):
    """Assemble all clips into final video with ffmpeg."""
    try:
        project = await pipeline.assemble_video(db, project_id)
        return await _project_to_response(db, project)
    except ValueError as e:
        raise APIError(message=str(e), status_code=400, error_code="assembly_error")
    except Exception as e:
        logger.error(f"Failed to assemble video: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Full Pipeline (One-shot)
# ============================================================

@router.post("/projects/{project_id}/run-pipeline", response_model=VideoGenerationStatus)
async def run_full_pipeline(
    project_id: str,
    global_def: VideoProjectGlobalDef,
    provider: Optional[str] = "openai",
    db: AsyncSession = Depends(get_db),
):
    """
    Run the complete video generation pipeline (Phases 2-5) in one call.
    Generates REAL video with DALL-E 3 images + TTS + ffmpeg.
    """
    try:
        status = await pipeline.run_full_pipeline(db, project_id, global_def, provider)
        return status
    except ValueError as e:
        raise APIError(message=str(e), status_code=404, error_code="project_not_found")
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# Clip & Asset Management
# ============================================================

@router.get("/projects/{project_id}/clips", response_model=List[VideoClipResponse])
async def list_clips(project_id: str, db: AsyncSession = Depends(get_db)):
    """List all clips in a project."""
    result = await db.execute(
        select(VideoProject).where(VideoProject.project_id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise APIError(
            message=f"Project '{project_id}' not found",
            status_code=404,
            error_code="project_not_found",
        )

    clips_result = await db.execute(
        select(VideoClip)
        .where(VideoClip.project_id == project.id)
        .order_by(VideoClip.sequence_number)
    )
    clips = clips_result.scalars().all()

    return [
        VideoClipResponse(
            clip_id=c.clip_id,
            sequence_number=c.sequence_number,
            narrative_purpose=c.narrative_purpose,
            pacing=c.pacing,
            scene=c.scene,
            content_action=c.content_action,
            transition_description=c.transition_description,
            target_duration=c.target_duration,
            camera_movement=c.camera_movement,
            status=c.status,
            video_url=c.video_url,
            actual_duration=c.actual_duration,
            created_at=c.created_at,
        )
        for c in clips
    ]


@router.get("/projects/{project_id}/assets", response_model=List[VideoAssetInfo])
async def list_assets(project_id: str, db: AsyncSession = Depends(get_db)):
    """List all assets in a project."""
    result = await db.execute(
        select(VideoProject).where(VideoProject.project_id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise APIError(
            message=f"Project '{project_id}' not found",
            status_code=404,
            error_code="project_not_found",
        )

    assets_result = await db.execute(
        select(VideoAsset).where(VideoAsset.project_id == project.id)
    )
    assets = assets_result.scalars().all()

    return [
        VideoAssetInfo(
            asset_id=a.asset_id,
            asset_type=a.asset_type,
            asset_role=a.asset_role,
            url=a.url,
            local_path=a.local_path,
            prompt_used=a.prompt_used,
            created_at=a.created_at,
        )
        for a in assets
    ]


# ============================================================
# Download/Stream Final Video
# ============================================================

@router.get("/projects/{project_id}/download")
async def download_video(project_id: str, db: AsyncSession = Depends(get_db)):
    """Download the final generated video."""
    result = await db.execute(
        select(VideoProject).where(VideoProject.project_id == project_id)
    )
    project = result.scalar_one_or_none()

    if not project:
        raise APIError(
            message=f"Project '{project_id}' not found",
            status_code=404,
            error_code="project_not_found",
        )

    if not project.output_path or not os.path.exists(project.output_path):
        raise APIError(
            message="Video not ready or not found",
            status_code=404,
            error_code="video_not_ready",
        )

    from fastapi.responses import FileResponse

    return FileResponse(
        path=project.output_path,
        filename=f"{project.title.replace(' ', '_')}.mp4",
        media_type="video/mp4",
    )


# ============================================================
# Helpers
# ============================================================

async def _project_to_response(db: AsyncSession, project: VideoProject) -> VideoProjectResponse:
    """Convert VideoProject model to response schema."""
    clips_result = await db.execute(
        select(VideoClip)
        .where(VideoClip.project_id == project.id)
        .order_by(VideoClip.sequence_number)
    )
    clips = clips_result.scalars().all()

    assets_result = await db.execute(
        select(VideoAsset).where(VideoAsset.project_id == project.id)
    )
    assets = assets_result.scalars().all()

    return VideoProjectResponse(
        project_id=project.project_id,
        title=project.title,
        description=project.description,
        status=project.status,
        current_phase=project.current_phase,
        progress_percent=project.progress_percent,
        aspect_ratio=project.aspect_ratio,
        duration_target=project.duration_target,
        output_url=project.output_url,
        style_spec=project.style_spec,
        voice_profiles=project.voice_profiles,
        bgm_source=project.bgm_source,
        created_at=project.created_at,
        updated_at=project.updated_at,
        clips=[
            VideoClipResponse(
                clip_id=c.clip_id,
                sequence_number=c.sequence_number,
                narrative_purpose=c.narrative_purpose,
                pacing=c.pacing,
                scene=c.scene,
                content_action=c.content_action,
                transition_description=c.transition_description,
                target_duration=c.target_duration,
                camera_movement=c.camera_movement,
                status=c.status,
                video_url=c.video_url,
                actual_duration=c.actual_duration,
                created_at=c.created_at,
            )
            for c in clips
        ],
        assets=[
            VideoAssetInfo(
                asset_id=a.asset_id,
                asset_type=a.asset_type,
                asset_role=a.asset_role,
                url=a.url,
                local_path=a.local_path,
                prompt_used=a.prompt_used,
                created_at=a.created_at,
            )
            for a in assets
        ],
    )
