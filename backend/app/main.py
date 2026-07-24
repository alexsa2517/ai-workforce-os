"""
AI Workforce OS — Backend API Server

Endpoints:
  GET  /                          — ระบบ status
  GET  /health                    — Health check
  POST /chat                      — Chat with AI
  POST /api/v1/character/video    — สร้างวิดีโอตัวละครพูดได้ (จากข้อความ)
  POST /api/v1/scene/video        — สร้างวิดีโอ 1 ฉาก (จาก DirectorAI)
  POST /api/v1/episode/video      — สร้างหนังเต็มตอน
  POST /api/v1/lipsync            — Lip-Sync ตรง (ภาพ + เสียง → วิดีโอ)
  GET  /api/v1/jobs/{job_id}      — ดูสถานะงาน
  GET  /api/v1/movies             — ดูรายการหนังที่สร้างแล้ว
  GET  /api/v1/movies/{episode}   — ดูวิดีโอใน episode
"""

import os
import json
import logging
import asyncio
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

# ── Logging ─────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("AIWorkforceOS")

# ── App ─────────────────────────────────────────────────────────
app = FastAPI(
    title="AI Workforce OS",
    description="ระบบสร้างหนัง AI อัตโนมัติ — DirectorAI + TTS + Lip-Sync + Video Assembly",
    version="0.2.0",
)

# ── Import Services ─────────────────────────────────────────────
from app.services.llm.factory import LLMFactory

# ── Base Models ─────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    provider: Optional[str] = "openai"


class CharacterVideoRequest(BaseModel):
    """สร้างวิดีโอตัวละครพูดข้อความ"""
    character: str = "linhfeng"
    text: str
    lip_sync_provider: Optional[str] = "simulated"
    image_provider: Optional[str] = "openai"
    run_id: Optional[str] = None


class SceneVideoRequest(BaseModel):
    """สร้างวิดีโอ 1 ฉาก"""
    character: str = "linhfeng"
    episode: str = "ep001"
    scene_index: int = 0
    lip_sync_provider: Optional[str] = "simulated"
    image_provider: Optional[str] = "openai"


class EpisodeVideoRequest(BaseModel):
    """สร้างหนังเต็มตอน"""
    character: str = "linhfeng"
    episode: str = "ep001"
    lip_sync_provider: Optional[str] = "simulated"
    image_provider: Optional[str] = "openai"
    max_scenes: int = 10


class LipSyncRequest(BaseModel):
    """Lip-Sync ตรง (ใช้ภาพ + เสียงที่มีอยู่แล้ว)"""
    image_path: str
    audio_path: str
    provider: Optional[str] = "simulated"
    duration_hint: Optional[int] = None


# ── In-memory job store ────────────────────────────────────────
_jobs: dict = {}
MOVIES_DIR = Path("./movies")
MOVIES_DIR.mkdir(exist_ok=True)

# ── Mount static files ─────────────────────────────────────────
app.mount("/movies", StaticFiles(directory=str(MOVIES_DIR), check_dir=False), name="movies")


# ═══════════════════════════════════════════════════════════════════
# Basic Endpoints
# ═══════════════════════════════════════════════════════════════════

@app.get("/")
def root():
    return {
        "message": "AI Workforce OS is running",
        "version": "0.2.0",
        "features": [
            "DirectorAI Agent",
            "Text-to-Speech (TTS)",
            "Image Generation",
            "Lip-Sync Video (ตัวละครพูดได้)",
            "Movie Pipeline (End-to-End)",
            "Video Assembly (รวมฉากเป็นหนัง)",
        ],
        "api_docs": "/docs",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "services": {
            "llm": "ready",
            "tts": "ready",
            "image_gen": "ready",
            "lip_sync": "ready",
            "pipeline": "ready",
        },
    }


@app.post("/chat")
def chat(request: ChatRequest):
    try:
        llm = LLMFactory.get(request.provider)
        response = llm.generate(request.message)
        return {
            "provider": request.provider,
            "response": response,
        }
    except Exception as e:
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════
# Video Generation Endpoints
# ═══════════════════════════════════════════════════════════════════

