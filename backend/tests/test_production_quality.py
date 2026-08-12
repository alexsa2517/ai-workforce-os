from app.services.production.schemas import (
    CharacterBible,
    ProductionPlan,
    Scene,
    Shot,
    evaluate_quality_gate,
)


def sample_plan() -> ProductionPlan:
    return ProductionPlan(
        title="หลินเฟิง คนตาย 1000 ปี",
        characters=[
            CharacterBible(
                name="หลินเฟิง",
                age=25,
                appearance="ชายจีนโบราณ ใบหน้าสงบ ผมดำยาว",
                outfit="ชุดจีนโบราณสีดำ",
                personality="สุขุม ลึกลับ",
            ),
            CharacterBible(
                name="หญิงปริศนา",
                age=24,
                appearance="หญิงสาวผมดำ ดวงตาเศร้า",
                outfit="ชุดจีนโบราณสีขาว",
                personality="ลึกลับ อ่อนโยน",
            ),
        ],
        scenes=[
            Scene(
                scene_id="S01",
                location="ป่าโบราณในหมอก",
                time="กลางคืน",
                mood="ลึกลับ",
                shots=[
                    Shot(
                        shot_id="S01_SH01",
                        description="ตัวละครสองคนเผชิญหน้ากันในป่าหมอก",
                        camera="medium close-up",
                        duration_seconds=8,
                        characters=["หลินเฟิง", "หญิงปริศนา"],
                        dialogue=["หลินเฟิง: เจ้าเป็นใคร?", "หญิงปริศนา: เจ้าจำข้าไม่ได้จริงหรือ... หลินเฟิง?"],
                    )
                ],
            )
        ],
    )


def test_complete_plan_passes_without_approval_for_generation():
    result = evaluate_quality_gate(sample_plan(), approved=False)
    assert result.passed is True
    assert result.approved_for_video is False


def test_complete_plan_requires_explicit_user_approval():
    result = evaluate_quality_gate(sample_plan(), approved=True)
    assert result.passed is True
    assert result.approved_for_video is True


def test_unknown_character_reference_fails():
    plan = sample_plan()
    plan.scenes[0].shots[0].characters.append("ตัวละครที่ไม่มีใน Bible")
    result = evaluate_quality_gate(plan, approved=True)
    assert result.passed is False
    assert "S01_SH01:character_reference" in result.failed_checks
