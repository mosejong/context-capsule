from __future__ import annotations

from app.schemas.capsule_schema import RepoChunk, RiskFinding, RiskLevel

RISK_RULES: list[tuple[RiskLevel, str, list[str]]] = [
    (RiskLevel.BLOCKED, "secret/env/credential 변경 또는 노출 가능성", ["secret", "credential", ".env", "api_key", "token"]),
    (RiskLevel.HIGH, "인증/권한 로직 영향 가능성", ["auth", "jwt", "login", "password", "permission"]),
    (RiskLevel.HIGH, "DB schema 또는 migration 영향 가능성", ["schema", "migration", "database", "model", "table", "column"]),
    (RiskLevel.HIGH, "배포/인프라 설정 영향 가능성", ["docker", "nginx", "deploy", "production", "ssl"]),
    (RiskLevel.MEDIUM, "API 응답 형식 변경 가능성", ["response", "router", "endpoint", "api", "status_code"]),
    (RiskLevel.MEDIUM, "테스트 보강 또는 검증 필요", ["test", "pytest", "spec"]),
]


def analyze_risk(task_request: str, chunks: list[RepoChunk], forbidden_rules: list[str]) -> list[RiskFinding]:
    findings: list[RiskFinding] = []
    combined_task = task_request.lower()

    for level, reason, keywords in RISK_RULES:
        for keyword in keywords:
            if keyword in combined_task:
                findings.append(RiskFinding(level=level, reason=reason, evidence=keyword))
                break

    for chunk in chunks:
        haystack = f"{chunk.path}\n{chunk.text}".lower()
        for level, reason, keywords in RISK_RULES:
            for keyword in keywords:
                if keyword in haystack:
                    findings.append(
                        RiskFinding(
                            level=level,
                            reason=reason,
                            evidence=keyword,
                            path=chunk.path,
                        )
                    )
                    break
            else:
                continue
            break

    for rule in forbidden_rules:
        if rule.strip():
            findings.append(
                RiskFinding(
                    level=RiskLevel.HIGH,
                    reason="사용자가 직접 지정한 금지/주의 규칙",
                    evidence=rule.strip(),
                )
            )

    return deduplicate_findings(findings)


def deduplicate_findings(findings: list[RiskFinding]) -> list[RiskFinding]:
    seen: set[tuple[str, str, str | None]] = set()
    unique: list[RiskFinding] = []
    for finding in findings:
        key = (finding.level.value, finding.reason, finding.path)
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

    if any(item.level in {RiskLevel.HIGH, RiskLevel.BLOCKED} for item in findings):
        checklist.extend(
            [
                "DB schema, 인증, 배포, secret 관련 변경이 포함되어 있지 않은가?",
                "위험도가 높은 변경은 사용자 승인 전까지 보류되는가?",
            ]
        )

    return checklist
