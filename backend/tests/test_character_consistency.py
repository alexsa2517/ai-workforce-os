from dataclasses import dataclass


@dataclass(frozen=True)
class Character:
    name: str
    age: int
    hair: str
    outfit: str


def character_is_consistent(reference: Character, candidate: Character) -> bool:
    return reference == candidate


def test_character_consistency_accepts_same_character():
    reference = Character("หลินเฟิง", 25, "ผมดำยาว", "ชุดจีนโบราณสีดำ")
    candidate = Character("หลินเฟิง", 25, "ผมดำยาว", "ชุดจีนโบราณสีดำ")
    assert character_is_consistent(reference, candidate)


def test_character_consistency_rejects_changed_attributes():
    reference = Character("หลินเฟิง", 25, "ผมดำยาว", "ชุดจีนโบราณสีดำ")
    candidate = Character("หลินเฟิง", 30, "ผมดำยาว", "ชุดจีนโบราณสีดำ")
    assert not character_is_consistent(reference, candidate)
