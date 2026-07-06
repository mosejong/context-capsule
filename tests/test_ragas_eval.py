from __future__ import annotations

from pathlib import Path

from app.schemas.capsule_schema import RetrievalMode
from scripts.evaluate_external_repo import DEFAULT_CASES_PATH, DEFAULT_REPO_PATH, load_cases
from scripts.evaluate_ragas import (
    KeywordEmbeddingClient,
    KeywordSelfCheckJudge,
    MetricScore,
    build_markdown,
    evaluate_case,
    fallback_question_from_text,
    parse_json_object,
    run_self_check,
    score_answer_relevancy,
    select_cases,
)


def test_ragas_self_check_requires_low_scores_for_bad_cases():
    checks = run_self_check(KeywordSelfCheckJudge(), KeywordEmbeddingClient())

    by_name = {check.name: check for check in checks}
    assert by_name["grounded_claim_high"].passed is True
    assert by_name["unsupported_claim_low"].passed is True
    assert by_name["unsupported_claim_low"].score is not None
    assert by_name["unsupported_claim_low"].score <= 0.5
    assert by_name["irrelevant_answer_low"].passed is True
    assert by_name["irrelevant_answer_low"].score is not None
    assert by_name["irrelevant_answer_low"].score <= 0.5


def test_select_cases_limits_smoke_run_size():
    cases = load_cases(DEFAULT_CASES_PATH)

    assert len(select_cases(cases, None)) == len(cases)
    assert len(select_cases(cases, 0)) == len(cases)
    assert [case.name for case in select_cases(cases, 2)] == [cases[0].name, cases[1].name]


def test_answer_relevancy_is_not_measured_without_embedding_client():
    score = score_answer_relevancy(
        "What is hybrid retrieval?",
        "Hybrid retrieval combines keyword and vector signals.",
        KeywordSelfCheckJudge(),
        None,
    )

    assert score.score is None
    assert score.status == "not measured"
    assert "Embedding client unavailable" in score.explanation


def test_parse_json_object_handles_wrapped_judge_output():
    payload = parse_json_object('Sure.\n{"score": 0.25, "unsupported_claims": ["x"], "explanation": "bad"}\nDone.')

    assert payload["score"] == 0.25
    assert payload["unsupported_claims"] == ["x"]


def test_fallback_question_from_non_json_ollama_text():
    question = fallback_question_from_text(
        'Judge did not return JSON: Here is the question:\n"What is hybrid retrieval?"'
    )

    assert question == "What is hybrid retrieval?"


def test_ragas_eval_case_marks_context_recall_not_measured():
    case = load_cases(DEFAULT_CASES_PATH)[0]
    result = evaluate_case(
        DEFAULT_REPO_PATH,
        case,
        KeywordSelfCheckJudge(),
        KeywordEmbeddingClient(),
        RetrievalMode.KEYWORD,
        top_k=3,
    )

    assert result.answer_source == "capsule.sections.ai_handoff_prompt"
    assert result.context_recall.score is None
    assert result.context_recall.status == "not measured"
    assert "expected_paths" in result.context_recall.explanation
    assert result.top_paths


def test_ragas_markdown_is_honest_about_context_recall():
    result = evaluate_case(
        DEFAULT_REPO_PATH,
        load_cases(DEFAULT_CASES_PATH)[0],
        KeywordSelfCheckJudge(),
        KeywordEmbeddingClient(),
        RetrievalMode.KEYWORD,
        top_k=3,
    )
    markdown = build_markdown(
        [result],
        run_self_check(KeywordSelfCheckJudge(), KeywordEmbeddingClient()),
        repo_path=Path("repo"),
        cases_path=Path("cases.json"),
        retriever_mode=RetrievalMode.KEYWORD,
        judge_name="keyword_self_check",
        embedding_name="keyword_embedding_test",
    )

    assert "Context Recall: not measured" in markdown
    assert "ground-truth answer text" in markdown
    assert "Faithfulness" in markdown
    assert "Answer Relevancy" in markdown


class BrokenHighJudge(KeywordSelfCheckJudge):
    name = "broken_high"

    def score_faithfulness(self, *, context: str, answer: str) -> MetricScore:
        return MetricScore(score=0.99, status="measured", explanation="always high", evidence=[])


def test_self_check_fails_when_faithfulness_judge_always_scores_high():
    checks = run_self_check(BrokenHighJudge(), KeywordEmbeddingClient())

    unsupported = next(check for check in checks if check.name == "unsupported_claim_low")
    assert unsupported.passed is False
