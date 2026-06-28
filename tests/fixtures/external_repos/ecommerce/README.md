# ShopFlow Dummy Ecommerce API

ShopFlow is a small FastAPI ecommerce backend used as an external-repository evaluation fixture for Context Capsule.

## Features

- User login and JWT token issuance
- Product listing API
- Order creation API
- Payment authorization service
- Notification service
- Environment-based settings

## Known seeded issues

- `src/services/auth_service.py` does not handle expired JWT tokens cleanly.
- `src/services/payment_service.py` has no retry or fallback behavior.
- `src/api/routes/products.py` has no pagination support.
- `src/db/models.py` does not include `last_login`.

## Local run

```bash
uvicorn main:app --reload
```
