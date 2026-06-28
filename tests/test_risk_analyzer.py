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


def test_korean_fix_colloquial_marks_jwt_as_high_change_risk():
    chunks = [
        RepoChunk(path="src/services/auth_service.py", kind=FileKind.CODE, text="jwt decode_token", start_line=1, end_line=1)
    ]

    findings = analyze_risk("만료 JWT 토큰 시 500 에러 나는 auth_service decode_token 고쳐줘", chunks, forbidden_rules=[])

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


def test_document_metric_conflict_is_flagged():
    chunks = [
        RepoChunk(
            path="README.md",
            kind=FileKind.DOC,
            text="Portfolio metric: accuracy 98.6%",
            start_line=1,
            end_line=1,
        ),
        RepoChunk(
            path="docs/qa_defense.md",
            kind=FileKind.DOC,
            text="QA defense source: accuracy 98.08%",
            start_line=1,
            end_line=1,
        ),
    ]

    findings = analyze_risk("README 포트폴리오 수치 정리", chunks, forbidden_rules=[])

    assert any(
        finding.kind == RiskKind.MENTION
        and finding.level == RiskLevel.MEDIUM
        and "수치 값" in finding.reason
        and "98.6%" in (finding.evidence or "")
        and "98.08%" in (finding.evidence or "")
        for finding in findings
    )


def test_matching_document_metrics_are_not_flagged_as_conflict():
    chunks = [
        RepoChunk(path="README.md", kind=FileKind.DOC, text="accuracy 98.08%", start_line=1, end_line=1),
        RepoChunk(path="docs/qa_defense.md", kind=FileKind.DOC, text="accuracy 98.08%", start_line=1, end_line=1),
    ]

    findings = analyze_risk("README 포트폴리오 수치 정리", chunks, forbidden_rules=[])

    assert not any("수치 값" in finding.reason for finding in findings)


def test_token_reduction_percent_is_not_compared_with_accuracy_metric():
    chunks = [
        RepoChunk(
            path="docs/experiment.md",
            kind=FileKind.DOC,
            text="토큰 감소율은 98%입니다. 모델 정확도는 98.08%입니다.",
            start_line=1,
            end_line=1,
        ),
        RepoChunk(
            path="docs/qa_defense.md",
            kind=FileKind.DOC,
            text="QA defense source accuracy 98.08%",
            start_line=1,
            end_line=1,
        ),
    ]

    findings = analyze_risk("README 포트폴리오 수치 정리", chunks, forbidden_rules=[])

    assert not any("수치 값" in finding.reason and "98%" in (finding.evidence or "") for finding in findings)
