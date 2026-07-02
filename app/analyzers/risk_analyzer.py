from __future__ import annotations

import re

from app.security.redaction import (
    PROMPT_INJECTION_PLACEHOLDER,
    SECRET_PLACEHOLDER,
    has_prompt_injection_or_redaction,
    has_secret_or_redaction,
)
from app.schemas.capsule_schema import FileKind, RepoChunk, RiskFinding, RiskKind, RiskLevel

RISK_RULES: list[tuple[RiskLevel, str, list[str]]] = [
    (
        RiskLevel.BLOCKED,
        "secret/env/credential 변경 또는 노출 가능성",
        [
            "secret",
            "credential",
            ".env",
            "environment variable",
            "환경변수",
            "api_key",
            "access_token",
            "refresh_token",
            "private_key",
            SECRET_PLACEHOLDER.lower(),
            "redacted_secret",
        ],
    ),
    (
        RiskLevel.BLOCKED,
        "프롬프트 인젝션 또는 승인 우회 지시문 가능성",
        [PROMPT_INJECTION_PLACEHOLDER.lower(), "system override", "ignore all previous instructions"],
    ),
    (
        RiskLevel.HIGH,
        "인증/권한 로직 영향 가능성",
        ["auth", "jwt", "login", "password", "permission", "token", "로그인", "인증", "권한"],
    ),
    (RiskLevel.HIGH, "DB schema 또는 migration 영향 가능성", ["schema", "migration", "database", "model", "table", "column"]),
    (RiskLevel.HIGH, "배포/인프라 설정 영향 가능성", ["docker", "nginx", "deploy", "production", "ssl"]),
    (RiskLevel.MEDIUM, "API 응답 형식 변경 가능성", ["response", "router", "endpoint", "api", "status_code"]),
    (RiskLevel.MEDIUM, "테스트 보강 또는 검증 필요", ["test", "pytest", "spec"]),
]
SAFE_TOKEN_CONTEXTS = [
    "token budget",
    "token analyzer",
    "token estimate",
    "token count",
    "token reduction",
    "token usage",
]
CHANGE_INTENT_KEYWORDS = [
    "수정",
    "변경",
    "고치",
    "고쳐",
    "구현",
    "추가",
    "삭제",
    "교체",
    "연동",
    "개선",
    "fix",
    "modify",
    "change",
    "update",
    "implement",
    "add",
    "remove",
    "delete",
    "migrate",
    "deploy",
    "refactor",
]
DOC_ONLY_HINTS = ["readme", "docs", "문서", "포트폴리오", "설명", "요약", "정리"]
NEGATION_HINTS = [
    "do not",
    "don't",
    "dont",
    "never",
    "avoid",
    "forbidden",
    "no ",
    "금지",
    "하지 마",
    "하지 말",
    "건드리지 마",
    "건드리지 말",
    "수정하지 마",
    "수정하지 말",
    "변경하지 마",
    "변경하지 말",
]
METRIC_TASK_HINTS = [
    "accuracy",
    "정확도",
    "수치",
    "metric",
    "score",
    "성능",
    "qa",
    "defense",
    "포트폴리오",
    "portfolio",
    "readme",
    "docs",
    "문서",
]
METRIC_CONTEXT_HINTS = [
    "accuracy",
    "정확도",
    "성능",
    "score",
    "점수",
    "qa",
    "defense",
    "pass",
    "hit@",
]
NON_COMPARABLE_PERCENT_HINTS = [
    "token",
    "토큰",
    "reduction",
    "감소율",
    "줄이",
    "과금",
    "billing",
]
PERCENT_PATTERN = re.compile(r"\b\d{1,3}(?:\.\d{1,2})?%")