@app.post("/api/v1/character/video")
async def create_character_video(request: CharacterVideoRequest, bg: BackgroundTasks):
    """
    สร้างวิดีโอตัวละครพูดได้ — ป้อนข้อความ → ได้วิดีโอปากขยับ

    Flow: Image → TTS → Lip-Sync → MP4

    Returns immediately with job_id. Check status with /api/v1/jobs/{job_id}
    """
    job_id = f"char_video_{len(_jobs) + 1}"
    _jobs[job_id] = {"status": "queued", "job_id": job_id}

    bg.add_task(_run_character_video_job, job_id, request)

    return {
        "status": "accepted",
        "job_id": job_id,
        "message": "Video generation started. Check status with /api/v1/jobs/{job_id}",
    }


@app.post("/api/v1/scene/video")
async def create_scene_video(request: SceneVideoRequest, bg: BackgroundTasks):
    """
    สร้างวิดีโอ 1 ฉาก — DirectorAI → Image → TTS → Lip-Sync → MP4

    Returns immediately with job_id.
    """
    job_id = f"scene_video_{len(_jobs) + 1}"
    _jobs[job_id] = {"status": "queued", "job_id": job_id}

    bg.add_task(_run_scene_video_job, job_id, request)

    return {
        "status": "accepted",
        "job_id": job_id,
        "message": "Scene video generation started. Check status with /api/v1/jobs/{job_id}",
    }


@app.post("/api/v1/episode/video")
async def create_episode_video(request: EpisodeVideoRequest, bg: BackgroundTasks):
    """
    สร้างหนังเต็มตอน — DirectorAI → ทุกฉาก → Lip-Sync → รวมคลิป → MP4

    Returns immediately with job_id. This may take several minutes.
    """
    job_id = f"episode_video_{len(_jobs) + 1}"
    _jobs[job_id] = {"status": "queued", "job_id": job_id}

    bg.add_task(_run_episode_video_job, job_id, request)

    return {
        "status": "accepted",
        "job_id": job_id,
        "message": "Episode video generation started. This may take several minutes.",
    }


@app.post("/api/v1/lipsync")
async def create_lipsync(request: LipSyncRequest, bg: BackgroundTasks):
    """
    Lip-Sync ตรง — ใช้ภาพ + เสียงที่มีอยู่แล้ว สร้างวิดีโอปากขยับ

    Returns immediately with job_id.
    """
    job_id = f"lipsync_{len(_jobs) + 1}"
    _jobs[job_id] = {"status": "queued", "job_id": job_id}

    bg.add_task(_run_lipsync_job, job_id, request)

    return {
        "status": "accepted",
        "job_id": job_id,
        "message": "Lip-sync generation started.",
    }


# ═══════════════════════════════════════════════════════════════════
# Job Status & Movie Listing
# ═══════════════════════════════════════════════════════════════════

@app.get("/api/v1/jobs/{job_id}")
def get_job_status(job_id: str):
    """ดูสถานะงานสร้างวิดีโอ"""
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return _jobs[job_id]


@app.get("/api/v1/movies")
def list_movies():
    """ดูรายการหนัง/วิดีโอที่สร้างแล้ว"""
    movies = []
    if MOVIES_DIR.exists():
        for item in sorted(MOVIES_DIR.iterdir()):
            if item.is_dir():
                video_files = list(item.rglob("*.mp4"))
                for vf in video_files:
                    movies.append({
                        "name": vf.name,
                        "path": f"/movies/{vf.relative_to(MOVIES_DIR)}",
                        "size_mb": round(vf.stat().st_size / (1024 * 1024), 2),
                        "full_path": str(vf),
                    })
    return {"movies": movies, "total": len(movies)}


@app.get("/api/v1/movies/{episode}")
def get_episode_movies(episode: str):
    """ดูรายการวิดีโอใน episode"""
    ep_dir = MOVIES_DIR / episode
    if not ep_dir.exists():
        return {"episode": episode, "videos": [], "total": 0}

    videos = []
    for vf in sorted(ep_dir.rglob("*.mp4")):
        videos.append({
            "name": vf.name,
            "path": f"/movies/{vf.relative_to(MOVIES_DIR)}",
            "size_mb": round(vf.stat().st_size / (1024 * 1024), 2),
        })

    return {"episode": episode, "videos": videos, "total": len(videos)}


