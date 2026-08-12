from dataclasses import dataclass


@dataclass
class Shot:
    description: str
    dialogue: str
    duration_seconds: int
    character: str
    camera: str


def validate_shot(shot: Shot) -> list[str]:
    missing = []
    if not shot.description.strip():
        missing.append("description")
    if not shot.dialogue.strip():
        missing.append("dialogue")
    if shot.duration_seconds <= 0:
        missing.append("duration")
    if not shot.character.strip():
        missing.append("character")
    if not shot.camera.strip():
        missing.append("camera")
    return missing


def test_storyboard_shot_contract():
    shot = Shot("ป่าโบราณในหมอก", "เจ้าเป็นใคร?", 5, "หลินเฟิง", "close-up")
    assert validate_shot(shot) == []


def test_storyboard_rejects_incomplete_shot():
    shot = Shot("", "", 0, "", "")
    assert set(validate_shot(shot)) == {"description", "dialogue", "duration", "character", "camera"}
