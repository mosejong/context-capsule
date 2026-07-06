# RAGAS-Style Evaluation

Generated at: 2026-07-06 10:15:39

Repository fixture: `tests\fixtures\external_repos\ecommerce`
Case file: `tests\fixtures\external_repo_eval_cases.json`
Retriever mode: `keyword`
Judge: `ollama:llama3.1:latest`
Embedding: `ollama:bge-m3`
Case limit: `2`

This report adds RAGAS-style quality signals on top of the existing hit@k retrieval harness. It is run-scoped and should not be treated as a broad benchmark claim.

## Summary

- Cases: 2
- Faithfulness average: 0.65
- Answer Relevancy average: not measured
- Context Recall: not measured

## Why Context Recall Is Not Measured

`tests/fixtures/external_repo_eval_cases.json` currently contains `expected_paths`, not reference answers or ground-truth answer text. Context Recall would be misleading without ground truth, so it is explicitly marked as `not measured`.

## Judge Self-Check

| Check | Metric | Expected | Score | Verdict | Explanation |
| --- | --- | --- | ---: | --- | --- |
| grounded_claim_high | faithfulness | high | 1.00 | PASS | The answer accurately reflects the context, which states that Context Capsule default retrieval is keyword/path-aware retrieval. |
| unsupported_claim_low | faithfulness | low | 0.00 | PASS | Context states that Capsule default retrieval is keyword/path-aware, not deep learning embeddings by default. |
| irrelevant_answer_low | answer_relevancy | low | - | PASS | Embedding failed for ollama:bge-m3: Ollama embedding model unavailable: bge-m3: HTTP Error 404: Not Found |

The self-check is required because a judge that always gives high scores is broken. At least one unsupported faithfulness case and one irrelevant answer case must receive a low score, or be explicitly marked as not measured when embeddings are unavailable.

## Results

| Case | Top Paths | Faithfulness | Answer Relevancy | Context Recall | Notes |
| --- | --- | ---: | ---: | --- | --- |
| readme_portfolio | README.md | 0.80 | not measured | not measured | 문맥에서 이 주장은 명시적이지 않습니다. README.md의 첫 번째 줄에 'ShopFlow Dummy Ecommerce API'라는 문구가 있지만, AI가 사용자의 승인 없이 코드를 직접 수정하지 않는다는 보장된 정보는 없습니다. |
| payment_fallback | src/services/payment_service.py, src/api/routes/orders.py, src/services/notification_service.py, src/services/auth_service.py, src/config/settings.py | 0.50 | not measured | not measured | 결제 실패 시 fallback 구조를 추가하는 것은 가능하지만, 관련된 코드와 로직을 분석하고 구체적인 구현을 제안해야 합니다. |

## Metric Definitions

- Faithfulness: asks a local Ollama judge whether answer claims are supported by retrieved context.
- Answer Relevancy: asks the judge to generate a reverse question from the answer, then compares it with the original task using a local embedding model.
- Context Recall: not measured until reference answers are added to the case file.

## How To Regenerate

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_ragas.py
```

Recommended local setup for Answer Relevancy:

```powershell
ollama pull bge-m3
```
