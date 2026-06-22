from __future__ import annotations

import re
from datetime import datetime

from app.schemas.capsule_schema import CapsuleOutput, ExecutionPacket, RiskKind, RiskLevel

BLOCKING_LEVELS = {RiskLevel.HIGH, RiskLevel.BLOCKED}


def build_execution_packet(capsule: CapsuleOutput) -> ExecutionPacket:
    blocking_findings = [
        finding
        for finding in capsule.risk_findings
        if finding.kind == RiskKind.CHANGE and finding.level in BLOCKING_LEVELS
    ]
    auto_start_allowed = not blocking_findings
    block_reason = build_block_reason(blocking_findings)
    title = build_issue_title(capsule.task_request)

    decision_record = build_decision_record(capsule, auto_start_allowed, block_reason)
    issue_body = build_issue_body(capsule, auto_start_allowed, block_reason)

    return ExecutionPacket(
        title=title,
        issue_body=issue_body,
        decision_record=decision_record,
        auto_start_allowed=auto_start_allowed,
        block_reason=block_reason,
        recommended_branch=build_branch_name(title),
    )


def build_issue_title(task_request: str) -> str:
    first_line = next((line.strip("- #") for line in task_request.splitlines() if line.strip()), "Context Capsule task")
    first_line = re.sub(r"\s+", " ", first_line).strip()
    if len(first_line) <= 72:
        return first_line
    return first_line[:69].rstrip() + "..."


def build_branch_name(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.lower()).strip("-")
    slug = re.sub(r"-+", "-", slug)
    if not slug:
        slug = "context-capsule-task"
    return f"task/{slug[:48]}"


def build_block_reason(blocking_findings) -> str | None:
    if not blocking_findings:
        return None
    reasons = []
    for finding in blocking_findings[:5]:
        reasons.append(
            f"{finding.kind.value} / {finding.level.value}: "
            f"{finding.reason} ({finding.path or finding.evidence or 'task'})"
        )
    return "; ".join(reasons)


def build_decision_record(capsule: CapsuleOutput, auto_start_allowed: bool, block_reason: str | None) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return "\n".join(
        [
            "# Decision Record",
            "",
            f"Generated at: {generated_at}",
            "",
            "## Decision",
            capsule.task_request,
            "",
            "## Handoff Target",
            capsule.handoff_target.value,
            "",
            "## Auto Start",
            "allowed" if auto_start_allowed else "blocked",
            "",
            "## Block Reason",
            block_reason or "No HIGH/BLOCKED risk found.",
        ]
    )


def build_issue_body(capsule: CapsuleOutput, auto_start_allowed: bool, block_reason: str | None) -> str:
    context_lines = [
        f"- `{chunk.path}:{chunk.start_line}-{chunk.end_line}` — score {chunk.score:.2f}"
        for chunk in capsule.relevant_chunks
    ]
    risk_lines = [
        f"- **{finding.kind.value} / {finding.level.value}** — "
        f"{finding.reason} / `{finding.path or finding.evidence or 'task'}`"
        for finding in capsule.risk_findings
    ]
    checklist_lines = [f"- [ ] {item}" for item in capsule.approval_checklist]
    acceptance_lines = [
        "- [ ] 관련 파일과 작업 범위가 이슈 본문에 명확히 남아 있다.",
        "- [ ] HIGH/BLOCKED change risk는 사람 승인 전까지 실행하지 않는다.",
        "- [ ] 변경 후 테스트 또는 실행 확인 결과를 남긴다.",
    ]

    return f"""# Context Capsule Execution Packet

## Task Request

{capsule.task_request}

## Project Summary

{capsule.project_summary}

## Auto Start Gate

- Status: {"allowed" if auto_start_allowed else "blocked"}
- Reason: {block_reason or "No HIGH/BLOCKED risk found."}

## Token Budget

- Raw context estimate: {capsule.token_budget.raw_context_tokens:,} tokens
- Retrieved context estimate: {capsule.token_budget.retrieved_context_tokens:,} tokens
- Handoff prompt estimate: {capsule.token_budget.handoff_prompt_tokens:,} tokens
- Estimated reduction: {capsule.token_budget.estimated_reduction_percent:.1f}%
- Method: {capsule.token_budget.method}
- Verification status: {capsule.token_budget.verification_status}
- Actual provider usage: {capsule.token_budget.actual_provider_usage}

## Relevant Context

{chr(10).join(context_lines) if context_lines else "- 관련 컨텍스트 없음"}

## Risk Findings

{chr(10).join(risk_lines) if risk_lines else "- 특별한 위험 신호 없음"}

## Human Approval Checklist

{chr(10).join(checklist_lines)}

## Acceptance Criteria

{chr(10).join(acceptance_lines)}

## AI / Teammate Handoff

```text
{capsule.handoff_prompt}
```
"""
