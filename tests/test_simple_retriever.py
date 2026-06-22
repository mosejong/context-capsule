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
