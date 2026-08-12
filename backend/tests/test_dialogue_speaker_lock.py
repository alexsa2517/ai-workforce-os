import pytest

from app.services.production.character_bible import LIN_FENG, MYSTERIOUS_WOMAN
from app.services.production.dialogue import DialogueLine, validate_dialogue_line, validate_scene_01_dialogue


def test_scene_01_speaker_lock_is_valid():
    validate_scene_01_dialogue()


def test_lin_feng_is_male_and_has_male_voice():
    assert LIN_FENG.gender == "MALE"
    assert LIN_FENG.voice_id.startswith("MALE_THAI_")


def test_mysterious_woman_is_female_and_has_female_voice():
    assert MYSTERIOUS_WOMAN.gender == "FEMALE"
    assert MYSTERIOUS_WOMAN.voice_id.startswith("FEMALE_THAI_")


def test_wrong_voice_for_lin_feng_is_rejected():
    line = DialogueLine(
        speaker_id=LIN_FENG.character_id,
        voice_id=MYSTERIOUS_WOMAN.voice_id,
        text="เจ้าเป็นใคร?",
    )
    with pytest.raises(ValueError, match="Voice mismatch"):
        validate_dialogue_line(
            line,
            {
                LIN_FENG.character_id: LIN_FENG,
                MYSTERIOUS_WOMAN.character_id: MYSTERIOUS_WOMAN,
            },
        )
