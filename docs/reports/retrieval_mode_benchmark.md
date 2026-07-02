# Retrieval Mode Benchmark

Generated at: 2026-07-02 17:13:12

Repository fixture: `tests\fixtures\external_repos\ecommerce`
Case file: `tests\fixtures\external_repo_eval_cases.json`
Embedding model setting: `hash_local_v1`

This report compares retrieval modes on the same external-style fixture. It is a local quality gate for choosing Korean/multilingual embedding candidates, not a broad benchmark claim.

## Provider Setup

| Mode | Provider / preparation |
| --- | --- |
| keyword | not_required |
| hybrid | not_required |
| indexed | hash_local_v1 |

## Summary

| Mode | Cases | PASS | WARN | FAIL | hit@1 | hit@3 | Included | Risk OK | Avg ms | Avg reduction | Used modes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| keyword | 10 | 10 | 0 | 0 | 9 | 10 | 10 | 10 | 10.19 | 0.0% | keyword |
| hybrid | 10 | 10 | 0 | 0 | 10 | 10 | 10 | 10 | 13.45 | 0.0% | hybrid |
| indexed | 10 | 10 | 0 | 0 | 9 | 10 | 10 | 10 | 15.19 | 0.0% | indexed |

## Results

| Mode | Case | Verdict | Best Rank | Expected | Top Paths | Risk | ms | Notes |
| --- | --- | --- | ---: | --- | --- | --- | ---: | --- |
| keyword | readme_portfolio | PASS | 1 | README.md | README.md | MEDIUM (expected >= MEDIUM) | 18.21 | OK |
| keyword | payment_fallback | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, src/services/notification_service.py, src/services/auth_service.py, src/config/settings.py | MEDIUM (expected >= MEDIUM) | 10.20 | OK |
| keyword | service_layer_refactor | PASS | 1 | src/api/routes/orders.py | src/api/routes/orders.py, main.py | MEDIUM (expected >= MEDIUM) | 8.14 | OK |
| keyword | jwt_500_bug | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py, src/services/payment_service.py, README.md | HIGH (expected >= HIGH) | 9.48 | OK |
| keyword | products_pagination | PASS | 1 | src/api/routes/products.py | src/api/routes/products.py, main.py, src/api/routes/orders.py, src/db/models.py, src/api/routes/middleware.py | MEDIUM (expected >= MEDIUM) | 9.44 | OK |
| keyword | auth_service_unit_test | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py, src/services/payment_service.py, src/api/routes/orders.py | HIGH (expected >= HIGH) | 9.51 | OK |
| keyword | last_login_migration | PASS | 1 | src/db/models.py, src/db/database.py | src/db/models.py, src/api/routes/users.py, src/api/routes/orders.py, src/api/routes/products.py, main.py | HIGH (expected >= HIGH) | 9.43 | OK |
| keyword | env_guide | PASS | 2 | .env.example, src/config/settings.py | README.md, src/config/settings.py | MEDIUM (expected >= MEDIUM) | 7.66 | OK |
| keyword | payment_code_review | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, README.md, src/services/notification_service.py, src/services/auth_service.py | MEDIUM (expected >= MEDIUM) | 9.14 | OK |
| keyword | payment_retry_issue | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, README.md, src/services/notification_service.py, src/services/auth_service.py | MEDIUM (expected >= MEDIUM) | 10.66 | OK |
| hybrid | readme_portfolio | PASS | 1 | README.md | README.md | MEDIUM (expected >= MEDIUM) | 10.05 | OK |
| hybrid | payment_fallback | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, src/services/notification_service.py, README.md, src/config/settings.py | MEDIUM (expected >= MEDIUM) | 13.53 | OK |
| hybrid | service_layer_refactor | PASS | 1 | src/api/routes/orders.py | src/api/routes/orders.py, main.py, src/services/notification_service.py, README.md, src/services/payment_service.py | MEDIUM (expected >= MEDIUM) | 13.63 | OK |
| hybrid | jwt_500_bug | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, src/api/routes/users.py, README.md, src/services/notification_service.py, src/services/payment_service.py | HIGH (expected >= HIGH) | 13.99 | OK |
| hybrid | products_pagination | PASS | 1 | src/api/routes/products.py | src/api/routes/products.py, src/api/routes/orders.py, main.py, src/db/models.py, src/services/notification_service.py | MEDIUM (expected >= MEDIUM) | 14.19 | OK |
| hybrid | auth_service_unit_test | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py, src/services/payment_service.py, src/api/routes/orders.py | HIGH (expected >= HIGH) | 13.97 | OK |
| hybrid | last_login_migration | PASS | 1 | src/db/models.py, src/db/database.py | src/db/models.py, src/api/routes/users.py, src/api/routes/orders.py, src/api/routes/products.py, main.py | HIGH (expected >= HIGH) | 14.16 | OK |
| hybrid | env_guide | PASS | 1 | .env.example, src/config/settings.py | src/config/settings.py, README.md | MEDIUM (expected >= MEDIUM) | 9.78 | OK |
| hybrid | payment_code_review | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, README.md, src/services/notification_service.py, src/services/auth_service.py | MEDIUM (expected >= MEDIUM) | 14.12 | OK |
| hybrid | payment_retry_issue | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, README.md, src/services/notification_service.py, src/services/auth_service.py | MEDIUM (expected >= MEDIUM) | 17.06 | OK |
| indexed | readme_portfolio | PASS | 1 | README.md | README.md | MEDIUM (expected >= MEDIUM) | 22.79 | OK |
| indexed | payment_fallback | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, README.md, src/services/notification_service.py, src/config/settings.py | MEDIUM (expected >= MEDIUM) | 13.81 | OK |
| indexed | service_layer_refactor | PASS | 1 | src/api/routes/orders.py | src/api/routes/orders.py, main.py, src/services/notification_service.py, README.md, src/services/payment_service.py | MEDIUM (expected >= MEDIUM) | 13.38 | OK |
| indexed | jwt_500_bug | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, src/api/routes/users.py, README.md, src/services/notification_service.py, src/db/models.py | HIGH (expected >= HIGH) | 13.68 | OK |
| indexed | products_pagination | PASS | 1 | src/api/routes/products.py | src/api/routes/products.py, src/api/routes/orders.py, README.md, src/db/models.py, main.py | MEDIUM (expected >= MEDIUM) | 16.93 | OK |
| indexed | auth_service_unit_test | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, README.md, src/db/models.py, src/api/routes/users.py, requirements.txt | HIGH (expected >= HIGH) | 17.33 | OK |
| indexed | last_login_migration | PASS | 2 | src/db/models.py, src/db/database.py | README.md, src/db/models.py, src/api/routes/users.py, main.py, src/services/notification_service.py | HIGH (expected >= HIGH) | 14.84 | OK |
| indexed | env_guide | PASS | 1 | .env.example, src/config/settings.py | src/config/settings.py, README.md | MEDIUM (expected >= MEDIUM) | 9.80 | OK |
| indexed | payment_code_review | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, README.md, src/api/routes/orders.py, src/services/notification_service.py, src/services/auth_service.py | MEDIUM (expected >= MEDIUM) | 14.68 | OK |
| indexed | payment_retry_issue | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, README.md, src/api/routes/orders.py, src/services/notification_service.py, src/api/routes/products.py | MEDIUM (expected >= MEDIUM) | 14.63 | OK |

## How To Regenerate

```powershell
.\.venv\Scripts\python.exe scripts\benchmark_retrieval_modes.py --modes keyword hybrid indexed
```

To test a local multilingual model:

```powershell
$env:CONTEXT_CAPSULE_EMBEDDING_MODEL = "BAAI/bge-m3"
.\.venv\Scripts\python.exe scripts\benchmark_retrieval_modes.py --modes hybrid indexed
```
