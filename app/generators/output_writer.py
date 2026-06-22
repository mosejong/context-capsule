from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from app.schemas.capsule_schema import CapsuleOutput, ExecutionPacket

DEFAULT_OUTPUT_ROOT = Path("outputs")


@dataclass(frozen=True)
class SavedOutputPacket:
    output_dir: Path
    files: dict[str, Path]


def save_output_packet(
    capsule: CapsuleOutput,
    execution_packet: ExecutionPacket,
    output_root: Path | str = DEFAULT_OUTPUT_ROOT,
    generated_at: datetime | None = None,
) -> SavedOutputPacket:
    generated_at = generated_at or datetime.now()
    output_root = Path(output_root)
    output_dir = next_available_output_dir(output_root, generated_at, capsule.task_request)
    output_dir.mkdir(parents=True, exist_ok=False)

    files = {
        "overview": output_dir / "OVERVIEW.md",
        "ai_handoff_prompt": output_dir / "AI_HANDOFF_PROMPT.md",
        "teammate_brief": output_dir / "TEAMMATE_BRIEF.md",
        "junior_guide": output_dir / "JUNIOR_GUIDE.md",
        "self_handoff": output_dir / "SELF_HANDOFF.md",
        "risk_checklist": output_dir / "RISK_CHECKLIST.md",
        "github_issue": output_dir / "GITHUB_ISSUE.md",
        "decision_record": output_dir / "DECISION_RECORD.md",
        "context_capsule": output_dir / "CONTEXT_CAPSULE.md",
        "metadata": output_dir / "metadata.json",
    }

    files["overview"].write_text(capsule.sections.overview, encoding="utf-8")
    files["ai_handoff_prompt"].write_text(capsule.sections.ai_handoff_prompt, encoding="utf-8")
    files["teammate_brief"].write_text(capsule.sections.teammate_brief, encoding="utf-8")
    files["junior_guide"].write_text(capsule.sections.junior_guide, encoding="utf-8")
    files["self_handoff"].write_text(capsule.sections.future_me_letter, encoding="utf-8")
    files["risk_checklist"].write_text(capsule.sections.risk_checklist, encoding="utf-8")
    files["github_issue"].write_text(execution_packet.issue_body, encoding="utf-8")
    files["decision_record"].write_text(execution_packet.decision_record, encoding="utf-8")
    files["context_capsule"].write_text(capsule.markdown, encoding="utf-8")
    files["metadata"].write_text(
        json.dumps(build_metadata(capsule, execution_packet, generated_at), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return SavedOutputPacket(output_dir=output_dir, files=files)


def next_available_output_dir(output_root: Path, generated_at: datetime, task_request: str) -> Path:
    base_name = f"{generated_at.strftime('%Y%m%d_%H%M%S')}_{slugify(task_request)}"
    output_dir = output_root / base_name
    if not output_dir.exists():
        return output_dir

    suffix = 2
    while True:
        candidate = output_root / f"{base_name}_{suffix}"
        if not candidate.exists():
            return candidate
        suffix += 1


def slugify(text: str, max_length: int = 48) -> str:
    ascii_text = text.encode("ascii", errors="ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    slug = re.sub(r"-+", "-", slug)
    return slug[:max_length].strip("-") or "context-capsule"


def build_metadata(capsule: CapsuleOutput, execution_packet: ExecutionPacket, generated_at: datetime) -> dict:
    return {
        "generated_at": generated_at.isoformat(timespec="seconds"),
        "task_request": capsule.task_request,
        "handoff_target": capsule.handoff_target.value,
        "project_summary": capsule.project_summary,
        "output_files": {
            "overview": "OVERVIEW.md",
            "ai_handoff_prompt": "AI_HANDOFF_PROMPT.md",
            "teammate_brief": "TEAMMATE_BRIEF.md",
            "junior_guide": "JUNIOR_GUIDE.md",
            "self_handoff": "SELF_HANDOFF.md",
            "risk_checklist": "RISK_CHECKLIST.md",
            "github_issue": "GITHUB_ISSUE.md",
            "decision_record": "DECISION_RECORD.md",
            "context_capsule": "CONTEXT_CAPSULE.md",
        },
        "github_issue": {
            "title": execution_packet.title,
            "recommended_branch": execution_packet.recommended_branch,
            "labels": execution_packet.labels,
            "risk_level": execution_packet.risk_level.value,
            "auto_start_allowed": execution_packet.auto_start_allowed,
            "block_reason": execution_packet.block_reason,
            "acceptance_criteria": execution_packet.acceptance_criteria,
        },
        "token_budget": capsule.token_budget.model_dump(mode="json"),
        "relevant_context": [chunk.model_dump(mode="json") for chunk in capsule.relevant_chunks],
        "risk_findings": [finding.model_dump(mode="json") for finding in capsule.risk_findings],
        "approval_checklist": capsule.approval_checklist,
    }
