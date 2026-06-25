from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from app.generators.output_writer import safe_write_text, slugify
from app.schemas.capsule_schema import BetaFeedback, FeedbackIssue, FeedbackReviewOutput, FeedbackSaveResult
from app.security.redaction import sanitize_untrusted_text

DEFAULT_FEEDBACK_ROOT = Path("outputs") / "feedback"


def save_beta_feedback(
    feedback: BetaFeedback,
    output_root: Path | str = DEFAULT_FEEDBACK_ROOT,
    generated_at: datetime | None = None,
) -> FeedbackSaveResult:
    generated_at = generated_at or datetime.now()
    safe_feedback, secret_count, injection_count = sanitize_feedback(feedback, generated_at)
    output_dir = next_feedback_dir(Path(output_root), generated_at, safe_feedback)
    output_dir.mkdir(parents=True, exist_ok=False)

    markdown_path = output_dir / "FEEDBACK.md"
    json_path = output_dir / "feedback.json"
    safe_write_text(markdown_path, render_feedback_markdown(safe_feedback))
    safe_write_text(
        json_path,
        json.dumps(safe_feedback.model_dump(mode="json"), ensure_ascii=False, indent=2),
    )

    return FeedbackSaveResult(
        output_dir=str(output_dir),
        markdown_path=str(markdown_path),
        json_path=str(json_path),
        redacted_secret_count=secret_count,
        redacted_prompt_injection_count=injection_count,
    )


def review_feedback(feedback_root: Path | str = DEFAULT_FEEDBACK_ROOT) -> FeedbackReviewOutput:
    feedback_items = load_feedback_items(Path(feedback_root))
    common_issues = build_common_issues(feedback_items)
    missed_file_cases = build_missed_file_cases(feedback_items)
    ui_confusion_points = unique_nonempty(
        item.confusing_part for item in feedback_items if looks_like_ui_confusion(item)
    )
    token_questions = unique_nonempty(
        item.notes or item.token_evidence
        for item in feedback_items
        if contains_any(join_feedback_text(item), ["토큰", "token", "절감", "계산"])
    )
    risk_questions = unique_nonempty(
        item.notes or item.risk_result
        for item in feedback_items
        if contains_any(join_feedback_text(item), ["위험", "risk", "blocked", "차단", "승인"])
    )
    workflow_trace_questions = unique_nonempty(
        item.workflow_trace_feedback
        for item in feedback_items
        if item.workflow_trace_feedback.strip()
    )
    priorities = build_priorities(
        common_issues,
        missed_file_cases,
        ui_confusion_points,
        token_questions,
        risk_questions,
        workflow_trace_questions,
    )
    regression_candidates = build_regression_candidates(feedback_items)
    safety_notes = [
        "이 결과는 팀원 평가가 아니라 제품 개선용 피드백 요약입니다.",
        "자동 배정, 자동 수정, 자동 GitHub 작업 생성에 사용하지 않습니다.",
        "저장 전 secret과 prompt-injection 의심 문장은 마스킹합니다.",
    ]
    output = FeedbackReviewOutput(
        feedback_count=len(feedback_items),
        common_issues=common_issues,
        missed_file_cases=missed_file_cases,
        ui_confusion_points=ui_confusion_points,
        token_questions=token_questions,
        risk_questions=risk_questions,
        workflow_trace_questions=workflow_trace_questions,
        next_patch_priorities=priorities,
        regression_test_candidates=regression_candidates,
        safety_notes=safety_notes,
        markdown="",
    )
    output.markdown = render_feedback_review_markdown(output)
    return output


