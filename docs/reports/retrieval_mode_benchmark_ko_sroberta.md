# Retrieval Mode Benchmark

Generated at: 2026-07-02 17:33:11

Repository fixture: `tests\fixtures\external_repos\ecommerce`
Case file: `tests\fixtures\external_repo_eval_cases.json`
Embedding model setting: `jhgan/ko-sroberta-multitask`

This report compares retrieval modes on the same external-style fixture. It is a local quality gate for choosing Korean/multilingual embedding candidates, not a broad benchmark claim.

## Provider Setup

| Mode | Provider / preparation |
| --- | --- |
| hybrid | sentence_transformers:jhgan/ko-sroberta-multitask:input_plain_v1 |

## Summary

| Mode | Cases | PASS | WARN | FAIL | hit@1 | hit@3 | Included | Risk OK | Avg ms | Avg reduction | Used modes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| hybrid | 10 | 10 | 0 | 0 | 10 | 10 | 10 | 10 | 2360.71 | 0.0% | hybrid |

## Results

| Mode | Case | Verdict | Best Rank | Expected | Top Paths | Risk | ms | Notes |
| --- | --- | --- | ---: | --- | --- | --- | ---: | --- |
| hybrid | readme_portfolio | PASS | 1 | README.md | README.md | MEDIUM (expected >= MEDIUM) | 2370.93 | OK |
| hybrid | payment_fallback | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, src/services/notification_service.py, src/utils/logger.py, src/config/settings.py | MEDIUM (expected >= MEDIUM) | 2270.41 | OK |
| hybrid | service_layer_refactor | PASS | 1 | src/api/routes/orders.py | src/api/routes/orders.py, main.py, src/config/settings.py, src/db/database.py, src/api/routes/middleware.py | MEDIUM (expected >= MEDIUM) | 2440.86 | OK |
| hybrid | jwt_500_bug | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, src/api/routes/users.py, README.md, src/services/payment_service.py, src/services/notification_service.py | HIGH (expected >= HIGH) | 2413.36 | OK |
| hybrid | products_pagination | PASS | 1 | src/api/routes/products.py | src/api/routes/products.py, main.py, src/api/routes/orders.py, src/db/models.py, src/utils/logger.py | MEDIUM (expected >= MEDIUM) | 2280.83 | OK |
| hybrid | auth_service_unit_test | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, src/api/routes/users.py, src/services/payment_service.py, src/services/notification_service.py, src/api/routes/orders.py | HIGH (expected >= HIGH) | 2239.85 | OK |
| hybrid | last_login_migration | PASS | 1 | src/db/models.py, src/db/database.py | src/db/models.py, src/api/routes/users.py, src/api/routes/orders.py, src/api/routes/products.py, src/db/database.py | HIGH (expected >= HIGH) | 2362.17 | OK |
| hybrid | env_guide | PASS | 1 | .env.example, src/config/settings.py | src/config/settings.py, README.md | MEDIUM (expected >= MEDIUM) | 2317.77 | OK |
| hybrid | payment_code_review | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, README.md, src/services/notification_service.py, src/services/auth_service.py | MEDIUM (expected >= MEDIUM) | 2365.93 | OK |
| hybrid | payment_retry_issue | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, README.md, src/services/notification_service.py, src/services/auth_service.py | MEDIUM (expected >= MEDIUM) | 2545.01 | OK |

## How To Regenerate

```powershell
.\.venv\Scripts\python.exe scripts\benchmark_retrieval_modes.py --modes keyword hybrid indexed
```

To test a local multilingual model:

```powershell
.\.venv\Scripts\python.exe scripts\benchmark_retrieval_modes.py --embedding-model BAAI/bge-m3 --modes hybrid indexed
```

`--embedding-model` sets `CONTEXT_CAPSULE_EMBEDDING_MODEL` only for that benchmark run.
Use `--offline` when the model is already cached or provided as a local path.
