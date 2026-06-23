from app.analyzers.risk_analyzer import analyze_risk, build_approval_checklist
from app.schemas.capsule_schema import FileKind, RepoChunk, RiskKind, RiskLevel


def test_detects_auth_risk_for_login_change():
    chunks = [
        RepoChunk(path="backend/auth/router.py", kind=FileKind.CODE, text="jwt token login password", start_line=1, end_line=1),
        RepoChunk(path=".env.example", kind=FileKind.CONFIG, text="API_KEY=", start_line=1, end_line=1),
    ]

    findings = analyze_risk("로그인 API 수정", chunks, forbidden_rules=[])
    levels = {finding.level for finding in findings}

    assert RiskLevel.HIGH in levels


def test_approval_checklist_expands_for_high_risk():
    chunks = [RepoChunk(path="models/user.py", kind=FileKind.CODE, text="database schema table", start_line=1, end_line=1)]
    findings = analyze_risk("DB schema를 수정한다", chunks, forbidden_rules=[])
    checklist = build_approval_checklist(findings)

    assert any("DB schema" in item for item in checklist)


def test_token_budget_does_not_count_as_secret_token():
    chunks = [
        RepoChunk(
            path="app/generators/capsule_generator.py",
            kind=FileKind.CODE,
            text="token budget estimate reduction",
            start_line=1,
            end_line=1,
        )
    ]

    findings = analyze_risk("토큰 분석 결과를 보여준다", chunks, forbidden_rules=[])

    assert all(finding.level != RiskLevel.BLOCKED for finding in findings)


def test_readme_security_mentions_are_not_blocking_change_risks():
    chunks = [
        RepoChunk(
            path="README.md",
            kind=FileKind.DOC,
            text="This document mentions secret, auth, database, deploy and API risk areas.",
            start_line=1,
            end_line=1,
        )
    ]

    findings = analyze_risk("README를 포트폴리오용으로 정리해줘", chunks, forbidden_rules=[])

    assert findings
    assert all(finding.kind == RiskKind.MENTION for finding in findings)
    assert all(finding.level not in {RiskLevel.HIGH, RiskLevel.BLOCKED} for finding in findings)


def test_jwt_login_change_is_high_change_risk():
    chunks = [
        RepoChunk(path="backend/auth/router.py", kind=FileKind.CODE, text="jwt login password", start_line=1, end_line=1)
    ]

    findings = analyze_risk("JWT 로그인 로직을 수정해줘", chunks, forbidden_rules=[])

    assert any(finding.kind == RiskKind.CHANGE and finding.level == RiskLevel.HIGH for finding in findings)


def test_env_secret_change_is_blocked_change_risk():
    chunks = [RepoChunk(path=".env.example", kind=FileKind.CONFIG, text="API_KEY=", start_line=1, end_line=1)]

    findings = analyze_risk(".env secret 값을 수정해줘", chunks, forbidden_rules=[])

    assert any(finding.kind == RiskKind.CHANGE and finding.level == RiskLevel.BLOCKED for finding in findings)


def test_negated_auth_instruction_is_not_high_change_risk():
    chunks = [
        RepoChunk(path="README.md", kind=FileKind.DOC, text="Do not touch auth logic.", start_line=1, end_line=1)
    ]

    findings = analyze_risk("README를 수정하되 auth 로직은 건드리지 말아줘", chunks, forbidden_rules=[])

    assert not any(finding.kind == RiskKind.CHANGE and finding.level == RiskLevel.HIGH for finding in findings)


def test_docs_only_task_ignores_unrelated_code_risk_noise():
    chunks = [
        RepoChunk(path="README.md", kind=FileKind.DOC, text="Portfolio documentation", start_line=1, end_line=1),
        RepoChunk(path="app/auth.py", kind=FileKind.CODE, text="jwt login password token schema", start_line=1, end_line=1),
    ]

    findings = analyze_risk("README를 포트폴리오용으로 정리해줘", chunks, forbidden_rules=[])

    assert not any(finding.kind == RiskKind.CHANGE and finding.level in {RiskLevel.HIGH, RiskLevel.BLOCKED} for finding in findings)