# ═══════════════════════════════════════════════════════════════════
# Background Job Runners
# ═══════════════════════════════════════════════════════════════════

def _run_character_video_job(job_id: str, request: CharacterVideoRequest):
    """Background task: สร้างวิดีโอตัวละครพูดได้"""
    try:
        from app.services.pipeline.movie_pipeline import MoviePipeline
        pipeline = MoviePipeline(
            lip_sync_provider=request.lip_sync_provider,
            image_provider=request.image_provider,
        )
        result = pipeline.generate_character_video(
            character=request.character,
            text=request.text,
            run_id=job_id,
        )
        _jobs[job_id] = {
            "status": "completed",
            "job_id": job_id,
            "result": result,
        }
        logger.info(f"Job {job_id} completed: {result.get('video_path')}")
    except Exception as e:
        _jobs[job_id] = {
            "status": "failed",
            "job_id": job_id,
            "error": str(e),
        }
        logger.error(f"Job {job_id} failed: {e}")


def _run_scene_video_job(job_id: str, request: SceneVideoRequest):
    """Background task: สร้างวิดีโอ 1 ฉาก"""
    try:
        from app.services.pipeline.movie_pipeline import MoviePipeline
        pipeline = MoviePipeline(
            lip_sync_provider=request.lip_sync_provider,
            image_provider=request.image_provider,
        )
        result = pipeline.generate_scene(
            character=request.character,
            episode=request.episode,
            scene_index=request.scene_index,
        )
        _jobs[job_id] = {
            "status": "completed",
            "job_id": job_id,
            "result": result,
        }
        logger.info(f"Job {job_id} completed: {result.get('video_path')}")
    except Exception as e:
        _jobs[job_id] = {
            "status": "failed",
            "job_id": job_id,
            "error": str(e),
        }
        logger.error(f"Job {job_id} failed: {e}")


def _run_episode_video_job(job_id: str, request: EpisodeVideoRequest):
    """Background task: สร้างหนังเต็มตอน"""
    try:
        from app.services.pipeline.movie_pipeline import MoviePipeline
        pipeline = MoviePipeline(
            lip_sync_provider=request.lip_sync_provider,
            image_provider=request.image_provider,
        )
        result = pipeline.generate_episode(
            character=request.character,
            episode=request.episode,
            max_scenes=request.max_scenes,
        )
        _jobs[job_id] = {
            "status": "completed",
            "job_id": job_id,
            "result": {
                "episode": result.get("episode"),
                "total_scenes": result.get("total_scenes"),
                "successful_scenes": result.get("successful_scenes"),
                "final_video": result.get("final_video"),
                "scenes_count": len(result.get("scenes", [])),
            },
        }
        logger.info(f"Job {job_id} episode completed: {result.get('final_video')}")
    except Exception as e:
        _jobs[job_id] = {
            "status": "failed",
            "job_id": job_id,
            "error": str(e),
        }
        logger.error(f"Job {job_id} episode failed: {e}")


def _run_lipsync_job(job_id: str, request: LipSyncRequest):
    """Background task: Lip-Sync ตรง"""
    try:
        from app.services.lip_sync.lip_sync_service import LipSyncService
        service = LipSyncService(provider=request.provider)
        output_path = str(MOVIES_DIR / f"lipsync_{job_id}.mp4")
        result = service.generate_lip_sync(
            image_path=request.image_path,
            audio_path=request.audio_path,
            output_path=output_path,
            duration_hint=request.duration_hint,
        )
        _jobs[job_id] = {
            "status": "completed",
            "job_id": job_id,
            "result": result,
        }
        logger.info(f"Job {job_id} lipsync completed: {result.get('output_path')}")
    except Exception as e:
        _jobs[job_id] = {
            "status": "failed",
            "job_id": job_id,
            "error": str(e),
        }
        logger.error(f"Job {job_id} lipsync failed: {e}")
