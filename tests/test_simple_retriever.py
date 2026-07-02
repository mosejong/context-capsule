from app.retrievers.simple_retriever import build_chunks, retrieve_relevant_chunks
from app.schemas.capsule_schema import FileKind, RepoFile


def test_explicit_path_query_filters_broad_path_token_noise():
    files = [
        RepoFile(
            path="app/analyzers/risk_analyzer.py",
            kind=FileKind.CODE,
            content="risk analyzer implementation",
            size=28,
        ),
        RepoFile(
            path="tests/test_risk_analyzer.py",
            kind=FileKind.TEST,
            content="risk analyzer test failed",
            size=26,
        ),
        RepoFile(
            path="app/auth.py",
            kind=FileKind.CODE,
            content="jwt login password token",
            size=24,
        ),
    ]

    chunks = retrieve_relevant_chunks(
        files,
        "Traceback in app/analyzers/risk_analyzer.py and tests/test_risk_analyzer.py failed",
        top_k=8,
    )
    paths = {chunk.path for chunk in chunks}

    assert "app/analyzers/risk_analyzer.py" in paths
    assert "tests/test_risk_analyzer.py" in paths
    assert "app/auth.py" not in paths


def test_snake_case_path_matches_space_separated_query():
    files = [
        RepoFile(
            path="app/generators/capsule_generator.py",
            kind=FileKind.CODE,
            content="generate capsule markdown",
            size=25,
        )
    ]

    chunks = retrieve_relevant_chunks(files, "capsule generator 작업을 정리해줘", top_k=8)

    assert [chunk.path for chunk in chunks] == ["app/generators/capsule_generator.py"]


def test_readme_task_mandatory_includes_readme_first():
    files = [
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Demo\nPortfolio guide", size=22),
        RepoFile(path="app/main.py", kind=FileKind.CODE, content="streamlit app readme portfolio docs update", size=42),
        RepoFile(path="tests/test_main.py", kind=FileKind.TEST, content="readme portfolio test update", size=28),
    ]

    chunks = retrieve_relevant_chunks(files, "README를 포트폴리오용으로 다듬어줘", top_k=3)

    assert chunks[0].path == "README.md"
    assert "README.md" in [chunk.path for chunk in chunks]


def test_root_readme_mention_does_not_make_nested_readmes_mandatory():
    files = [
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Demo\nPortfolio guide", size=22),
        RepoFile(path="frontend-rn/README.md", kind=FileKind.DOC, content="React Native app notes", size=22),
        RepoFile(path="ai/liveportrait/README.md", kind=FileKind.DOC, content="LivePortrait notes", size=18),
    ]

    chunks = retrieve_relevant_chunks(files, "README.md documentation portfolio", top_k=3)
    paths = [chunk.path for chunk in chunks]

    assert paths[0] == "README.md"
    assert all((chunk.score or 0) < 1000 for chunk in chunks[1:])


def test_explicit_docs_path_is_mandatory_first():
    files = [
        RepoFile(path="README.md", kind=FileKind.DOC, content="local app guide", size=15),
        RepoFile(path="docs/local_app.md", kind=FileKind.DOC, content="install run dashboard", size=21),
        RepoFile(path="app/main.py", kind=FileKind.CODE, content="local app dashboard", size=19),
    ]

    chunks = retrieve_relevant_chunks(files, "docs/local_app.md를 사용자 친화적으로 정리해줘", top_k=3)

    assert chunks[0].path == "docs/local_app.md"


def test_stem_mention_mandatory_includes_target_file_first():
    files = [
        RepoFile(path="docs/research/llm_tech_scan.md", kind=FileKind.DOC, content="vector embedding retriever search", size=33),
        RepoFile(path="tests/test_simple_retriever.py", kind=FileKind.TEST, content="simple retriever vector test", size=28),
        RepoFile(path="app/retrievers/simple_retriever.py", kind=FileKind.CODE, content="def retrieve_relevant_chunks(): pass", size=36),
    ]

    chunks = retrieve_relevant_chunks(files, "simple_retriever에 벡터 검색을 추가", top_k=3)

    assert chunks[0].path == "app/retrievers/simple_retriever.py"


def test_cli_task_prefers_explicit_cli_and_related_adapter():
    files = [
        RepoFile(path="README.md", kind=FileKind.DOC, content="create issue command guide", size=26),
        RepoFile(path="app/cli.py", kind=FileKind.CODE, content="create issue command parser", size=27),
        RepoFile(path="app/adapters/github_issue_adapter.py", kind=FileKind.CODE, content="create issue dry run apply", size=27),
    ]

    chunks = retrieve_relevant_chunks(files, "app/cli.py의 create-issue 명령 오류를 고쳐줘", top_k=3)
    paths = [chunk.path for chunk in chunks]

    assert paths[0] == "app/cli.py"
    assert "app/adapters/github_issue_adapter.py" in paths