def load_feedback_items(feedback_root: Path) -> list[BetaFeedback]:
    if not feedback_root.exists():
        return []
    items: list[BetaFeedback] = []
    for path in sorted(feedback_root.rglob("feedback.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            items.append(BetaFeedback(**data))
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            continue
    return items


def save_feedback_review(
    review: FeedbackReviewOutput,
    output_root: Path | str = Path("outputs"),
    generated_at: datetime | None = None,
) -> Path:
    generated_at = generated_at or datetime.now()
    output_root = Path(output_root)
    output_dir = output_root / f"{generated_at.strftime('%Y%m%d_%H%M%S')}_feedback-review"
    suffix = 2
    while output_dir.exists():
        output_dir = output_root / f"{generated_at.strftime('%Y%m%d_%H%M%S')}_feedback-review_{suffix}"
        suffix += 1
    output_dir.mkdir(parents=True, exist_ok=False)
    safe_write_text(output_dir / "FEEDBACK_REVIEW.md", review.markdown)
    safe_write_text(
        output_dir / "feedback_review.json",
        json.dumps(review.model_dump(mode="json"), ensure_ascii=False, indent=2),
    )
    return output_dir


def sanitize_feedback(feedback: BetaFeedback, generated_at: datetime) -> tuple[BetaFeedback, int, int]:
    values = feedback.model_dump(mode="json")
    secret_count = 0
    injection_count = 0
    for key, value in values.items():
        if isinstance(value, str):
            sanitized = sanitize_untrusted_text(value)
            values[key] = sanitized.text
            secret_count += sanitized.secret_count
            injection_count += sanitized.prompt_injection_count
        elif isinstance(value, list):
            safe_values: list[str] = []
            for item in value:
                sanitized = sanitize_untrusted_text(str(item))
                safe_values.append(sanitized.text)
                secret_count += sanitized.secret_count
                injection_count += sanitized.prompt_injection_count
            values[key] = safe_values
    if not values.get("created_at"):
        values["created_at"] = generated_at.isoformat(timespec="seconds")
    return BetaFeedback(**values), secret_count, injection_count


def next_feedback_dir(output_root: Path, generated_at: datetime, feedback: BetaFeedback) -> Path:
    label = feedback.project_name or feedback.request_text or feedback.mode or "feedback"
    base_name = f"{generated_at.strftime('%Y%m%d_%H%M%S')}_{slugify(label)}"
    output_dir = output_root / base_name
    suffix = 2
    while output_dir.exists():
        output_dir = output_root / f"{base_name}_{suffix}"
        suffix += 1
    return output_dir


def render_feedback_markdown(feedback: BetaFeedback) -> str:
    expected = "\n".join(f"- `{item}`" for item in feedback.expected_files) or "- (not provided)"
    actual = "\n".join(f"- `{item}`" for item in feedback.actual_top_files) or "- (not provided)"
    return f"""# Beta Feedback

## Basic Info
- Version: {feedback.version}
- Mode: {feedback.mode}
- Project: {feedback.project_name or "(not provided)"}
- Repo path/type: `{feedback.repo_path or "(not provided)"}` / {feedback.repo_type or "(not provided)"}
- Created at: {feedback.created_at or "(not provided)"}

## Request
{feedback.request_text or "(not provided)"}

## Expected Files
{expected}

## Actual Top Files
{actual}

## Risk Result
{feedback.risk_result or "(not provided)"}

## Token Evidence
{feedback.token_evidence or "(not provided)"}

## Result Reading Order
{feedback.result_order_feedback or "(not provided)"}

## Workflow Trace Feedback
{feedback.workflow_trace_feedback or "(not provided)"}

## Confusing UI/UX
{feedback.confusing_part or "(not provided)"}

## Reuse Willingness
{feedback.reuse_willingness or "(not provided)"}

## Notes
{feedback.notes or "(not provided)"}

## Screenshot Note
{feedback.screenshot_note or "(not provided)"}
"""


def build_common_issues(items: list[BetaFeedback]) -> list[FeedbackIssue]:
    counters: Counter[str] = Counter()
    evidence: dict[str, list[str]] = {}
    for item in items:
        text = join_feedback_text(item)
        if item.expected_files and not expected_files_are_present(item):
            add_issue(counters, evidence, "retrieval_mismatch", item)
        if looks_like_ui_confusion(item):
            add_issue(counters, evidence, "ui_confusion", item)
        if contains_any(text, ["토큰", "token", "절감", "계산"]):
            add_issue(counters, evidence, "token_evidence_question", item)
        if contains_any(text, ["위험", "risk", "blocked", "차단", "승인"]):
            add_issue(counters, evidence, "risk_message_question", item)
        if contains_any(text, ["느림", "로딩", "멈춘", "안 보여", "loading"]):
            add_issue(counters, evidence, "loading_feedback", item)
        if item.workflow_trace_feedback.strip() or contains_any(text, ["작업 흐름", "workflow", "trace", "단계", "왜 멈", "왜 차단"]):
            add_issue(counters, evidence, "workflow_trace_question", item)

    labels = {
        "retrieval_mismatch": "기대한 파일과 실제 top files가 다릅니다.",
        "ui_confusion": "사용자가 화면/버튼/탭에서 헤맸습니다.",
        "token_evidence_question": "토큰 절감 근거 설명이 더 필요합니다.",
        "risk_message_question": "위험/승인 메시지 해석이 어렵습니다.",
        "loading_feedback": "로딩 상태나 처리 진행 표시가 약합니다.",
        "workflow_trace_question": "작업 흐름 탭의 단계/상태 설명이 더 필요합니다.",
    }
    return [
        FeedbackIssue(
            category=category,
            summary=labels.get(category, category),
            count=count,
            evidence=evidence.get(category, [])[:5],
        )
        for category, count in counters.most_common()
    ]


def add_issue(counters: Counter[str], evidence: dict[str, list[str]], category: str, item: BetaFeedback) -> None:
    counters[category] += 1
    evidence.setdefault(category, []).append(item.request_text or item.notes or item.confusing_part or "(empty request)")


def build_missed_file_cases(items: list[BetaFeedback]) -> list[str]:
    cases: list[str] = []
    for item in items:
        if item.expected_files and not expected_files_are_present(item):
            cases.append(
                f"{item.request_text or '(empty request)'} -> expected {', '.join(item.expected_files)} / actual {', '.join(item.actual_top_files) or '(none)'}"
            )
    return cases


def build_priorities(
    common_issues: list[FeedbackIssue],
    missed_file_cases: list[str],
    ui_confusion_points: list[str],
    token_questions: list[str],
    risk_questions: list[str],
    workflow_trace_questions: list[str],
) -> list[str]:
    priorities: list[str] = []
    categories = {issue.category for issue in common_issues}
    if missed_file_cases or "retrieval_mismatch" in categories:
        priorities.append("검색 랭킹과 한/영 도메인 키워드 매핑을 먼저 튜닝합니다.")
    if ui_confusion_points or "ui_confusion" in categories:
        priorities.append("첫 화면, 입력 위치, 결과 탭 이름을 더 쉬운 한국어로 정리합니다.")
    if token_questions or "token_evidence_question" in categories:
        priorities.append("Token Evidence에 estimated 기준과 실제 provider usage 미측정 상태를 더 짧게 표시합니다.")
    if risk_questions or "risk_message_question" in categories:
        priorities.append("Risk & Approval을 mention risk/change risk/blocked로 나눠 설명합니다.")
    if "loading_feedback" in categories:
        priorities.append("결과 영역 로딩 상태와 실패 안내를 더 크게 표시합니다.")
    if workflow_trace_questions or "workflow_trace_question" in categories:
        priorities.append("작업 흐름 탭의 현재 단계, 상태, 다음 행동을 더 쉬운 한국어로 정리합니다.")
    if not priorities:
        priorities.append("새로운 블로커가 적습니다. 다음 베타에서는 더 다양한 외부 레포로 테스트를 넓힙니다.")
    return priorities


def build_regression_candidates(items: list[BetaFeedback]) -> list[str]:
    candidates: list[str] = []
    for item in items:
        if item.request_text and item.expected_files:
            expected = ", ".join(item.expected_files)
            candidates.append(f'입력 "{item.request_text}" -> 기대 파일: {expected}')
        elif item.request_text and looks_like_ui_confusion(item):
            candidates.append(f'입력 "{item.request_text}" -> UI 안내 문구 확인 필요')
    return unique_nonempty(candidates)[:20]


def expected_files_are_present(item: BetaFeedback) -> bool:
    actual = [normalize_path(path) for path in item.actual_top_files]
    for expected in item.expected_files:
        normalized_expected = normalize_path(expected)
        if not any(normalized_expected in path or path in normalized_expected for path in actual):
            return False
    return True


def normalize_path(path: str) -> str:
    return path.replace("\\", "/").lower().strip()


def looks_like_ui_confusion(item: BetaFeedback) -> bool:
    return bool(item.confusing_part.strip()) or contains_any(
        join_feedback_text(item),
        ["헷갈", "어디", "버튼", "입력", "화면", "탭", "ux", "ui", "로딩", "안 보"],
    )


def join_feedback_text(item: BetaFeedback) -> str:
    return "\n".join(
        [
            item.request_text,
            item.risk_result,
            item.token_evidence,
            item.result_order_feedback,
            item.workflow_trace_feedback,
            item.confusing_part,
            item.reuse_willingness,
            item.notes,
            item.screenshot_note,
        ]
    ).lower()


def contains_any(text: str, needles: list[str]) -> bool:
    lower = text.lower()
    return any(needle.lower() in lower for needle in needles)


def unique_nonempty(items) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        text = str(item).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def render_feedback_review_markdown(output: FeedbackReviewOutput) -> str:
    return f"""# Beta Feedback Review

## Summary
- Feedback count: {output.feedback_count}

## Common Issues
{render_issue_list(output.common_issues)}

## Missed File Cases
{render_plain_list(output.missed_file_cases)}

## UI Confusion Points
{render_plain_list(output.ui_confusion_points)}

## Token Questions
{render_plain_list(output.token_questions)}

## Risk Questions
{render_plain_list(output.risk_questions)}

## Workflow Trace Questions
{render_plain_list(output.workflow_trace_questions)}

## Next Patch Priorities
{render_plain_list(output.next_patch_priorities)}

## Regression Test Candidates
{render_plain_list(output.regression_test_candidates)}

## Safety Notes
{render_plain_list(output.safety_notes)}
"""


def render_issue_list(issues: list[FeedbackIssue]) -> str:
    if not issues:
        return "- No repeated issues detected."
    lines: list[str] = []
    for issue in issues:
        lines.append(f"- {issue.category} ({issue.count}): {issue.summary}")
        for evidence in issue.evidence:
            lines.append(f"  - evidence: {evidence}")
    return "\n".join(lines)


def render_plain_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None"
