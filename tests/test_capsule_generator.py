from pathlib import Path

from app.generators.capsule_generator import generate_capsule
from app.schemas.capsule_schema import CapsuleInput, FileKind, HandoffTarget, RepoFile


def sample_files():
    return [
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Demo\nA test project.", size=22),
        RepoFile(
            path="app/missions.py",
            kind=FileKind.CODE,
            content="mission complete api response status_code",
            size=41,
        ),
    ]


def test_generates_teammate_brief():
    output = generate_capsule(
        CapsuleInput(
            repo_path=Path("."),
            task_request="미션 완료 기능을 팀원에게 넘길 작업으로 정리해줘",
            handoff_target=HandoffTarget.TEAMMATE,
        ),
        sample_files(),
    )

    assert output.handoff_target == HandoffTarget.TEAMMATE
    assert output.sections.teammate_brief
    assert output.sections.future_me_letter
    assert output.sections.junior_guide
    assert output.sections.ai_handoff_prompt
    assert output.sections.risk_checklist
    assert output.token_budget.raw_context_tokens > 0
    assert output.token_budget.handoff_prompt_tokens > 0
    assert output.token_budget.verification_status == "Estimated only"
    assert output.token_budget.actual_provider_usage == "Not measured yet"
    assert "오늘 할 일" in output.handoff_prompt
    assert "질문해야 할 것" in output.handoff_prompt
    assert "Token Budget" in output.markdown
    assert "Verification status: Estimated only" in output.markdown
    assert "Teammate Brief" in output.markdown
    assert "RiskLevel." not in output.markdown


def test_generates_self_handoff():
    output = generate_capsule(
        CapsuleInput(
            repo_path=Path("."),
            task_request="내일 이어서 작업할 수 있게 현재 상태를 정리해줘",
            handoff_target=HandoffTarget.FUTURE_ME,
        ),
        sample_files(),
    )

    assert output.handoff_target == HandoffTarget.FUTURE_ME
    assert "내일 이어서 작업" in output.handoff_prompt
    assert "Self Handoff" in output.markdown
    assert "RiskLevel." not in output.markdown


def test_junior_guide_uses_user_facing_task_text():
    output = generate_capsule(
        CapsuleInput(
            repo_path=Path("."),
            task_request="리드미 포폴용으로 손보자",
            handoff_target=HandoffTarget.JUNIOR_DEVELOPER,
        ),
        sample_files(),
    )

    assert "리드미 포폴용으로 손보자" in output.sections.junior_guide
    assert "Intent:" not in output.sections.junior_guide
    assert "Normalized terms:" not in output.sections.junior_guide
    assert "Target hints:" not in output.sections.junior_guide
    assert "이유:" in output.sections.junior_guide
