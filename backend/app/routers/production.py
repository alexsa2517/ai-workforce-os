from pathlib import Path

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.config import settings
from app.services.production.deepseek_director import DeepSeekDirector
from app.services.production.google_media import GoogleMediaProvider
from app.services.production.schemas import ProductionPlan, QualityGateResult, evaluate_quality_gate

router = APIRouter(prefix="/api/v1/production", tags=["Production"])


class IdeaRequest(BaseModel):
    idea: str


class VideoRequest(BaseModel):
    plan: ProductionPlan
    approved: bool = False


@router.post("/plan", response_model=ProductionPlan)
async def create_production_plan(request: IdeaRequest):
    """Turn a natural-language idea into a structured Thai production plan."""
    if not request.idea.strip():
        raise HTTPException(status_code=400, detail="idea is required")
    try:
        return DeepSeekDirector().create_plan(request.idea)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Director failed: {exc}") from exc


@router.post("/quality-gate", response_model=QualityGateResult)
async def quality_gate(plan: ProductionPlan, approved: bool = False):
    """Validate the plan before any real media API can be called."""
    return evaluate_quality_gate(plan, approved=approved)


@router.post("/video")
async def generate_video(request: VideoRequest):
    """Generate a real Veo clip only after every quality gate passes and user approval is explicit."""
    if not settings.REAL_MEDIA_ENABLED:
        raise HTTPException(status_code=409, detail="Real media generation is disabled")

    gate = evaluate_quality_gate(request.plan, approved=request.approved)
    if not gate.approved_for_video:
        raise HTTPException(status_code=422, detail=gate.model_dump())

    if len(request.plan.scenes) != 1 or len(request.plan.scenes[0].shots) != 1:
        raise HTTPException(
            status_code=422,
            detail="MVP video endpoint accepts exactly one scene with one shot; compose multi-shot episodes later.",
        )

    shot = request.plan.scenes[0].shots[0]
    dialogue = " ".join(shot.dialogue)
    prompt = (
        f"Cinematic Thai-language dialogue scene. {shot.description}. "
        f"Camera: {shot.camera}. Natural facial expressions, subtle blinking and eye saccades, "
        f"physically correct eye and object reflections, realistic body language and timing. "
        f"Keep character appearance identical to the supplied character bible. "
        f"Thai dialogue with clear pronunciation and accurate lip synchronization: {dialogue}. "
        f"Lighting: {shot.lighting}. {shot.reflections}. Vertical 9:16."
    )
    output = Path(settings.MOVIES_DIR) / f"{request.plan.title.replace(' ', '_')}_shot.mp4"
    try:
        path = GoogleMediaProvider().generate_video(prompt, str(output), request.plan.aspect_ratio)
        return {"status": "completed", "path": path, "quality_gate": gate.model_dump()}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Google video generation failed: {exc}") from exc
