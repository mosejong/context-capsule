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
    assert "portfolio" not in understanding.search_query.lower()


def test_readme_portfolio_request_keeps_portfolio_context():
    understanding = understand_request("README 포폴용으로 다듬자", sample_files())

    assert understanding.intent == "documentation_edit"
    assert understanding.file_hints == ["README.md"]
    assert "portfolio" in understanding.search_query.lower()


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


def test_generic_docs_request_does_not_expand_entire_docs_tree_as_file_hints():
    files = [
        *sample_files(),
        RepoFile(path="docs/README.md", kind=FileKind.DOC, content="Docs index", size=10),
        RepoFile(path="docs/releases/v0.2.8.md", kind=FileKind.DOC, content="Release notes", size=13),
        RepoFile(path="docs/archive/vision.md", kind=FileKind.DOC, content="Old vision", size=10),
    ]

    understanding = understand_request("auth는 건드리지 말고 문서만 바꾸자", files)

    assert "README.md" in understanding.file_hints
    assert "docs/README.md" in understanding.file_hints
    assert "docs/releases/v0.2.8.md" not in understanding.file_hints
    assert "docs/archive/vision.md" not in understanding.file_hints
    assert "docs/releases/v0.2.8.md" not in understanding.search_query
    assert "docs/archive/vision.md" not in understanding.search_query


def test_md_file_scope_is_detected_as_hard_constraint():
    understanding = understand_request("전체 폴더의 md파일들을 확인하고 기획서.md를 하나 만들어줘", sample_files())

    assert understanding.include_extensions == [".md"]
    assert understanding.exclude_extensions == []
    assert "include_extension:.md" in understanding.search_query


def test_json_exclusion_scope_is_detected():
    understanding = understand_request("전체 폴더를 확인하되 json은 보지 말고 기획서.md를 만들어줘", sample_files())

    assert understanding.include_extensions == []
    assert understanding.exclude_extensions == [".json"]
    assert "exclude_extension:.json" in understanding.search_query


def test_exact_path_scope_distinguishes_frontend_rn_from_frontend():
    files = [
        *sample_files(),
        RepoFile(path="frontend-rn/README.md", kind=FileKind.DOC, content="React Native readme", size=18),
        RepoFile(path="frontend/README.md", kind=FileKind.DOC, content="Web frontend readme", size=19),
    ]

    understanding = understand_request(
        "frontend-rn 폴더만 봐. 다시말해서 frontend는 보지마. frontend-rn 폴더에서 md파일을 찾아줘",
        files,
    )

    assert understanding.include_path_hints == ["frontend-rn/"]
    assert understanding.exclude_path_hints == ["frontend/"]
    assert understanding.include_extensions == [".md"]
    assert "include_path:frontend-rn/" in understanding.search_query
    assert "exclude_path:frontend/" in understanding.search_query


def test_ambiguous_request_asks_one_question():
    understanding = understand_request("이거 왜그래?", sample_files())

    assert understanding.needs_clarification is True
    assert understanding.confidence_label == "low"
    assert understanding.clarification_question == "대상 파일, 기능명, 또는 오류 로그 중 하나를 알려주세요."
