from __future__ import annotations

import re

from app.schemas.capsule_schema import ChatTaskExtraction

PATH_PATTERN = re.compile(
    r"(?P<path>(?:[\w.-]+[\\/])+[\w.-]+\.[A-Za-z0-9_]+|[\w.-]+\.[A-Za-z0-9_]+)"
)
ERROR_HINTS = (
    "error",
    "exception",
    "traceback",
    "failed",
    "failure",
    "에러",
    "오류",
    "실패",
    "안됨",
    "안 돼",
    "안되",
)
DECISION_HINTS = (
    "/fix",
    "fix",
    "확정",
    "픽스",
    "이걸로 가자",
    "이 방향",
    "만들자",
    "진행",
    "go",
)
BUILD_HINTS = ("구현", "추가", "만들", "붙이", "연동", "자동화", "생성")
SUMMARY_HINTS = ("요약", "정리", "브리프", "문서")


def extract_task_request(chat_log: str) -> ChatTaskExtraction:
    lines = [line.strip() for line in chat_log.splitlines() if line.strip()]
    detected_paths = dedupe(match.group("path").replace("\\", "/") for match in PATH_PATTERN.finditer(chat_log))
    error_hints = pick_lines(lines, ERROR_HINTS)
    decision_hints = pick_lines(lines, DECISION_HINTS)
    source_excerpt = build_excerpt(decision_hints or error_hints or lines)
    task_request = build_task_request(chat_log, source_excerpt, detected_paths, error_hints, decision_hints)
    confidence = score_confidence(detected_paths, error_hints, decision_hints, task_request)

    return ChatTaskExtraction(
        task_request=task_request,
        detected_paths=detected_paths,
        error_hints=error_hints[:5],
        decision_hints=decision_hints[:5],
        source_excerpt=source_excerpt,
        confidence=confidence,
    )


def pick_lines(lines: list[str], hints: tuple[str, ...]) -> list[str]:
    selected = []
    for line in lines:
        lower = line.lower()
        if any(hint.lower() in lower for hint in hints):
            selected.append(line)
    return selected


def build_excerpt(lines: list[str], limit: int = 5) -> str:
    if not lines:
        return ""
    return "\n".join(lines[-limit:])


def build_task_request(
    chat_log: str,
    source_excerpt: str,
    detected_paths: list[str],
    error_hints: list[str],
    decision_hints: list[str],
) -> str:
    lower = chat_log.lower()

    if error_hints:
        intent = "대화 로그에서 언급된 오류 원인을 분석하고, 관련 파일 기준으로 수정 계획과 검증 방법을 제안해줘."
    elif any(hint in lower for hint in BUILD_HINTS):
        intent = "대화 로그에서 확정된 아이디어를 구현 가능한 작업 브리프로 정리해줘."
    elif any(hint in lower for hint in SUMMARY_HINTS):
        intent = "대화 로그를 요약하고 다음 작업으로 옮길 수 있는 브리프로 정리해줘."
    else:
        intent = "대화 로그에서 실행 가능한 작업 요청을 추출하고 관련 파일, 위험도, 완료 기준을 정리해줘."

    details = []
    if decision_hints:
        details.append("결정/진행 힌트:\n" + "\n".join(f"- {line}" for line in decision_hints[:3]))
    if error_hints:
        details.append("오류 힌트:\n" + "\n".join(f"- {line}" for line in error_hints[:3]))
    if detected_paths:
        details.append("언급된 파일:\n" + "\n".join(f"- {path}" for path in detected_paths[:8]))
    if source_excerpt:
        details.append("근거 대화 발췌:\n" + source_excerpt)

    if not details:
        return intent
    return intent + "\n\n" + "\n\n".join(details)


def score_confidence(
    detected_paths: list[str],
    error_hints: list[str],
    decision_hints: list[str],
    task_request: str,
) -> float:
    score = 0.25
    if detected_paths:
        score += 0.25
    if error_hints:
        score += 0.2
    if decision_hints:
        score += 0.2
    if len(task_request) > 80:
        score += 0.1
    return min(round(score, 2), 1.0)


def dedupe(items) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result
