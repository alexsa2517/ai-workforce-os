from pydantic import BaseModel, Field


class CharacterBible(BaseModel):
    name: str
    age: int | None = None
    appearance: str
    outfit: str
    personality: str
    voice: str = "เสียงภาษาไทยชัดเจน เป็นธรรมชาติ"


class Shot(BaseModel):
    shot_id: str
    description: str
    camera: str
    duration_seconds: int = Field(gt=0)
    characters: list[str] = []
    dialogue: list[str] = []
    performance: str = "เป็นธรรมชาติ กระพริบตาและกรอกตาตามบริบท"
    lighting: str = "cinematic natural lighting"
    reflections: str = "วัตถุและดวงตาสะท้อนแสงและสภาพแวดล้อมตามจริง"


class Scene(BaseModel):
    scene_id: str
    location: str
    time: str
    mood: str
    shots: list[Shot]


class ProductionPlan(BaseModel):
    title: str
    language: str = "th-TH"
    aspect_ratio: str = "9:16"
    characters: list[CharacterBible]
    scenes: list[Scene]


class QualityGateResult(BaseModel):
    passed: bool
    failed_checks: list[str]
    approved_for_video: bool = False


def evaluate_quality_gate(plan: ProductionPlan, approved: bool = False) -> QualityGateResult:
    failures: list[str] = []
    if not plan.title.strip():
        failures.append("title")
    if not plan.characters:
        failures.append("characters")
    if not plan.scenes:
        failures.append("scenes")

    known = {c.name for c in plan.characters}
    for scene in plan.scenes:
        if not scene.shots:
            failures.append(f"{scene.scene_id}:shots")
        for shot in scene.shots:
            if not shot.description.strip():
                failures.append(f"{shot.shot_id}:description")
            if not shot.camera.strip():
                failures.append(f"{shot.shot_id}:camera")
            if shot.duration_seconds <= 0:
                failures.append(f"{shot.shot_id}:duration")
            if any(name not in known for name in shot.characters):
                failures.append(f"{shot.shot_id}:character_reference")

    return QualityGateResult(
        passed=not failures,
        failed_checks=failures,
        approved_for_video=(not failures and approved),
    )
