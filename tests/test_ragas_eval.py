from __future__ import annotations

from pathlib import Path

from app.schemas.capsule_schema import RetrievalMode
from scripts.evaluate_external_repo import DEFAULT_CASES_PATH, DEFAULT_REPO_PATH, ExternalRepoCase, load_cases
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
    split_claims,
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
    assert by_name["context_recall_high"].passed is True
    assert by_name["context_recall_high"].score is not None
    assert by_name["context_recall_high"].score >= 0.65
    assert by_name["context_recall_missing_claim_low"].passed is True
    assert by_name["context_recall_missing_claim_low"].score is not None
    assert by_name["context_recall_missing_claim_low"].score <= 0.75


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


def test_ragas_eval_case_measures_context_recall_when_ground_truth_exists():
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
    assert result.context_recall.score is not None
    assert result.context_recall.status == "measured"
    assert 0.0 <= result.context_recall.score <= 1.0
    assert result.top_paths


def test_ragas_eval_case_keeps_context_recall_unmeasured_without_ground_truth():
    case = ExternalRepoCase(
        name="missing_ground_truth_guard",
        task="README를 확인해줘",
        expected_paths=["README.md"],
        ground_truth_answer=None,
    )
    result = evaluate_case(
        DEFAULT_REPO_PATH,
        case,
        KeywordSelfCheckJudge(),
        KeywordEmbeddingClient(),
        RetrievalMode.KEYWORD,
        top_k=3,
    )

    assert result.context_recall.score is None
    assert result.context_recall.status == "not measured"
    assert "ground_truth_answer" in result.context_recall.explanation


def test_ragas_markdown_reports_context_recall_coverage():
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

    assert "Context Recall average:" in markdown
    assert "1/1 measured" in markdown
    assert "Context Recall Coverage" in markdown
    assert "ground_truth_answer" in markdown
    assert "Faithfulness" in markdown
    assert "Answer Relevancy" in markdown


def test_context_recall_claim_splitter_uses_ground_truth_sentences():
    claims = split_claims("A is true. B is true.\n- C is true")

    assert claims == ["A is true", "B is true", "C is true"]


class BrokenHighJudge(KeywordSelfCheckJudge):
    name = "broken_high"

    def score_faithfulness(self, *, context: str, answer: str) -> MetricScore:
        return MetricScore(score=0.99, status="measured", explanation="always high", evidence=[])


def test_self_check_fails_when_faithfulness_judge_always_scores_high():
    checks = run_self_check(BrokenHighJudge(), KeywordEmbeddingClient())

    unsupported = next(check for check in checks if check.name == "unsupported_claim_low")
    assert unsupported.passed is False


class BrokenRecallJudge(KeywordSelfCheckJudge):
    name = "broken_recall"

    def score_context_recall(self, *, ground_truth: str, context: str) -> MetricScore:
        return MetricScore(score=0.99, status="measured", explanation="always high", evidence=[])


def test_self_check_fails_when_context_recall_judge_always_scores_high():
    checks = run_self_check(BrokenRecallJudge(), KeywordEmbeddingClient())

    recall = next(check for check in checks if check.name == "context_recall_missing_claim_low")
    assert recall.passed is False
