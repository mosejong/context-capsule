from app.analyzers.request_understanding import understand_request
from app.schemas.capsule_schema import FileKind, RepoFile


def sample_files():
    return [
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Demo", size=6),
        RepoFile(path="docs/local_app.md", kind=FileKind.DOC, content="local launcher docs", size=19),
        RepoFile(path="app/retrievers/simple_retriever.py", kind=FileKind.CODE, content="retriever", size=9),
        RepoFile(path="app/adapters/github_issue_adapter.py", kind=FileKind.CODE, content="github issue", size=12),
        RepoFile(path="app/cli.py", kind=FileKind.CODE, content="create issue cli", size=16),
        RepoFile(path="run_context_capsule.bat", kind=FileKind.CONFIG, content="streamlit run", size=12),
        RepoFile(path="scripts/run_dashboard.ps1", kind=FileKind.CONFIG, content="streamlit run", size=12),
        RepoFile(path="app/analyzers/token_analyzer.py", kind=FileKind.CODE, content="token budget", size=12),
        RepoFile(path="scripts/generate_performance_report.py", kind=FileKind.CODE, content="performance", size=11),
        RepoFile(path="docs/reports/performance_comparison.md", kind=FileKind.DOC, content="token report", size=12),
        RepoFile(path="app/generators/output_writer.py", kind=FileKind.CODE, content="write output", size=12),
    ]


def test_readme_colloquial_request_maps_to_readme():
    understanding = understand_request("리드미 손보자", sample_files())

    assert understanding.intent == "documentation_edit"
    assert understanding.confidence_label == "high"
    assert understanding.file_hints == ["README.md"]
    assert "README.md" in understanding.search_query


def test_token_metric_request_maps_to_token_analyzer_and_report():
    understanding = understand_request("토큰 계산 뻥튀기 같은데?", sample_files())

    assert understanding.intent == "metric_validation"
    assert "app/analyzers/token_analyzer.py" in understanding.file_hints
    assert "docs/reports/performance_comparison.md" in understanding.file_hints
    assert understanding.needs_clarification is False


def test_negated_auth_becomes_protected_not_target():
    understanding = understand_request("auth는 건드리지 말고 문서만 바꾸자", sample_files())

    assert "auth" in understanding.protected_hints
    assert "README.md" in understanding.file_hints
    assert "auth" not in understanding.search_query.lower()


def test_ambiguous_request_asks_one_question():
    understanding = understand_request("이거 왜그래?", sample_files())

    assert understanding.needs_clarification is True
    assert understanding.confidence_label == "low"
    assert understanding.clarification_question == "대상 파일, 기능명, 또는 오류 로그 중 하나를 알려주세요."
