from __future__ import annotations

from app.schemas.capsule_schema import FileKind, RepoChunk, RiskFinding, RiskKind, RiskLevel

RISK_RULES: list[tuple[RiskLevel, str, list[str]]] = [
    (
        RiskLevel.BLOCKED,
        "secret/env/credential 변경 또는 노출 가능성",
        ["secret", "credential", ".env", "api_key", "access_token", "refresh_token", "private_key"],
    ),
    (RiskLevel.HIGH, "인증/권한 로직 영향 가능성", ["auth", "jwt", "login", "password", "permission", "token"]),
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


def analyze_risk(task_request: str, chunks: list[RepoChunk], forbidden_rules: list[str]) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    combined_task = task_request.lower()
    change_intent = has_change_intent(combined_task)
    doc_only = is_doc_or_summary_task(combined_task)

    for level, reason, keywords in RISK_RULES:
        for keyword in keywords:
            if keyword in combined_task and not is_safe_keyword_context(keyword, combined_task):
                kind = RiskKind.CHANGE if change_intent else RiskKind.MENTION
                findings.append(
                    RiskFinding(
                        level=level if kind == RiskKind.CHANGE else mention_level(level),
                        kind=kind,
                        reason=reason,
                        evidence=keyword,
                    )
                )
                break

    for chunk in chunks:
        haystack = f"{chunk.path}\n{chunk.text}".lower()
        for level, reason, keywords in RISK_RULES:
            for keyword in keywords:
                if keyword in haystack and not is_safe_keyword_context(keyword, haystack):
                    kind = classify_chunk_risk_kind(chunk, combined_task, change_intent, doc_only, keywords)
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

    return deduplicate_findings(findings)


def is_safe_keyword_context(keyword: str, haystack: str) -> bool:
    if keyword != "token":
        return False
    return any(context in haystack for context in SAFE_TOKEN_CONTEXTS)


def has_change_intent(text: str) -> bool:
    return any(keyword in text for keyword in CHANGE_INTENT_KEYWORDS)


def is_doc_or_summary_task(text: str) -> bool:
    return any(keyword in text for keyword in DOC_ONLY_HINTS)


def classify_chunk_risk_kind(
    chunk: RepoChunk,
    task_request: str,
    change_intent: bool,
    doc_only: bool,
    keywords: list[str],
) -> RiskKind:
    if doc_only and chunk.kind == FileKind.DOC:
        return RiskKind.MENTION
    if not change_intent:
        return RiskKind.MENTION
    if chunk.kind == FileKind.DOC and not any(keyword in task_request for keyword in keywords):
        return RiskKind.MENTION
    if any(keyword in task_request for keyword in keywords):
        return RiskKind.CHANGE
    if chunk.kind in {FileKind.CODE, FileKind.CONFIG} and not doc_only:
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
        key = (finding.level.value, finding.kind.value, finding.reason, finding.path)
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
