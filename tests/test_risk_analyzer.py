from app.analyzers.risk_analyzer import analyze_risk, build_approval_checklist
from app.schemas.capsule_schema import FileKind, RepoChunk, RiskLevel


def test_detects_auth_and_env_risk():
    chunks = [
        RepoChunk(path="backend/auth/router.py", kind=FileKind.CODE, text="jwt token login password", start_line=1, end_line=1),
        RepoChunk(path=".env.example", kind=FileKind.CONFIG, text="API_KEY=", start_line=1, end_line=1),
    ]

    findings = analyze_risk("로그인 API 수정", chunks, forbidden_rules=[])
    levels = {finding.level for finding in findings}

    assert RiskLevel.HIGH in levels
    assert RiskLevel.BLOCKED in levels


def test_approval_checklist_expands_for_high_risk():
    chunks = [RepoChunk(path="models/user.py", kind=FileKind.CODE, text="database schema table", start_line=1, end_line=1)]
    findings = analyze_risk("DB schema를 수정한다", chunks, forbidden_rules=[])
    checklist = build_approval_checklist(findings)

    assert any("DB schema" in item for item in checklist)
