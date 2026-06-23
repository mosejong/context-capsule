from app.retrievers.simple_retriever import retrieve_relevant_chunks
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