def analyze_risk(task_request: str, chunks: list[RepoChunk], forbidden_rules: list[str]) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    combined_task = task_request.lower()
    change_intent = has_change_intent(combined_task)
    doc_only = is_doc_or_summary_task(combined_task)

    for level, reason, keywords in RISK_RULES:
        for keyword in keywords:
            if keyword in combined_task and not is_safe_keyword_context(keyword, combined_task):
                negated = is_negated_keyword_context(keyword, combined_task)
                kind = RiskKind.CHANGE if change_intent and not negated else RiskKind.MENTION
                findings.append(
                    RiskFinding(
                        level=level if kind == RiskKind.CHANGE else mention_level(level),
                        kind=kind,
                        reason=reason,
                        evidence=keyword,
                    )
                )
                break

    if has_secret_or_redaction(task_request):
        findings.append(
            RiskFinding(
                level=RiskLevel.BLOCKED,
                kind=RiskKind.CHANGE,
                reason="작업 요청에 secret 또는 credential 패턴이 포함되어 마스킹되었습니다.",
                evidence=SECRET_PLACEHOLDER,
            )
        )
    if has_prompt_injection_or_redaction(task_request):
        findings.append(
            RiskFinding(
                level=RiskLevel.BLOCKED,
                kind=RiskKind.CHANGE,
                reason="작업 요청에 프롬프트 인젝션 또는 승인 우회 지시문이 포함되어 마스킹되었습니다.",
                evidence=PROMPT_INJECTION_PLACEHOLDER,
            )
        )

    if doc_only and is_portfolio_or_readme_task(combined_task):
        findings.append(
            RiskFinding(
                level=RiskLevel.MEDIUM,
                kind=RiskKind.MENTION,
                reason="포트폴리오/README 문서 정확도, 과장 표현, secret 노출 여부 확인 필요",
                evidence="documentation quality guard",
            )
        )

    for chunk in chunks:
        haystack = f"{chunk.path}\n{chunk.text}".lower()
        if has_secret_or_redaction(chunk.text):
            findings.append(
                RiskFinding(
                    level=RiskLevel.BLOCKED,
                    kind=RiskKind.CHANGE,
                    reason="검색된 컨텍스트에 secret 또는 credential 패턴이 포함되어 마스킹되었습니다.",
                    evidence=SECRET_PLACEHOLDER,
                    path=chunk.path,
                )
            )
        if has_prompt_injection_or_redaction(chunk.text):
            findings.append(
                RiskFinding(
                    level=RiskLevel.BLOCKED,
                    kind=RiskKind.CHANGE,
                    reason="검색된 컨텍스트에 프롬프트 인젝션 또는 승인 우회 지시문이 포함되어 마스킹되었습니다.",
                    evidence=PROMPT_INJECTION_PLACEHOLDER,
                    path=chunk.path,
                )
            )
        for level, reason, keywords in RISK_RULES:
            for keyword in keywords:
                if keyword in haystack and not is_safe_keyword_context(keyword, haystack):
                    kind = classify_chunk_risk_kind(chunk, combined_task, change_intent, doc_only, keyword, keywords)
                    if kind is None:
                        continue
                    findings.append(
                        RiskFinding(
                            level=level if kind == RiskKind.CHANGE else mention_level(level),
                            kind=kind,
                            reason=reason,
                            evidence=keyword,
                            path=chunk.path,
                        )
                    )
                    break

    for rule in forbidden_rules:
        if rule.strip():
            findings.append(
                RiskFinding(
                    level=RiskLevel.MEDIUM,
                    kind=RiskKind.MENTION,
                    reason="사용자가 직접 지정한 금지/주의 규칙",
                    evidence=rule.strip(),
                )
            )

    findings.extend(detect_metric_conflicts(combined_task, chunks))

    return deduplicate_findings(findings)


def is_safe_keyword_context(keyword: str, haystack: str) -> bool:
    if keyword != "token":
        return False
    return any(context in haystack for context in SAFE_TOKEN_CONTEXTS)


def has_change_intent(text: str) -> bool:
    return any(keyword in text for keyword in CHANGE_INTENT_KEYWORDS)


def is_negated_keyword_context(keyword: str, text: str) -> bool:
    index = text.find(keyword)
    if index < 0:
        return False
    start = max(0, index - 40)
    end = min(len(text), index + len(keyword) + 40)
    window = text[start:end]
    return any(hint in window for hint in NEGATION_HINTS)


def is_doc_or_summary_task(text: str) -> bool:
    return any(keyword in text for keyword in DOC_ONLY_HINTS)


def is_portfolio_or_readme_task(text: str) -> bool:
    return any(
        keyword in text
        for keyword in (
            "portfolio",
            "포트폴리오",
            "포폴",
            "성과",
            "수치",
            "정확도",
            "metric",
            "accuracy",
            "qa",
            "defense",
        )
    )


def detect_metric_conflicts(task_request: str, chunks: list[RepoChunk]) -> list[RiskFinding]:
    if not should_check_metric_conflicts(task_request, chunks):
        return []

    values_by_percent: dict[str, set[str]] = {}
    for chunk in chunks:
        if chunk.kind not in {FileKind.DOC, FileKind.UNKNOWN}:
            continue
        for percent in comparable_metric_percents(chunk):
            values_by_percent.setdefault(percent, set()).add(chunk.path)

    if len(values_by_percent) < 2:
        return []

    evidence_parts = []
    for percent, paths in sorted(values_by_percent.items(), key=lambda item: item[0]):
        sample_paths = ", ".join(sorted(paths)[:2])
        evidence_parts.append(f"{percent} in {sample_paths}")

    return [
        RiskFinding(
            level=RiskLevel.MEDIUM,
            kind=RiskKind.MENTION,
            reason="문서 간 수치 값이 서로 달라 확인 필요",
            evidence="; ".join(evidence_parts[:4]),
        )
    ]


