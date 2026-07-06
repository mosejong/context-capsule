# RAGAS-Style Evaluation

Generated at: 2026-07-06 14:30:54

Repository fixture: `tests\fixtures\external_repos\ecommerce`
Case file: `tests\fixtures\external_repo_eval_cases.json`
Retriever mode: `keyword`
Judge: `keyword_self_check`
Embedding: `keyword_embedding_test`
Case limit: `none`

This report adds RAGAS-style quality signals on top of the existing hit@k retrieval harness. It is run-scoped and should not be treated as a broad benchmark claim.

## Summary

- Cases: 10
- Faithfulness average: 0.50
- Answer Relevancy average: 0.00
- Context Recall average: 0.50 (3/10 measured)

## Context Recall Coverage

Context Recall is measured only for cases that include `ground_truth_answer` in `tests/fixtures/external_repo_eval_cases.json`. Cases without that field remain explicitly marked as `not measured` so the report does not fabricate recall scores before reference answers are authored.

## Judge Self-Check

| Check | Metric | Expected | Score | Verdict | Explanation |
| --- | --- | --- | ---: | --- | --- |
| grounded_claim_high | faithfulness | high | 0.95 | PASS | claim appears in context |
| unsupported_claim_low | faithfulness | low | 0.10 | PASS | unsupported embedding claim |
| irrelevant_answer_low | answer_relevancy | low | 0.00 | PASS | Cosine similarity between original question and judge-generated reverse question. |
| context_recall_high | context_recall | high | 1.00 | PASS | 2/2 ground-truth claims found in retrieved context. |
| context_recall_missing_claim_low | context_recall | low | 0.50 | PASS | 1/2 ground-truth claims found in retrieved context. |

The self-check is required because a judge that always gives high scores is broken. At least one unsupported faithfulness case, one missing-claim Context Recall case, and one irrelevant answer case must receive a low score, or be explicitly marked as not measured when embeddings are unavailable.

## Results

| Case | Top Paths | Faithfulness | Answer Relevancy | Context Recall | Notes |
| --- | --- | ---: | ---: | --- | --- |
| readme_portfolio | README.md | 0.50 | 0.00 | 0.33 | ambiguous deterministic score |
| payment_fallback | src/services/payment_service.py, src/api/routes/orders.py, src/services/notification_service.py, src/services/auth_service.py, src/config/settings.py | 0.50 | 0.00 | 0.67 | ambiguous deterministic score |
| service_layer_refactor | src/api/routes/orders.py, main.py | 0.50 | 0.00 | not measured | ambiguous deterministic score |
| jwt_500_bug | src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py, src/services/payment_service.py, README.md | 0.50 | 0.00 | 0.50 | ambiguous deterministic score |
| products_pagination | src/api/routes/products.py, main.py, src/api/routes/orders.py, src/db/models.py, src/api/routes/middleware.py | 0.50 | 0.00 | not measured | ambiguous deterministic score |
| auth_service_unit_test | src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py, src/services/payment_service.py, src/api/routes/orders.py | 0.50 | 0.00 | not measured | ambiguous deterministic score |
| last_login_migration | src/db/models.py, src/api/routes/users.py, src/api/routes/orders.py, src/api/routes/products.py, main.py | 0.50 | 0.00 | not measured | ambiguous deterministic score |
| env_guide | README.md, src/config/settings.py | 0.50 | 0.00 | not measured | ambiguous deterministic score |
| payment_code_review | src/services/payment_service.py, README.md, src/api/routes/orders.py, src/services/notification_service.py, src/services/auth_service.py | 0.50 | 0.00 | not measured | ambiguous deterministic score |
| payment_retry_issue | src/services/payment_service.py, README.md, src/api/routes/orders.py, src/services/notification_service.py, src/services/auth_service.py | 0.50 | 0.00 | not measured | ambiguous deterministic score |

## Metric Definitions

- Faithfulness: asks the configured judge whether answer claims are supported by retrieved context. The default judge is local Ollama; `keyword-self-check` is deterministic and intended for smoke tests.
- Answer Relevancy: asks the judge to generate a reverse question from the answer, then compares it with the original task using the configured embedding client.
- Context Recall: decomposes a ground-truth answer into claims and estimates what fraction of those claims are attributable to retrieved context. It is measured only for cases with `ground_truth_answer`.

## How To Regenerate

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_ragas.py --judge keyword-self-check
```

Recommended local setup for Answer Relevancy:

```powershell
ollama pull bge-m3
```
