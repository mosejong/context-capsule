# External Repo Evaluation

Generated at: 2026-06-28 18:01:10

Repository fixture: `tests\fixtures\external_repos\ecommerce`
Case file: `tests\fixtures\external_repo_eval_cases.json`
Retriever mode: `keyword`

This report validates Context Capsule against a small external-style FastAPI ecommerce repository. It is a regression harness and product signal, not a broad benchmark claim.

## Summary

- Cases: 10
- PASS: 10
- WARN: 0
- FAIL: 0
- hit@1: 9/10
- hit@3: 10/10
- target included in top results: 10/10
- risk floor satisfied: 10/10
- average estimated token reduction: 0.0%

## Results

| Case | Verdict | Best Rank | Expected Target | Actual Top Paths | Risk | Token Reduction | Notes |
| --- | --- | ---: | --- | --- | --- | ---: | --- |
| readme_portfolio | PASS | 1 | README.md | README.md | MEDIUM (expected >= MEDIUM) | 0.0% | OK |
| payment_fallback | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, src/api/routes/orders.py, README.md, src/services/notification_service.py, src/config/settings.py | MEDIUM (expected >= MEDIUM) | 0.0% | OK |
| service_layer_refactor | PASS | 1 | src/api/routes/orders.py | src/api/routes/orders.py, main.py | MEDIUM (expected >= MEDIUM) | 0.0% | OK |
| jwt_500_bug | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, src/api/routes/users.py, README.md, src/services/notification_service.py, src/services/payment_service.py | HIGH (expected >= HIGH) | 0.0% | OK |
| products_pagination | PASS | 1 | src/api/routes/products.py | src/api/routes/products.py, main.py, src/api/routes/orders.py, src/db/models.py, src/api/routes/middleware.py | MEDIUM (expected >= MEDIUM) | 0.0% | OK |
| auth_service_unit_test | PASS | 1 | src/services/auth_service.py | src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py, src/services/payment_service.py, README.md | HIGH (expected >= HIGH) | 0.0% | OK |
| last_login_migration | PASS | 1 | src/db/models.py, src/db/database.py | src/db/models.py, src/api/routes/users.py, src/api/routes/orders.py, src/api/routes/products.py, main.py | HIGH (expected >= HIGH) | 0.0% | OK |
| env_guide | PASS | 2 | .env.example, src/config/settings.py | README.md, src/config/settings.py | MEDIUM (expected >= MEDIUM) | 0.0% | OK |
| payment_code_review | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, README.md, src/api/routes/orders.py, src/services/notification_service.py, src/services/auth_service.py | MEDIUM (expected >= MEDIUM) | 0.0% | OK |
| payment_retry_issue | PASS | 1 | src/services/payment_service.py | src/services/payment_service.py, README.md, src/api/routes/orders.py, src/services/notification_service.py, src/services/auth_service.py | MEDIUM (expected >= MEDIUM) | 0.0% | OK |

## Interpretation

- `PASS` means the core target file ranked within the case threshold and risk was not under-warned.
- `WARN` means the target was found, but ranking was weaker than expected or risk was stricter than expected.
- `FAIL` means the core target file was missing or risk was below the expected floor.
- This fixture is intentionally small, so token reduction may be `0.0%`. In small repositories, this harness mainly validates target-file selection and risk floor behavior.

## How To Regenerate

```powershell
.\.venv\Scripts\python.exe scripts\evaluate_external_repo.py
```
