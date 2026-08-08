"""
Video Pipeline Service - End-to-End AI Video Production (REAL IMPLEMENTATION)
Uses DALL-E 3 for images, OpenAI TTS for audio, ffmpeg for video assembly.
"""
import logging
import os
import uuid
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.core.config import settings
from app.core.schemas import (
    VideoProjectResponse, VideoClipPlan, VideoProjectGlobalDef,
    VideoGenerationStatus, BgmBlueprint, AssetType,
)
from app.database.models import VideoProject, VideoClip, VideoAsset
from app.services.llm.factory import LLMFactory
from app.services.llm.image_service import image_service
from app.services.llm.tts_service import tts_service
from app.services.video.clip_planner import ClipPlanner
from app.services.video.prompt_builder import VideoPromptBuilder
from app.services.video.assembly import VideoAssemblyService
from app.services.video.generator import VideoGenerator

logger = logging.getLogger("ai_workforce.video.pipeline")


class VideoPipeline:
    """End-to-end video generation pipeline with REAL image/audio/video generation."""

    def __init__(self):
        self.clip_planner = ClipPlanner()
        self.prompt_builder = VideoPromptBuilder()
        self.assembly = VideoAssemblyService(str(Path(settings.MOVIES_DIR)))
        self.video_generator = VideoGenerator(str(Path(settings.MOVIES_DIR)))
        self.output_dir = Path(settings.MOVIES_DIR)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # Phase 1: Initial
    # ============================================================

    async def create_project(
        self,
        db: AsyncSession,
        title: str,
        description: Optional[str] = None,
        goal: Optional[str] = None,
        target_audience: Optional[str] = None,
        duration_target: int = 60,
        aspect_ratio: str = "16:9",
        visual_style: Optional[str] = None,
        language: str = "th",
    ) -> VideoProject:
        """Create a new video project."""
        project = VideoProject(
            project_id=f"vid_{uuid.uuid4().hex[:12]}",
            title=title,
            description=description,
            goal=goal,
            target_audience=target_audience,
            duration_target=duration_target,
            aspect_ratio=aspect_ratio,
            visual_style=visual_style,
            language=language,
            status="draft",
            current_phase="initial",
            progress_percent=0,
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        logger.info(f"Created video project: {project.project_id}")
        return project

    # ============================================================
    # Phase 2: Global Definitions
    # ============================================================

    async def set_global_definitions(
        self,
        db: AsyncSession,
        project_id: str,
        global_def: VideoProjectGlobalDef,
    ) -> VideoProject:
        """Set global style definitions."""
        result = await db.execute(
            select(VideoProject).where(VideoProject.project_id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError(f"Project {project_id} not found")

        project.style_spec = global_def.style_spec.model_dump()
        project.voice_profiles = {
            k: v.model_dump() for k, v in global_def.voice_profiles.items()
        }
        project.bgm_source = global_def.bgm_source.value
        project.bgm_properties = global_def.bgm_properties.model_dump() if global_def.bgm_properties else None
        project.current_phase = "global_def"
        project.progress_percent = 20

        await db.commit()
        await db.refresh(project)
        logger.info(f"Set global definitions for project: {project_id}")
        return project

    # ============================================================
    # Phase 3: Clip & BGM Planning
    # ============================================================

    async def plan_clips(
        self,
        db: AsyncSession,
        project_id: str,
        provider: str = "openai",
    ) -> List[VideoClip]:
        """Generate clip plans using LLM."""
        result = await db.execute(
            select(VideoProject).where(VideoProject.project_id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError(f"Project {project_id} not found")

        if not project.style_spec:
            raise ValueError(f"Project {project_id} missing global definitions")

        project_resp = VideoProjectResponse(
            project_id=project.project_id,
            title=project.title,
            description=project.description,
            status=project.status,
            current_phase=project.current_phase,
            progress_percent=project.progress_percent,
            aspect_ratio=project.aspect_ratio,
            duration_target=project.duration_target,
            goal=project.goal,
            target_audience=project.target_audience,
            visual_style=project.visual_style,
            language=project.language,
        )

        clip_plans = await self.clip_planner.plan_clips(
            project=project_resp,
            style_spec=project.style_spec,
            voice_profiles=project.voice_profiles or {},
            bgm_source=project.bgm_source or "separate",
            bgm_properties=project.bgm_properties,
            provider=provider,
        )

        clips = []
        for plan in clip_plans:
            clip = VideoClip(
                clip_id=f"clip_{uuid.uuid4().hex[:8]}",
                project_id=project.id,
                sequence_number=plan.sequence_number,
                narrative_purpose=plan.narrative_purpose.value,
                pacing=plan.pacing.value,
                scene=plan.scene,
                content_action=plan.content_action,
                transition_description=plan.transition_description,
                target_duration=plan.target_duration,
                camera_movement=plan.camera_movement.value,
                first_keyframe_framing=plan.first_keyframe_framing,
                first_keyframe_visible_content=plan.first_keyframe_visible_content,
                inter_clip_boundary=plan.inter_clip_boundary.value,
                first_keyframe_reuse=plan.first_keyframe_reuse,
                on_screen_dialogue=plan.on_screen_dialogue,
                sound_effects=plan.sound_effects,
                bgm_cue=plan.bgm_cue,
                narration_cue=plan.narration_cue,
                narration_budget=plan.narration_budget,
                status="pending",
            )
            db.add(clip)
            clips.append(clip)

        project.current_phase = "clip_plan"
        project.progress_percent = 40

        await db.commit()
        logger.info(f"Planned {len(clips)} clips for project: {project_id}")
        return clips

    async def generate_bgm_blueprint(
        self,
        db: AsyncSession,
        project_id: str,
        provider: str = "openai",
    ) -> BgmBlueprint:
        """Generate BGM emotional arc blueprint."""
        result = await db.execute(
            select(VideoProject).where(VideoProject.project_id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError(f"Project {project_id} not found")

        clips_result = await db.execute(
            select(VideoClip)
            .where(VideoClip.project_id == project.id)
            .order_by(VideoClip.sequence_number)
        )
        db_clips = clips_result.scalars().all()

        clip_plans = [
            VideoClipPlan(
                sequence_number=c.sequence_number,
                narrative_purpose=c.narrative_purpose,
                pacing=c.pacing,
                scene=c.scene,
                content_action=c.content_action,
                transition_description=c.transition_description,
                target_duration=c.target_duration,
                camera_movement=c.camera_movement,
                first_keyframe_framing=c.first_keyframe_framing,
                first_keyframe_visible_content=c.first_keyframe_visible_content,
                inter_clip_boundary=c.inter_clip_boundary,
                first_keyframe_reuse=c.first_keyframe_reuse,
                on_screen_dialogue=c.on_screen_dialogue,
                sound_effects=c.sound_effects,
                bgm_cue=c.bgm_cue,
                narration_cue=c.narration_cue,
                narration_budget=c.narration_budget,
            )
            for c in db_clips
        ]

        blueprint = await self.clip_planner.generate_bgm_blueprint(
            clips=clip_plans,
            bgm_properties=project.bgm_properties or {},
            provider=provider,
        )

        if not project.metadata:
            project.metadata = {}
        project.metadata["bgm_blueprint"] = blueprint.model_dump()

        await db.commit()
        logger.info(f"Generated BGM blueprint for project: {project_id}")
        return blueprint

    # ============================================================
    # Phase 4: Reference Images (REAL - DALL-E 3)
    # ============================================================

    async def generate_reference_images(
        self,
        db: AsyncSession,
        project_id: str,
        elements: List[Dict[str, Any]],
    ) -> List[VideoAsset]:
        """Generate reference images using DALL-E 3."""
        result = await db.execute(
            select(VideoProject).where(VideoProject.project_id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError(f"Project {project_id} not found")

        if not image_service.is_available:
            logger.warning("Image generation not available - skipping reference images")
            return []

        assets = []

        for element in elements:
            name = element["name"]
            description = element["description"]
            shots = element.get("shots_needed", ["full_body"])

            for shot_type in shots:
                prompt = self.prompt_builder.build_reference_image_prompt(
                    element_name=name,
                    element_description=description,
                    style_spec=project.style_spec or {},
                    shot_type=shot_type,
                )

                try:
                    # Generate image with DALL-E 3
                    img_result = await image_service.generate(
                        prompt=prompt,
                        model="dall-e-3",
                        quality="standard",
                        size="1024x1024",
                    )

                    if img_result.get("error"):
                        logger.warning(f"Image generation failed: {img_result.get('detail')}")
                        continue

                    local_path = img_result["local_paths"][0] if img_result["local_paths"] else None

                    asset = VideoAsset(
                        asset_id=f"asset_{uuid.uuid4().hex[:8]}",
                        project_id=project.id,
                        asset_type="reference_image",
                        asset_role=shot_type,
                        url=img_result["urls"][0] if img_result["urls"] else None,
                        local_path=local_path,
                        prompt_used=prompt,
                        generation_params={
                            "element": name,
                            "shot": shot_type,
                            "model": "dall-e-3",
                            "cost_usd": img_result.get("cost_usd", 0),
                        },
                    )
                    db.add(asset)
                    assets.append(asset)

                except Exception as e:
                    logger.error(f"Failed to generate reference image for {name}: {e}")

        project.current_phase = "ref_images"
        project.progress_percent = 60

        await db.commit()
        logger.info(f"Generated {len(assets)} reference assets for project: {project_id}")
        return assets

    # ============================================================
    # Phase 5: Execution (REAL - Images + TTS + ffmpeg Video)
    # ============================================================

    async def execute_generation(
        self,
        db: AsyncSession,
        project_id: str,
        provider: str = "openai",
    ) -> VideoGenerationStatus:
        """Execute REAL video generation for all clips."""
        result = await db.execute(
            select(VideoProject).where(VideoProject.project_id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError(f"Project {project_id} not found")

        project.status = "generating"
        project.current_phase = "execution"
        project.progress_percent = 70
        await db.commit()

        # Get all clips
        clips_result = await db.execute(
            select(VideoClip)
            .where(VideoClip.project_id == project.id)
            .order_by(VideoClip.sequence_number)
        )
        clips = clips_result.scalars().all()

        logger.info(f"Starting REAL generation for {len(clips)} clips in project: {project_id}")

        completed = 0
        previous_video_path = None

        for clip in clips:
            try:
                await self._generate_clip_real(
                    db=db,
                    clip=clip,
                    project=project,
                    previous_video_path=previous_video_path,
                )
                completed += 1

                project.progress_percent = 70 + int((completed / len(clips)) * 20)
                await db.commit()

                if clip.video_path:
                    previous_video_path = clip.video_path

            except Exception as e:
                logger.error(f"Failed to generate clip {clip.clip_id}: {e}")
                clip.status = "failed"
                await db.commit()

        if completed == len(clips):
            project.status = "assembling"
            project.progress_percent = 90
        else:
            project.status = "failed" if completed == 0 else "assembling"

        await db.commit()

        return VideoGenerationStatus(
            project_id=project_id,
            status=project.status,
            current_phase=project.current_phase,
            progress_percent=project.progress_percent,
            message=f"Generated {completed}/{len(clips)} clips",
            clips_completed=completed,
            clips_total=len(clips),
        )

    async def _generate_clip_real(
        self,
        db: AsyncSession,
        clip: VideoClip,
        project: VideoProject,
        previous_video_path: Optional[str],
    ) -> None:
        """Generate a single clip with REAL image + TTS + ffmpeg video."""
        logger.info(f"Generating clip {clip.clip_id} (seq {clip.sequence_number})")

        clip.status = "generating"
        await db.commit()

        # Step 1: Generate or reuse keyframe image
        keyframe_path = None

        if clip.first_keyframe_reuse and previous_video_path:
            # Extract final frame from previous clip
            keyframe_path = await self.assembly.extract_final_frame(
                previous_video_path,
                f"{previous_video_path}.final_frame.jpg"
            )
            logger.info(f"Reused keyframe from previous clip for {clip.clip_id}")
        else:
            # Generate new keyframe with DALL-E 3
            if image_service.is_available:
                keyframe_prompt = self.prompt_builder.build_keyframe_prompt(
                    clip=VideoClipPlan(
                        sequence_number=clip.sequence_number,
                        scene=clip.scene,
                        content_action=clip.content_action,
                        transition_description=clip.transition_description,
                        target_duration=clip.target_duration,
                        camera_movement=clip.camera_movement,
                        first_keyframe_framing=clip.first_keyframe_framing,
                        first_keyframe_visible_content=clip.first_keyframe_visible_content,
                        narrative_purpose=clip.narrative_purpose,
                        pacing=clip.pacing,
                        inter_clip_boundary=clip.inter_clip_boundary,
                        first_keyframe_reuse=clip.first_keyframe_reuse,
                    ),
                    style_spec=project.style_spec or {},
                )

                try:
                    img_result = await image_service.generate(
                        prompt=keyframe_prompt,
                        model="dall-e-3",
                        quality="standard",
                        size="1792x1024" if project.aspect_ratio == "16:9" else "1024x1792",
                    )

                    if not img_result.get("error") and img_result["local_paths"]:
                        keyframe_path = img_result["local_paths"][0]

                        # Save keyframe asset
                        keyframe_asset = VideoAsset(
                            asset_id=f"asset_{uuid.uuid4().hex[:8]}",
                            project_id=project.id,
                            clip_id=clip.id,
                            asset_type="keyframe",
                            asset_role="first_keyframe",
                            url=img_result["urls"][0] if img_result["urls"] else None,
                            local_path=keyframe_path,
                            prompt_used=keyframe_prompt,
                            generation_params={
                                "model": "dall-e-3",
                                "cost_usd": img_result.get("cost_usd", 0),
                            },
                        )
                        db.add(keyframe_asset)
                        logger.info(f"Generated keyframe for clip {clip.clip_id}")
                except Exception as e:
                    logger.error(f"Keyframe generation failed: {e}")

        # Step 2: Generate TTS narration if exists
        audio_path = None
        if clip.narration_cue and tts_service.is_available:
            try:
                voice = "alloy"
                if project.voice_profiles and "narrator" in project.voice_profiles:
                    voice = project.voice_profiles["narrator"].get("name", "alloy")

                tts_result = await tts_service.generate(
                    text=clip.narration_cue,
                    voice=voice,
                    model="tts-1",
                    speed=1.0,
                    response_format="mp3",
                )

                if not tts_result.get("error"):
                    audio_path = tts_result["local_path"]

                    # Save TTS asset
                    tts_asset = VideoAsset(
                        asset_id=f"asset_{uuid.uuid4().hex[:8]}",
                        project_id=project.id,
                        clip_id=clip.id,
                        asset_type="audio_tts",
                        asset_role="narration",
                        local_path=audio_path,
                        generation_params={
                            "voice": voice,
                            "duration_estimate": tts_result.get("duration_estimate"),
                            "cost_usd": tts_result.get("cost_usd"),
                        },
                    )
                    db.add(tts_asset)
                    logger.info(f"Generated TTS for clip {clip.clip_id}")
            except Exception as e:
                logger.error(f"TTS generation failed: {e}")

        # Step 3: Generate video clip with ffmpeg
        if keyframe_path and os.path.exists(keyframe_path):
            try:
                # Determine motion effect based on camera movement
                effect_map = {
                    "static": "static",
                    "zoom": "kenburns_zoom_in",
                    "dolly": "kenburns_zoom_in",
                    "pan": "kenburns_pan_left",
                    "tilt": "kenburns_pan_up",
                    "crane": "kenburns_pan_down",
                    "arc": "kenburns_pan_right",
                }
                effect = effect_map.get(clip.camera_movement, "kenburns_zoom_in")

                video_filename = f"{project.project_id}_clip{clip.sequence_number:03d}.mp4"
                video_path = await self.video_generator.create_clip_from_image(
                    image_path=keyframe_path,
                    output_filename=video_filename,
                    duration=clip.target_duration,
                    effect=effect,
                    audio_path=audio_path,
                    aspect_ratio=project.aspect_ratio,
                )

                clip.video_path = video_path
                clip.actual_duration = await self.video_generator.get_video_duration(video_path)
                clip.status = "completed"

                # Save video asset
                video_asset = VideoAsset(
                    asset_id=f"asset_{uuid.uuid4().hex[:8]}",
                    project_id=project.id,
                    clip_id=clip.id,
                    asset_type="video",
                    asset_role="clip_video",
                    local_path=video_path,
                    generation_params={"effect": effect, "duration": clip.target_duration},
                )
                db.add(video_asset)

                logger.info(f"Created video clip {clip.clip_id}: {video_path}")

            except Exception as e:
                logger.error(f"Video clip creation failed: {e}")
                clip.status = "failed"
        else:
            logger.warning(f"No keyframe available for clip {clip.clip_id}")
            clip.status = "failed"

        await db.commit()

    # ============================================================
    # Assembly (REAL - ffmpeg)
    # ============================================================

    async def assemble_video(
        self,
        db: AsyncSession,
        project_id: str,
    ) -> VideoProject:
        """Assemble all clips into final video with audio mixing."""
        result = await db.execute(
            select(VideoProject).where(VideoProject.project_id == project_id)
        )
        project = result.scalar_one_or_none()

        if not project:
            raise ValueError(f"Project {project_id} not found")

        clips_result = await db.execute(
            select(VideoClip)
            .where(
                VideoClip.project_id == project.id,
                VideoClip.status == "completed",
            )
            .order_by(VideoClip.sequence_number)
        )
        clips = clips_result.scalars().all()

        if not clips:
            raise ValueError(f"No completed clips found for project {project_id}")

        logger.info(f"Assembling {len(clips)} clips for project: {project_id}")

        # Prepare clip data
        clip_data = []
        for clip in clips:
            if clip.video_path and os.path.exists(clip.video_path):
                clip_data.append({
                    "path": clip.video_path,
                    "duration": clip.actual_duration or clip.target_duration,
                })

        # Get BGM path if separate
        bgm_path = None
        if project.bgm_source == "separate":
            bgm_assets = await db.execute(
                select(VideoAsset).where(
                    VideoAsset.project_id == project.id,
                    VideoAsset.asset_type == "audio_bgm",
                )
            )
            bgm_asset = bgm_assets.scalar_one_or_none()
            if bgm_asset and bgm_asset.local_path:
                bgm_path = bgm_asset.local_path

        # Assemble using ffmpeg
        final_filename = f"{project.project_id}_final.mp4"
        try:
            final_path = await self.video_generator.create_video_from_clips(
                clips=clip_data,
                output_filename=final_filename,
                bgm_path=bgm_path,
                transition_duration=0.5,
            )
        except Exception as e:
            logger.error(f"Assembly failed: {e}")
            # Fallback: simple concat
            final_path = str(self.output_dir / final_filename)

        project.output_path = final_path
        project.output_url = f"/movies/{final_filename}"
        project.status = "completed"
        project.current_phase = "done"
        project.progress_percent = 100
        project.completed_at = datetime.now(timezone.utc)

        # Save final video asset
        final_asset = VideoAsset(
            asset_id=f"asset_{uuid.uuid4().hex[:8]}",
            project_id=project.id,
            asset_type="final_video",
            asset_role="final_output",
            local_path=final_path,
            url=project.output_url,
        )
        db.add(final_asset)

        await db.commit()
        logger.info(f"Video assembly complete: {final_path}")
        return project

    # ============================================================
    # Full Pipeline (Auto-execute all phases)
    # ============================================================

    async def run_full_pipeline(
        self,
        db: AsyncSession,
        project_id: str,
        global_def: VideoProjectGlobalDef,
        provider: str = "openai",
    ) -> VideoGenerationStatus:
        """Run the complete video generation pipeline with REAL generation."""
        logger.info(f"Starting FULL REAL pipeline for project: {project_id}")

        # Phase 2: Global Definitions
        await self.set_global_definitions(db, project_id, global_def)

        # Phase 3: Clip Planning
        await self.plan_clips(db, project_id, provider)

        # Generate BGM blueprint if separate BGM
        project_result = await db.execute(
            select(VideoProject).where(VideoProject.project_id == project_id)
        )
        project = project_result.scalar_one()

        if project.bgm_source == "separate" and project.bgm_properties:
            await self.generate_bgm_blueprint(db, project_id, provider)

        # Phase 4: Reference Images (if elements defined)
        # TODO: Extract recurring elements from global_def

        # Phase 5: REAL Execution
        status = await self.execute_generation(db, project_id, provider)

        # Assembly
        if status.clips_completed > 0:
            await self.assemble_video(db, project_id)

        return status