def should_check_metric_conflicts(task_request: str, chunks: list[RepoChunk]) -> bool:
    if any(hint in task_request for hint in METRIC_TASK_HINTS):
        return True
    return any(metric_context_is_relevant(chunk) for chunk in chunks)


def metric_context_is_relevant(chunk: RepoChunk) -> bool:
    return bool(comparable_metric_percents(chunk))


def comparable_metric_percents(chunk: RepoChunk) -> list[str]:
    text = f"{chunk.path}\n{chunk.text}".lower()
    values: list[str] = []
    for match in PERCENT_PATTERN.finditer(text):
        start = max(0, match.start() - 80)
        end = min(len(text), match.end() + 80)
        sentence = metric_sentence_window(text, match.start(), match.end())
        surrounding = text[start:end]
        if any(hint in sentence for hint in NON_COMPARABLE_PERCENT_HINTS) and not any(
            hint in sentence for hint in METRIC_CONTEXT_HINTS
        ):
            continue
        if any(hint in sentence for hint in METRIC_CONTEXT_HINTS):
            values.append(match.group())
            continue
        if any(hint in surrounding for hint in METRIC_CONTEXT_HINTS) and not any(
            hint in surrounding for hint in NON_COMPARABLE_PERCENT_HINTS
        ):
            values.append(match.group())
    return values


def metric_sentence_window(text: str, start: int, end: int) -> str:
    left = max(text.rfind("\n", 0, start), text.rfind(".", 0, start), text.rfind("。", 0, start))
    right_candidates = [index for index in (text.find("\n", end), text.find(".", end), text.find("。", end)) if index >= 0]
    right = min(right_candidates) if right_candidates else len(text)
    return text[left + 1 : right]


def classify_chunk_risk_kind(
    chunk: RepoChunk,
    task_request: str,
    change_intent: bool,
    doc_only: bool,
    matched_keyword: str,
    keywords: list[str],
) -> RiskKind | None:
    keyword_in_task = matched_keyword in task_request
    keyword_is_positive = keyword_in_task and not is_negated_keyword_context(matched_keyword, task_request)
    domain_is_positive = any(
        keyword in task_request and not is_negated_keyword_context(keyword, task_request) for keyword in keywords
    )
    if doc_only and chunk.kind in {FileKind.CODE, FileKind.TEST} and not domain_is_positive:
        return None
    if doc_only and chunk.kind == FileKind.DOC:
        return RiskKind.MENTION
    if not change_intent:
        return RiskKind.MENTION
    if chunk.kind == FileKind.DOC and not domain_is_positive:
        return RiskKind.MENTION
    if keyword_is_positive:
        return RiskKind.CHANGE
    if is_negated_keyword_context(matched_keyword, task_request):
        return RiskKind.MENTION
    if chunk.kind == FileKind.TEST:
        return RiskKind.MENTION
    if chunk.kind == FileKind.CONFIG and domain_is_positive and matched_keyword in chunk.path.lower():
        return RiskKind.CHANGE
    if chunk.kind == FileKind.CODE and domain_is_positive and matched_keyword in chunk.path.lower():
        return RiskKind.CHANGE
    return RiskKind.MENTION


def mention_level(level: RiskLevel) -> RiskLevel:
    if level in {RiskLevel.BLOCKED, RiskLevel.HIGH}:
        return RiskLevel.MEDIUM
    if level == RiskLevel.MEDIUM:
        return RiskLevel.LOW
    return level


def deduplicate_findings(findings: list[RiskFinding]) -> list[RiskFinding]:
    seen: set[tuple[str, str, str, str | None]] = set()
    unique: list[RiskFinding] = []
    for finding in findings:
        key = (finding.level.value, finding.kind.value, finding.reason, finding.evidence)
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)
    return unique


def build_approval_checklist(findings: list[RiskFinding]) -> list[str]:
    checklist = [
        "작업 범위가 사용자의 요청과 일치하는가?",
        "변경 대상 파일이 관련 컨텍스트 안에 포함되어 있는가?",
        "AI가 직접 적용하기 전에 수정안과 영향도를 먼저 설명하는가?",
    ]

    if any(item.kind == RiskKind.CHANGE and item.level in {RiskLevel.HIGH, RiskLevel.BLOCKED} for item in findings):
        checklist.extend(
            [
                "DB schema, 인증, 배포, secret 관련 변경이 포함되어 있지 않은가?",
                "위험도가 높은 변경은 사용자 승인 전까지 보류되는가?",
            ]
        )

    return checklist
