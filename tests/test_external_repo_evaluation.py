from pathlib import Path

from app.schemas.capsule_schema import RetrievalMode
from scripts.evaluate_external_repo import (
    DEFAULT_CASES_PATH,
    DEFAULT_REPO_PATH,
    build_markdown,
    evaluate_cases,
    load_cases,
    summarize,
)


def test_external_repo_eval_cases_load():
    cases = load_cases(DEFAULT_CASES_PATH)

    assert len(cases) == 10
    assert cases[0].name == "readme_portfolio"
    assert cases[0].expected_paths == ["README.md"]


def test_external_repo_eval_harness_passes_fixture():
    cases = load_cases(DEFAULT_CASES_PATH)

    results = evaluate_cases(DEFAULT_REPO_PATH, cases, retriever_mode=RetrievalMode.KEYWORD, top_k=8)
    summary = summarize(results)

    assert summary["cases"] == 10
    assert summary["fail"] == 0
    assert summary["target_included"] == 10
    assert summary["risk_floor_ok"] == 10
    assert summary["hit_at_3"] == 10
    assert any(result.name == "jwt_500_bug" and result.actual_risk == "HIGH" for result in results)


def test_external_repo_eval_markdown_is_honest_about_small_repo_tokens():
    cases = load_cases(DEFAULT_CASES_PATH)
    results = evaluate_cases(DEFAULT_REPO_PATH, cases, retriever_mode=RetrievalMode.KEYWORD, top_k=8)

    markdown = build_markdown(results, DEFAULT_REPO_PATH, DEFAULT_CASES_PATH, RetrievalMode.KEYWORD)

    assert "not a broad benchmark claim" in markdown
    assert "token reduction may be `0.0%`" in markdown
    assert "hit@3: 10/10" in markdown
