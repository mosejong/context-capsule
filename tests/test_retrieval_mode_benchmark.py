from app.schemas.capsule_schema import RetrievalMode
from scripts.benchmark_retrieval_modes import build_markdown, evaluate_modes, summarize
from scripts.evaluate_external_repo import DEFAULT_CASES_PATH, DEFAULT_REPO_PATH, load_cases


def test_retrieval_mode_benchmark_runs_keyword_and_hybrid():
    cases = load_cases(DEFAULT_CASES_PATH)[:3]

    results, providers = evaluate_modes(
        DEFAULT_REPO_PATH,
        cases,
        [RetrievalMode.KEYWORD, RetrievalMode.HYBRID],
        top_k=8,
    )
    summary = summarize(results)

    assert providers["keyword"] == "not_required"
    assert providers["hybrid"] == "not_required"
    assert summary["keyword"]["cases"] == 3
    assert summary["hybrid"]["cases"] == 3
    assert summary["keyword"]["fail"] == 0
    assert summary["hybrid"]["fail"] == 0


def test_retrieval_mode_benchmark_prepares_indexed_provider():
    cases = load_cases(DEFAULT_CASES_PATH)[:2]

    results, providers = evaluate_modes(
        DEFAULT_REPO_PATH,
        cases,
        [RetrievalMode.INDEXED],
        top_k=8,
    )
    summary = summarize(results)

    assert providers["indexed"]
    assert summary["indexed"]["cases"] == 2
    assert summary["indexed"]["fail"] == 0
    assert {result.used_mode for result in results} == {"indexed"}


def test_retrieval_mode_benchmark_markdown_is_honest_and_reproducible():
    cases = load_cases(DEFAULT_CASES_PATH)[:1]
    results, providers = evaluate_modes(
        DEFAULT_REPO_PATH,
        cases,
        [RetrievalMode.KEYWORD],
        top_k=8,
    )

    markdown = build_markdown(results, providers, DEFAULT_REPO_PATH, DEFAULT_CASES_PATH)

    assert "not a broad benchmark claim" in markdown
    assert "benchmark_retrieval_modes.py --modes keyword hybrid indexed" in markdown
    assert "CONTEXT_CAPSULE_EMBEDDING_MODEL" in markdown
