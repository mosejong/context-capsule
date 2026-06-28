from datetime import datetime
from pathlib import Path

import json

from app.generators.capsule_generator import generate_capsule
from app.generators.execution_packet_generator import build_execution_packet
from app.generators.output_writer import save_output_packet
from app.schemas.capsule_schema import CapsuleInput, FileKind, HandoffTarget, RepoFile


def build_sample_capsule():
    files = [
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Demo\nA test project.", size=22),
        RepoFile(path="app/tasks.py", kind=FileKind.CODE, content="task handoff issue metadata", size=27),
    ]
    return generate_capsule(
        CapsuleInput(
            repo_path=Path("."),
            task_request="Create a teammate brief for issue packet saving",
            handoff_target=HandoffTarget.TEAMMATE,
        ),
        files,
    )


def test_save_output_packet_writes_expected_files(tmp_path):
    capsule = build_sample_capsule()
    execution_packet = build_execution_packet(capsule)

    saved = save_output_packet(
        capsule,
        execution_packet,
        output_root=tmp_path,
        generated_at=datetime(2026, 6, 23, 10, 30, 0),
    )

    expected_files = {
        "OVERVIEW.md",
        "AI_HANDOFF_PROMPT.md",
        "TEAMMATE_BRIEF.md",
        "JUNIOR_GUIDE.md",
        "SELF_HANDOFF.md",
        "RISK_CHECKLIST.md",
        "GITHUB_ISSUE.md",
        "DECISION_RECORD.md",
        "CONTEXT_CAPSULE.md",
        "metadata.json",
    }
    assert saved.output_dir.exists()
    assert {path.name for path in saved.files.values()} == expected_files
    for path in saved.files.values():
        assert path.exists()

    metadata = json.loads((saved.output_dir / "metadata.json").read_text(encoding="utf-8"))
    assert metadata["generated_at"] == "2026-06-23T10:30:00"
    assert metadata["handoff_target"] == "teammate"
    assert metadata["github_issue"]["title"] == execution_packet.title
    assert metadata["github_issue"]["recommended_branch"] == execution_packet.recommended_branch
    assert metadata["github_issue"]["labels"] == execution_packet.labels
    assert metadata["github_issue"]["acceptance_criteria"] == execution_packet.acceptance_criteria
    assert metadata["token_budget"]["verification_status"] == "Estimated only"
    assert metadata["token_evidence"]["estimated_reduction_percent"] == capsule.token_budget.estimated_reduction_percent
    assert metadata["token_evidence"]["verification_status"] == "Estimated only"
    assert metadata["token_evidence"]["actual_provider_usage"] == "Not measured yet"
    assert metadata["token_evidence"]["candidate_file_context_tokens"] == capsule.token_budget.raw_context_tokens


def test_save_output_packet_avoids_directory_collision(tmp_path):
    capsule = build_sample_capsule()
    execution_packet = build_execution_packet(capsule)
    generated_at = datetime(2026, 6, 23, 10, 30, 0)

    first = save_output_packet(capsule, execution_packet, output_root=tmp_path, generated_at=generated_at)
    second = save_output_packet(capsule, execution_packet, output_root=tmp_path, generated_at=generated_at)

    assert first.output_dir != second.output_dir
    assert second.output_dir.name.endswith("_2")
