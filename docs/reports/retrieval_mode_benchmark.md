# Retrieval Mode Benchmark

Generated at: 2026-07-02 17:38:31

Repository fixture: `tests\fixtures\external_repos\ecommerce`
Case file: `tests\fixtures\external_repo_eval_cases.json`
Embedding model setting: `hash_local_v1`

This report compares retrieval modes on the same external-style fixture. It is a local quality gate for choosing Korean/multilingual embedding candidates, not a broad benchmark claim.

## Provider Setup

| Mode | Provider / preparation |
| --- | --- |
| keyword | not_required |
| hybrid | hash_local_v1 |
| indexed | hash_local_v1 |

## Summary

| Mode | Cases | PASS | WARN | FAIL | hit@1 | hit@3 | Included | Risk OK | Avg ms | Avg reduction | Used modes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| keyword | 10 | 10 | 0 | 0 | 9 | 10 | 10 | 10 | 10.23 | 0.0% | keyword |
| hybrid | 10 | 10 | 0 | 0 | 10 | 10 | 10 | 10 | 12.88 | 0.0% | hybrid |
| indexed | 10 | 10 | 0 | 0 | 9 | 10 | 10 | 10 | 14.0 | 0.0% | indexed |

## Results

| Mode | Case | Verdict | Best Rank | Expected | Top Paths | Risk | ms | Notes |
| --- | --- | --- | ---: | --- | --- | --- | ---: | --- |
| keyword | readme_portfolio | PASS | 1 | README.md | README.md | MEDIUM (expected >= MEDIUM) | 14.27 | OK |
| keyword | payment_fallback | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, src/services/notification_service.py, src/services/auth_service.py, src/config/settings.py | MEDIUM (expected >= MEDIUM) | 10.25 | OK |
| keyword | service_layer_refactor | PASS | 1 | src/api/routes/orders.py | src/api/routes/orders.py, main.py | MEDIUM (expected >= MEDIUM) | 9.93 | OK |
| keyword | jwt_500_bug | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py, src/services/payment_service.py, README.md | HIGH (expected >= HIGH) | 10.22 | OK |
| keyword | products_pagination | PASS | 1 | src/api/routes/products.py | src/api/routes/products.py, main.py, src/api/routes/orders.py, src/db/models.py, src/api/routes/middleware.py | MEDIUM (expected >= MEDIUM) | 9.68 | OK |
| keyword | auth_service_unit_test | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py, src/services/payment_service.py, src/api/routes/orders.py | HIGH (expected >= HIGH) | 10.23 | OK |
| keyword | last_login_migration | PASS | 1 | src/db/models.py, src/db/database.py | src/db/models.py, src/api/routes/users.py, src/api/routes/orders.py, src/api/routes/products.py, main.py | HIGH (expected >= HIGH) | 10.00 | OK |
| keyword | env_guide | PASS | 2 | .env.example, src/config/settings.py | README.md, src/config/settings.py | MEDIUM (expected >= MEDIUM) | 7.36 | OK |
| keyword | payment_code_review | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, README.md, src/services/notification_service.py, src/services/auth_service.py | MEDIUM (expected >= MEDIUM) | 10.69 | OK |
| keyword | payment_retry_issue | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, README.md, src/services/notification_service.py, src/services/auth_service.py | MEDIUM (expected >= MEDIUM) | 9.70 | OK |
| hybrid | readme_portfolio | PASS | 1 | README.md | README.md | MEDIUM (expected >= MEDIUM) | 9.36 | OK |
| hybrid | payment_fallback | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, src/services/notification_service.py, README.md, src/config/settings.py | MEDIUM (expected >= MEDIUM) | 13.23 | OK |
| hybrid | service_layer_refactor | PASS | 1 | src/api/routes/orders.py | src/api/routes/orders.py, main.py, src/services/notification_service.py, README.md, src/services/payment_service.py | MEDIUM (expected >= MEDIUM) | 13.55 | OK |
| hybrid | jwt_500_bug | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, src/api/routes/users.py, README.md, src/services/notification_service.py, src/services/payment_service.py | HIGH (expected >= HIGH) | 14.03 | OK |
| hybrid | products_pagination | PASS | 1 | src/api/routes/products.py | src/api/routes/products.py, src/api/routes/orders.py, main.py, src/db/models.py, src/services/notification_service.py | MEDIUM (expected >= MEDIUM) | 13.22 | OK |
| hybrid | auth_service_unit_test | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py, src/services/payment_service.py, src/api/routes/orders.py | HIGH (expected >= HIGH) | 13.75 | OK |
| hybrid | last_login_migration | PASS | 1 | src/db/models.py, src/db/database.py | src/db/models.py, src/api/routes/users.py, src/api/routes/orders.py, src/api/routes/products.py, main.py | HIGH (expected >= HIGH) | 14.55 | OK |
| hybrid | env_guide | PASS | 1 | .env.example, src/config/settings.py | src/config/settings.py, README.md | MEDIUM (expected >= MEDIUM) | 9.83 | OK |
| hybrid | payment_code_review | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, README.md, src/services/notification_service.py, src/services/auth_service.py | MEDIUM (expected >= MEDIUM) | 13.85 | OK |
| hybrid | payment_retry_issue | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, README.md, src/services/notification_service.py, src/services/auth_service.py | MEDIUM (expected >= MEDIUM) | 13.38 | OK |
| indexed | readme_portfolio | PASS | 1 | README.md | README.md | MEDIUM (expected >= MEDIUM) | 24.23 | OK |
| indexed | payment_fallback | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, README.md, src/services/notification_service.py, src/config/settings.py | MEDIUM (expected >= MEDIUM) | 12.54 | OK |
| indexed | service_layer_refactor | PASS | 1 | src/api/routes/orders.py | src/api/routes/orders.py, main.py, src/services/notification_service.py, README.md, src/services/payment_service.py | MEDIUM (expected >= MEDIUM) | 12.18 | OK |
| indexed | jwt_500_bug | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, src/api/routes/users.py, README.md, src/services/notification_service.py, src/db/models.py | HIGH (expected >= HIGH) | 12.86 | OK |
| indexed | products_pagination | PASS | 1 | src/api/routes/products.py | src/api/routes/products.py, src/api/routes/orders.py, README.md, src/db/models.py, main.py | MEDIUM (expected >= MEDIUM) | 13.25 | OK |
| indexed | auth_service_unit_test | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, README.md, src/db/models.py, src/api/routes/users.py, requirements.txt | HIGH (expected >= HIGH) | 12.32 | OK |
| indexed | last_login_migration | PASS | 2 | src/db/models.py, src/db/database.py | README.md, src/db/models.py, src/api/routes/users.py, main.py, src/services/notification_service.py | HIGH (expected >= HIGH) | 12.93 | OK |
| indexed | env_guide | PASS | 1 | .env.example, src/config/settings.py | src/config/settings.py, README.md | MEDIUM (expected >= MEDIUM) | 11.23 | OK |
| indexed | payment_code_review | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, README.md, src/api/routes/orders.py, src/services/notification_service.py, src/services/auth_service.py | MEDIUM (expected >= MEDIUM) | 14.69 | OK |
| indexed | payment_retry_issue | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, README.md, src/api/routes/orders.py, src/services/notification_service.py, src/api/routes/products.py | MEDIUM (expected >= MEDIUM) | 13.79 | OK |

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
