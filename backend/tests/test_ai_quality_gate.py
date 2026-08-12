from dataclasses import dataclass


@dataclass
class QualityResult:
    passed: bool
    failed_checks: list[str]


def evaluate_quality_gate(*, script: bool, dialogue: bool, character: bool, storyboard: bool, images: bool, continuity: bool) -> QualityResult:
    checks = {
        "script": script,
        "dialogue": dialogue,
        "character": character,
        "storyboard": storyboard,
        "images": images,
        "continuity": continuity,
    }
    failed = [name for name, passed in checks.items() if not passed]
    return QualityResult(passed=not failed, failed_checks=failed)


def test_quality_gate_passes_complete_output():
    result = evaluate_quality_gate(
        script=True,
        dialogue=True,
        character=True,
        storyboard=True,
        images=True,
        continuity=True,
    )
    assert result.passed is True
    assert result.failed_checks == []


def test_quality_gate_rejects_incomplete_output():
    result = evaluate_quality_gate(
        script=True,
        dialogue=True,
        character=True,
        storyboard=False,
        images=True,
        continuity=True,
    )
    assert result.passed is False
    assert result.failed_checks == ["storyboard"]