def test_retrieval_deduplicates_same_file_by_default():
    content = "\n".join(f"def section_{index}(): return 'simple retriever'" for index in range(170))
    files = [RepoFile(path="app/retrievers/simple_retriever.py", kind=FileKind.CODE, content=content, size=len(content))]

    chunks = retrieve_relevant_chunks(files, "simple_retriever 수정", top_k=8)

    assert [chunk.path for chunk in chunks] == ["app/retrievers/simple_retriever.py"]


def test_metric_query_prefers_qa_numbers_over_portfolio_readme():
    files = [
        RepoFile(
            path="README_portfolio.md",
            kind=FileKind.DOC,
            content="ML model accuracy 98.6 portfolio marketing summary",
            size=51,
        ),
        RepoFile(
            path="check.md",
            kind=FileKind.DOC,
            content="ML model accuracy check note",
            size=28,
        ),
        RepoFile(
            path="docs/numbers_reference.md",
            kind=FileKind.DOC,
            content="ML model accuracy 98.08 holdout qa defense validated metric",
            size=62,
        ),
    ]

    chunks = retrieve_relevant_chunks(files, "ML 모델 정확도가 몇 %야?", top_k=3)

    assert chunks[0].path == "docs/numbers_reference.md"


def test_path_scope_includes_frontend_rn_without_frontend_prefix_leakage():
    files = [
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Root\nPortfolio README", size=24),
        RepoFile(path="frontend-rn/README.md", kind=FileKind.DOC, content="React Native app portfolio docs", size=31),
        RepoFile(path="frontend/README.md", kind=FileKind.DOC, content="Web frontend docs", size=18),
        RepoFile(path="ai/liveportrait/README.md", kind=FileKind.DOC, content="LivePortrait experiment docs", size=28),
    ]

    chunks = retrieve_relevant_chunks(
        files,
        "frontend-rn 폴더에서 md파일을 찾아서 포트폴리오용으로 다듬어줘",
        top_k=5,
        include_extensions=[".md"],
        include_path_hints=["frontend-rn/"],
        exclude_path_hints=["frontend/"],
    )
    paths = [chunk.path for chunk in chunks]

    assert paths == ["frontend-rn/README.md"]


def test_markdown_chunking_respects_heading_boundaries():
    content = "\n".join(
        [
            "# Project",
            "root overview",
            "## Install",
            "run setup",
            "## API",
            "auth endpoint",
            "login endpoint",
        ]
    )
    files = [RepoFile(path="README.md", kind=FileKind.DOC, content=content, size=len(content))]

    chunks = build_chunks(files, max_lines=80)

    assert [chunk.start_line for chunk in chunks] == [1, 3, 5]
    assert [chunk.end_line for chunk in chunks] == [2, 4, 7]
    assert chunks[1].text.startswith("## Install")


def test_oversized_markdown_section_still_splits_by_line_window():
    section_lines = ["# Long Section", *[f"line {index}" for index in range(1, 7)]]
    content = "\n".join(section_lines)
    files = [RepoFile(path="README.md", kind=FileKind.DOC, content=content, size=len(content))]

    chunks = build_chunks(files, max_lines=3)

    assert [(chunk.start_line, chunk.end_line) for chunk in chunks] == [(1, 3), (4, 6), (7, 7)]


def test_generic_docs_request_deprioritizes_release_notes_noise():
    files = [
        RepoFile(path="docs/README.md", kind=FileKind.DOC, content="# Docs\n문서 설명 정리", size=18),
        RepoFile(path="docs/releases/v0.2.8.md", kind=FileKind.DOC, content="# Release\n문서 설명 정리 release", size=25),
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Project\n문서 설명", size=16),
    ]

    chunks = retrieve_relevant_chunks(files, "문서 설명 정리하자", top_k=3)
    paths = [chunk.path for chunk in chunks]

    assert paths[0] in {"docs/README.md", "README.md"}
    assert "docs/releases/v0.2.8.md" not in paths[:2]


def test_release_request_keeps_release_notes_available():
    files = [
        RepoFile(path="docs/README.md", kind=FileKind.DOC, content="# Docs\n문서 설명 정리", size=18),
        RepoFile(path="docs/releases/v0.2.8.md", kind=FileKind.DOC, content="# Release\nrelease notes patch", size=25),
        RepoFile(path="README.md", kind=FileKind.DOC, content="# Project\n문서 설명", size=16),
    ]

    chunks = retrieve_relevant_chunks(files, "release notes 정리", top_k=3)
    paths = [chunk.path for chunk in chunks]

    assert paths[0] == "docs/releases/v0.2.8.md"
