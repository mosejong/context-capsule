from pathlib import Path

from app.generators.capsule_generator import generate_capsule
from app.generators.execution_packet_generator import build_execution_packet
from app.schemas.capsule_schema import CapsuleInput, FileKind, RepoFile, RiskLevel


def test_execution_packet_blocks_high_risk_auto_start():
    files = [
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Demo\nA test project.", size=22),
        RepoFile(path="app/auth.py", kind=FileKind.CODE, content="jwt login password token", size=24),
    ]
    capsule = generate_capsule(
        CapsuleInput(
            repo_path=Path("."),
            task_request="로그인 jwt token 로직을 수정하는 작업 브리프를 만들어줘",
        ),
        files,
    )

    packet = build_execution_packet(capsule)

    assert packet.auto_start_allowed is False
    assert packet.block_reason
    assert "Auto Start Gate" in packet.issue_body
    assert "Acceptance Criteria" in packet.issue_body
    assert "Verification status: Estimated only" in packet.issue_body
    assert "RiskLevel." not in packet.issue_body
    assert "RiskLevel." not in packet.block_reason
    assert "GitHub" not in packet.recommended_branch
    assert packet.risk_level in {RiskLevel.HIGH, RiskLevel.BLOCKED}
    assert "context-capsule" in packet.labels
    assert "auto-start:blocked" in packet.labels
    assert "needs-human-approval" in packet.labels
    assert packet.acceptance_criteria
    assert "Issue Metadata" in packet.issue_body
    assert "Recommended branch" in packet.issue_body


def test_execution_packet_allows_low_risk_doc_task():
    files = [
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Demo\nA test project.", size=22),
    ]
    capsule = generate_capsule(
        CapsuleInput(
            repo_path=Path("."),
            task_request="README 문서 정리 작업 브리프를 만들어줘",
        ),
        files,
    )

    packet = build_execution_packet(capsule)

    assert packet.auto_start_allowed is True
    assert packet.block_reason is None
    assert "Decision Record" in packet.decision_record
    assert packet.recommended_branch.startswith("task/")
    assert packet.risk_level == RiskLevel.LOW
    assert "auto-start:allowed" in packet.labels
    assert "ready-for-brief" in packet.labels
