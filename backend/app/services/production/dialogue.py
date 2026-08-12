from dataclasses import dataclass

from app.services.production.character_bible import CharacterBible, LIN_FENG, MYSTERIOUS_WOMAN


@dataclass(frozen=True)
class DialogueLine:
    speaker_id: str
    voice_id: str
    text: str


def validate_dialogue_line(line: DialogueLine, characters: dict[str, CharacterBible]) -> None:
    character = characters.get(line.speaker_id)
    if character is None:
        raise ValueError(f"Unknown speaker_id: {line.speaker_id}")
    if line.voice_id != character.voice_id:
        raise ValueError(
            f"Voice mismatch for {line.speaker_id}: expected {character.voice_id}, got {line.voice_id}"
        )


SCENE_01_DIALOGUE = [
    DialogueLine(LIN_FENG.character_id, LIN_FENG.voice_id, "เจ้าเป็นใคร?"),
    DialogueLine(
        MYSTERIOUS_WOMAN.character_id,
        MYSTERIOUS_WOMAN.voice_id,
        "เจ้าจำข้าไม่ได้จริงหรือ... หลินเฟิง?",
    ),
]


def validate_scene_01_dialogue() -> None:
    characters = {
        LIN_FENG.character_id: LIN_FENG,
        MYSTERIOUS_WOMAN.character_id: MYSTERIOUS_WOMAN,
    }
    for line in SCENE_01_DIALOGUE:
        validate_dialogue_line(line, characters)
