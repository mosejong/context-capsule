from app.analyzers.token_analyzer import analyze_token_budget, calculate_reduction, estimate_tokens
from app.schemas.capsule_schema import FileKind, RepoChunk, RepoFile


def test_estimate_tokens_returns_positive_count():
    assert estimate_tokens("로그인 API response schema") > 0


def test_calculate_reduction():
    assert calculate_reduction(1000, 250) == 75.0
    assert calculate_reduction(0, 250) == 0.0
    assert calculate_reduction(100, 250) == 0.0


def test_analyze_token_budget_compares_raw_and_prompt():
    files = [
        RepoFile(
            path="README.md",
            kind=FileKind.DOC,
            content="로그인 API 설명\n" * 200,
            size=2000,
        )
    ]
    chunks = [
        RepoChunk(
            path="README.md",
            kind=FileKind.DOC,
            text="로그인 API 설명",
            start_line=1,
            end_line=1,
        )
    ]

    budget = analyze_token_budget(files, chunks, "로그인 API만 확인하세요.")

    assert budget.raw_context_tokens > budget.retrieved_context_tokens
    assert budget.raw_context_tokens > budget.handoff_prompt_tokens
    assert budget.estimated_reduction_percent > 0
    assert budget.method == "approx_local_v1"
