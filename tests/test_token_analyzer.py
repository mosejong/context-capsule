from app.analyzers.token_analyzer import (
    ApproxLocalTokenUsageProvider,
    ExternalTokenAnalyzerProvider,
    TokenUsageInput,
    analyze_token_budget,
    build_token_usage_input,
    calculate_reduction,
    estimate_tokens,
)
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
    assert budget.baseline_context_scope == "retrieved_file_contents"


def test_token_baseline_uses_retrieved_files_not_whole_repo():
    files = [
        RepoFile(
            path="app/auth.py",
            kind=FileKind.CODE,
            content="def login():\n    return token\n",
            size=28,
        ),
        RepoFile(
            path="docs/large_unrelated.md",
            kind=FileKind.DOC,
            content=("unrelated documentation\n" * 500),
            size=12000,
        ),
    ]
    chunks = [
        RepoChunk(
            path="app/auth.py",
            kind=FileKind.CODE,
            text="def login():\n    return token",
            start_line=1,
            end_line=2,
        )
    ]

    usage_input = build_token_usage_input(files, chunks, "Fix login using app/auth.py only.")

    assert usage_input.baseline_context_scope == "retrieved_file_contents"
    assert "large_unrelated" not in usage_input.raw_context
    assert estimate_tokens(usage_input.raw_context) < estimate_tokens("\n\n".join(file.content for file in files))


def test_approx_provider_implements_token_usage_provider():
    provider = ApproxLocalTokenUsageProvider()

    budget = provider.analyze(
        TokenUsageInput(
            raw_context="full repository context " * 50,
            retrieved_context="auth router context",
            handoff_prompt="Fix login issue using only auth router context.",
        )
    )

    assert budget.method == "approx_local_v1"
    assert budget.verification_status == "Estimated only"
    assert budget.actual_provider_usage == "Not measured yet"
    assert budget.estimated_reduction_percent > 0


def test_external_token_analyzer_provider_is_placeholder():
    provider = ExternalTokenAnalyzerProvider()

    try:
        provider.analyze(TokenUsageInput(raw_context="", retrieved_context="", handoff_prompt=""))
    except NotImplementedError as exc:
        assert "upstream open-source API and license" in str(exc)
    else:
        raise AssertionError("Expected external provider placeholder to raise")
