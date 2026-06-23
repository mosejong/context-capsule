from __future__ import annotations

import re
from datetime import datetime

from app.schemas.capsule_schema import CapsuleOutput, ExecutionPacket, RiskKind, RiskLevel

BLOCKING_LEVELS = {RiskLevel.HIGH, RiskLevel.BLOCKED}
RISK_PRIORITY = {
    RiskLevel.LOW: 0,
    RiskLevel.MEDIUM: 1,
    RiskLevel.HIGH: 2,
    RiskLevel.BLOCKED: 3,
}


def build_execution_packet(capsule: CapsuleOutput) -> ExecutionPacket:
    blocking_findings = [
        finding
        for finding in capsule.risk_findings
        if finding.kind == RiskKind.CHANGE and finding.level in BLOCKING_LEVELS
    ]
    needs_clarification = capsule.request_understanding.needs_clarification
    auto_start_allowed = not blocking_findings and not needs_clarification
    block_reason = (
        capsule.request_understanding.clarification_question
        if needs_clarification
        else build_block_reason(blocking_findings)
    )
    title = build_issue_title(capsule.task_request)
    recommended_branch = build_branch_name(title)
    risk_level = compute_risk_level(capsule)
    labels = build_issue_labels(capsule, risk_level, auto_start_allowed)
    acceptance_criteria = build_acceptance_criteria(auto_start_allowed)

    decision_record = build_decision_record(capsule, auto_start_allowed, block_reason)
    issue_body = build_issue_body(
        capsule,
        auto_start_allowed,
        block_reason,
        recommended_branch,
        risk_level,
        labels,
        acceptance_criteria,
    )

    return ExecutionPacket(
        title=title,
        issue_body=issue_body,
        decision_record=decision_record,
        auto_start_allowed=auto_start_allowed,
        block_reason=block_reason,
        recommended_branch=recommended_branch,
        labels=labels,
        risk_level=risk_level,
        acceptance_criteria=acceptance_criteria,
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


def compute_risk_level(capsule: CapsuleOutput) -> RiskLevel:
    if not capsule.risk_findings:
        return RiskLevel.LOW
    return max(capsule.risk_findings, key=lambda item: RISK_PRIORITY[item.level]).level


def build_issue_labels(capsule: CapsuleOutput, risk_level: RiskLevel, auto_start_allowed: bool) -> list[str]:
    gate_label = "auto-start:allowed" if auto_start_allowed else "auto-start:blocked"
    approval_label = "ready-for-brief" if auto_start_allowed else "needs-human-approval"
    return [
        "context-capsule",
        f"handoff:{capsule.handoff_target.value}",
        f"risk:{risk_level.value.lower()}",
        gate_label,
        approval_label,
    ]


def build_acceptance_criteria(auto_start_allowed: bool) -> list[str]:
    criteria = [
        "관련 파일과 작업 범위가 이슈 본문에 명확히 남아 있다.",
        "변경 후 테스트 또는 실행 확인 결과를 남긴다.",
        "완료 기준과 검증 방법을 담당자가 확인할 수 있다.",
    ]
    if not auto_start_allowed:
        criteria.insert(1, "HIGH/BLOCKED change risk는 사람 승인 전까지 실행하지 않는다.")
    return criteria


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
            block_reason or "No HIGH/BLOCKED change risk found.",
        ]
    )


def build_issue_body(
    capsule: CapsuleOutput,
    auto_start_allowed: bool,
    block_reason: str | None,
    recommended_branch: str,
    risk_level: RiskLevel,
    labels: list[str],
    acceptance_criteria: list[str],
) -> str:
    context_lines = [
        f"- `{chunk.path}:{chunk.start_line}-{chunk.end_line}` - score {chunk.score:.2f}"
        for chunk in capsule.relevant_chunks
    ]
    risk_lines = [
        f"- **{finding.kind.value} / {finding.level.value}** - "
        f"{finding.reason} / `{finding.path or finding.evidence or 'task'}`"
        for finding in capsule.risk_findings
    ]
    checklist_lines = [f"- [ ] {item}" for item in capsule.approval_checklist]
    acceptance_lines = [f"- [ ] {item}" for item in acceptance_criteria]

    return f"""# Context Capsule Execution Packet

## Issue Metadata

- Recommended branch: `{recommended_branch}`
- Labels: {", ".join(f"`{label}`" for label in labels)}
- Risk level: {risk_level.value}

## Task Request

{capsule.task_request}

## Request Understanding

- Intent: {capsule.request_understanding.intent}
- Confidence: {capsule.request_understanding.confidence_label} ({capsule.request_understanding.confidence:.2f})
- Needs clarification: {capsule.request_understanding.needs_clarification}
- Clarification question: {capsule.request_understanding.clarification_question or "None"}
- Target hints: {", ".join(capsule.request_understanding.target_hints) if capsule.request_understanding.target_hints else "None"}
- Protected hints: {", ".join(capsule.request_understanding.protected_hints) if capsule.request_understanding.protected_hints else "None"}
- File hints: {", ".join(capsule.request_understanding.file_hints) if capsule.request_understanding.file_hints else "None"}

## Retrieval Report

- Requested mode: {capsule.retrieval_report.requested_mode}
- Used mode: {capsule.retrieval_report.used_mode}
- Fallback reason: {capsule.retrieval_report.fallback_reason or "None"}
- Index path: {capsule.retrieval_report.index_path or "None"}

## Project Summary

{capsule.project_summary}

## Auto Start Gate

- Status: {"allowed" if auto_start_allowed else "blocked"}
- Reason: {block_reason or "No HIGH/BLOCKED change risk found."}

## Token Budget

- Candidate file context estimate: {capsule.token_budget.raw_context_tokens:,} tokens
- Retrieved context estimate: {capsule.token_budget.retrieved_context_tokens:,} tokens
- Handoff prompt estimate: {capsule.token_budget.handoff_prompt_tokens:,} tokens
- Estimated reduction: {capsule.token_budget.estimated_reduction_percent:.1f}%
- Method: {capsule.token_budget.method}
- Baseline scope: {capsule.token_budget.baseline_context_scope}
- Verification status: {capsule.token_budget.verification_status}
- Actual provider usage: {capsule.token_budget.actual_provider_usage}

## Relevant Context

{chr(10).join(context_lines) if context_lines else "- 관련 컨텍스트 없음"}

## Risk Findings

{chr(10).join(risk_lines) if risk_lines else "- 뚜렷한 위험 신호 없음"}

## Human Approval Checklist

{chr(10).join(checklist_lines)}

## Acceptance Criteria

{chr(10).join(acceptance_lines)}

## AI / Teammate Handoff

```text
{capsule.handoff_prompt}
```
"""
