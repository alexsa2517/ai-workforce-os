from dataclasses import dataclass


@dataclass(frozen=True)
class CharacterBible:
    character_id: str
    name: str
    gender: str
    age: int
    appearance: str
    outfit: str
    voice_id: str


LIN_FENG = CharacterBible(
    character_id="LIN_FENG",
    name="หลินเฟิง",
    gender="MALE",
    age=25,
    appearance="ชายจีนโบราณ ใบหน้าชายชัดเจน ผมดำยาว ดวงตาคม",
    outfit="ชุดจีนโบราณสีดำ",
    voice_id="MALE_THAI_LIN_FENG",
)

MYSTERIOUS_WOMAN = CharacterBible(
    character_id="MYSTERIOUS_WOMAN",
    name="หญิงปริศนา",
    gender="FEMALE",
    age=25,
    appearance="หญิงจีนโบราณ ใบหน้าหญิงชัดเจน ผมดำยาว",
    outfit="ชุดจีนโบราณสีขาว",
    voice_id="FEMALE_THAI_MYSTERIOUS_WOMAN",
)
