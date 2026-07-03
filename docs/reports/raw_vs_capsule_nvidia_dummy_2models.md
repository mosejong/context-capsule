# Raw vs Context Capsule — 전체 비교

**날짜**: 2026-07-03  
**Provider**: nvidia_nim  
**모델**: nvidia/nemotron-3-ultra-550b-a55b, deepseek-ai/deepseek-v4-flash

## 실험 요약 수치

- CC 전체 정답률: 18/18 (100.0%)
- Raw 전체 정답률: 16/18 (88.9%)
- 평균 토큰 절감: 46.0%
- 핵심 메시지: 비싼 모델도 Raw 컨텍스트에서는 추상적으로 답할 수 있으며, Context Capsule이 관련 근거를 좁혀줄 때 파일명/함수명/수치 정확도가 살아난다.

## Provider Cost Observation

NVIDIA NIM Build endpoints are treated as prototype/testing endpoints in this report. No product-operation cost guarantee is claimed, and API keys are read only from `NVIDIA_API_KEY` without being written to reports or metadata.

## Actual API Cost (computed from response `usage`)

No local price table is configured for this provider. Usage can be captured when the endpoint returns token usage, but this report does not convert it to billing cost.

## Run Scope

- Selected repos: dummy
- Task limit per repo: 3
- The table below is generated only from this run's measured rows.
- If `--task-limit` is set, treat this as a smoke test, not a full benchmark.
- Provider calls retry transient 429/5xx/timeout errors up to 2 times before recording an error.

## Repo/Model Summary

| Repo | Model | Raw measured | Raw score | CC score | Avg token reduction |
|---|---|---:|---:|---:|---:|
| dummy-repo (소형 16파일) | deepseek-v4-flash | 3 | 9/9 | 9/9 | 46.0% |
| dummy-repo (소형 16파일) | nemotron-3-ultra-550b-a55b | 3 | 7/9 | 9/9 | 46.0% |

## 요약

| 레포 | ID | 태스크 | 모델 | Raw토큰 | CC토큰 | 절감 | Raw점수 | CC점수 | Raw비용 | CC비용 |
|---|---|---|---|---|---|---|---|---|---:|---:|
| dummy-repo | D-T1 | auth_service 500 에러  | nemotron-3-ultra-550b-a55b | ~4,468 | ~2,327 | 47.9% | 3/3 | 3/3 | $0.0000 | $0.0000 |
| dummy-repo | D-T1 | auth_service 500 에러  | deepseek-v4-flash | ~4,468 | ~2,327 | 47.9% | 3/3 | 3/3 | $0.0000 | $0.0000 |
| dummy-repo | D-T2 | 결제 실패 고쳐줘 | nemotron-3-ultra-550b-a55b | ~4,468 | ~2,179 | 51.2% | 3/3 | 3/3 | $0.0000 | $0.0000 |
| dummy-repo | D-T2 | 결제 실패 고쳐줘 | deepseek-v4-flash | ~4,468 | ~2,179 | 51.2% | 3/3 | 3/3 | $0.0000 | $0.0000 |
| dummy-repo | D-T3 | 로그인 안돼 | nemotron-3-ultra-550b-a55b | ~4,468 | ~2,732 | 38.9% | 1/3 | 3/3 | $0.0000 | $0.0000 |
| dummy-repo | D-T3 | 로그인 안돼 | deepseek-v4-flash | ~4,468 | ~2,732 | 38.9% | 3/3 | 3/3 | $0.0000 | $0.0000 |

---

## 상세 응답

### [D-T1] auth_service 500 에러 고쳐줘 — nemotron-3-ultra-550b-a55b

선택 파일: src/services/auth_service.py, src/services/payment_service.py, src/services/notification_service.py, src/utils/cache.py

**Raw 응답** (3/3)

The user wants me to fix the 500 error in `auth_service.py` when an expired JWT token is used. Let me analyze the issue.

From the code and the known issues in README.md:
- `#61` 만료된 JWT 토큰 → 500 에러 (401이어야 함)

Looking at `src/services/auth_service.py`, the `decode_token` function:
```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

The comment even says it doesn't catch JWTError, so expired tokens cause a 500 error instead of 401.

And in `src/api/routes/users.py`, the `get_current_user` function:
```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # decode_token이 JWTError를 안 잡아서 만료 토큰 → 500 터짐
    payload = decode_token(token)
   

**CC 응답** (3/3)

The user is asking me to fix a 500 error in auth_service. Looking at the context, I can see the issue:

1. In `src/services/auth_service.py`, the `decode_token` function doesn't catch `JWTError`, so expired tokens cause a 500 error instead of a proper 401.
2. In `src/api/routes/users.py`, the `get_current_user` function calls `decode_token` which throws an unhandled exception for expired/invalid tokens.
3. The README.md mentions issue #61: "만료된 JWT 토큰 → 500 에러 (401이어야 함)" - expired JWT token → 500 error (should be 401).

The fix should be in `src/services/auth_service.py` to catch `JWTError` in `decode_token` and raise an appropriate exception, or handle it in the `get_current_user` function in `src/api/routes/users.py`.

Let me analyze the files that need to be changed:
1. `src/services/auth_service.py` - The `decode_token` function needs to catch `JWTError`
2. `src/api/routes/users.py` - The `get_current

---

### [D-T1] auth_service 500 에러 고쳐줘 — deepseek-v4-flash

선택 파일: src/services/auth_service.py, src/services/payment_service.py, src/services/notification_service.py, src/utils/cache.py

**Raw 응답** (3/3)

# `auth_service.py` 500 에러 분석 및 수정

## 문제 원인

`decode_token` 함수에서 `JWTError` 예외를 처리하지 않아 만료된 토큰이나 유효하지 않은 토큰이 전달되면 500 Internal Server Error가 발생합니다.

### 현재 코드 (`src/services/auth_service.py`)

```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

`jwt.decode()`는 다음과 같은 경우 `JWTError`를 발생시킵니다:
- 토큰 만료 (`ExpiredSignatureError`)
- 서명 불일치 (`JWTClaimsError`)
- 잘못된 형식의 토큰

## 수정된 코드

```python
from jose import JWTError, jwt, ExpiredSignatureError

def decode_token(token: str) -> dict:
    """
    JWT 토큰을 디코딩합니다.
    
    Args:
       

**CC 응답** (3/3)

## 분석 결과

### 수정 대상 파일
1. **`src/services/auth_service.py`** - `decode_token` 함수에서 JWTError 예외 처리 누락
2. **`src/api/routes/users.py`** - `get_current_user` 함수에서 예외 처리 누락

### 예상 영향도

**높음 (HIGH)**
- 인증/권한 로직에 직접적인 영향
- 만료된 JWT 토큰으로 API 호출 시 500 에러 → 401 Unauthorized로 변경
- 모든 보호된 엔드포인트(orders, products 등)에 영향

**낮음 (LOW)**
- API 응답 형식만 변경 (500 → 401)
- 데이터베이스 스키마 변경 없음
- 기존 정상 토큰 사용자에게 영향 없음

### 수정안

**1. `src/services/auth_service.py` - `decode_token` 함수 수정**
```python
def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:


---

### [D-T2] 결제 실패 고쳐줘 — nemotron-3-ultra-550b-a55b

선택 파일: src/services/payment_service.py, src/services/notification_service.py, src/utils/cache.py, src/api/routes/orders.py

**Raw 응답** (3/3)

The user wants me to fix the payment failure issue. Let me analyze the codebase to understand the problem.

From the README.md, I can see known issues:
- `#58` 결제 실패 시 재시도 로직 없음 (No retry logic on payment failure)

Looking at the payment service (`src/services/payment_service.py`), I can see:
1. `charge_payment` function calls the payment API but has no retry logic
2. `process_order_payment` function calls `charge_payment` once and if it fails, immediately sets order status to "failed"
3. The comment says "재시도 로직 없음 — 한 번 실패하면 바로 failed 처리" (No retry logic - immediately marks as failed on first failure)

Also, from the config settings, there are retry-related environment variables:
- `MAX_RETRY_COUNT=3`
- `RETRY_DELAY_SECONDS=1.0`

But these are not being used in the payment service.

Let me also check if there are any other issues:
1. The `charge_payment` function catches `httpx.TimeoutException` and `httpx.HTTPStatusError` but raises `RuntimeError` in both cases
2. The `process_order_payment` catches `

**CC 응답** (3/3)

The user is asking me to fix a payment failure issue. Let me analyze the context to understand the problem.

From the context, I can see:
1. `payment_service.py` - Has a `charge_payment` function that calls a payment API, but it has no retry logic (just raises errors on timeout or HTTP errors)
2. `settings.py` - Has `MAX_RETRY_COUNT` and `RETRY_DELAY_SECONDS` config values that are defined but not used
3. `README.md` - Lists known issue `#58` "결제 실패 시 재시도 로직 없음" (No retry logic on payment failure)
4. `orders.py` - Uses `process_order_payment` from payment_service (but I only see `charge_payment` in the provided code snippet)

The issue is clear: payment failures (timeouts, HTTP errors) are not retried. The config has retry settings but they're not being used.

Let me check what needs to be modified:
1. `src/services/payment_service.py` - Add retry logic to `charge_payment` function using the config values
2. Possibly need to import the retry config from settings

The user wants me to analyze first and explain the impact before

---

### [D-T2] 결제 실패 고쳐줘 — deepseek-v4-flash

선택 파일: src/services/payment_service.py, src/services/notification_service.py, src/utils/cache.py, src/api/routes/orders.py

**Raw 응답** (3/3)

# 결제 실패 문제 분석 및 수정

## 현재 문제점

`src/services/payment_service.py`의 `process_order_payment` 함수에서 결제 실패 시 재시도 로직이 없어 한 번 실패하면 바로 주문이 `failed` 상태가 됩니다. 이는 README에 명시된 이슈 `#58`에 해당합니다.

## 수정할 파일

### 1. `src/services/payment_service.py` - 재시도 로직 추가

```python
import httpx
import logging
import time
from sqlalchemy.orm import Session
from src.db.models import Order
from src.config.settings import (
    PAYMENT_API_KEY, 
    PAYMENT_API_URL, 
    PAYMENT_TIMEOUT_SECONDS,
    MAX_RETRY_COUNT,
    RETRY_DELAY_SECONDS
)

logger = logging.getLogger(__name__)


def charge_payment(order_id: int, amount: float, card_token: str) -> dict:
    """결제 API 호출. 재시도 가능하도록 예외를 명확히 구분."""
    headers = {"Authorization": f"Bearer {PAYMENT_API_KEY}"}
    payload

**CC 응답** (3/3)

# 결제 실패 문제 분석

## 수정 대상 파일

1. **`src/services/payment_service.py`** - 결제 API 호출 및 재시도 로직
2. **`src/api/routes/orders.py`** - 주문 생성 및 결제 처리 라우트
3. **`src/config/settings.py`** - 재시도 관련 설정 (이미 존재)

## 예상 영향도

### 1. `payment_service.py` - 결제 재시도 로직 추가 (높은 영향도)

**현재 문제**: `charge_payment` 함수가 실패 시 fallback 없이 바로 에러를 던짐 (README.md #58 이슈)

**수정안**:
```python
import time
from src.config.settings import MAX_RETRY_COUNT, RETRY_DELAY_SECONDS

def charge_payment(order_id: int, amount: float, card_token: str) -> dict:
    """결제 API 호출. 실패 시 재시도 로직 포함."""
    headers = {"Authorization": f"Bearer {PAYMENT_API_KEY}"}
    payload = {
        "order_id": str(order_id),
       

---

### [D-T3] 로그인 안돼 — nemotron-3-ultra-550b-a55b

선택 파일: src/services/payment_service.py, src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py

**Raw 응답** (1/3)

The user is reporting a login issue ("로그인 안돼" - login doesn't work). I need to analyze the codebase to identify potential causes for login failures.

Let me examine the relevant files:
1. `src/api/routes/users.py` - login endpoint
2. `src/services/auth_service.py` - authentication logic
3. `src/db/models.py` - User model
4. `src/config/settings.py` - configuration

Looking at the login flow:
1. User sends email/password via OAuth2PasswordRequestForm (username field is used for email)
2. `authenticate_user` is called with `form.username` (email) and `form.password`
3. `authenticate_user` queries user by email, verifies password
4. If successful, creates access token

Potential issues I can see:

1. **OAuth2PasswordRequestForm uses `username` field but we're using email** - The form expects `username` and `password` fields. In the login endpoint, it uses `form.username` as email. This should work if the client sends `username` field with email value.

2. **Password hashing/verification** - Uses bcrypt via passlib. `verify_password`

**CC 응답** (3/3)

The user is reporting a login issue ("로그인 안돼" - login not working). Let me analyze the provided code to identify potential causes.

Looking at the context files, I can see several authentication-related files:

1. **src/services/auth_service.py** - Contains authentication logic
2. **src/api/routes/users.py** - Contains login/register endpoints
3. **src/db/models.py** - User model

Let me analyze the auth_service.py more carefully:

```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

The comment explicitly states there's a bug: JWTError is not caught, so expired tokens cause 500 errors.

Also in users.py:
```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # decode_token이 JWTError를 안 잡아서 만료 토큰 → 500 터짐
    payload = decode_token(token)
    ...
```

And the authenticate

---

### [D-T3] 로그인 안돼 — deepseek-v4-flash

선택 파일: src/services/payment_service.py, src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py

**Raw 응답** (3/3)

# 로그인 안됨 문제 분석

## 문제 진단

로그인이 안 되는 원인은 여러 가지가 있을 수 있습니다. 주요 원인과 관련 파일을 분석해드리겠습니다.

## 주요 원인 및 해결 방안

### 1. **JWT 토큰 만료 시 500 에러 (이슈 #61)**

**관련 파일:** `src/services/auth_service.py`, `src/api/routes/users.py`

```python
# src/services/auth_service.py - 문제 코드
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

**해결 방안:**
```python
from jose import JWTError, ExpiredSignatureError

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401

**CC 응답** (3/3)

## 분석 결과

"로그인 안돼"라는 문제를 분석하기 위해 관련 컨텍스트를 검토했습니다.

### 수정 대상 파일
1. **src/services/auth_service.py** - `decode_token` 함수 (JWT 예외 처리 누락)
2. **src/api/routes/users.py** - `get_current_user` 함수 (토큰 검증 로직)

### 예상 영향도

**높은 영향도:**
- `auth_service.py`의 `decode_token` 함수는 JWTError를 잡지 않아 만료된 토큰이나 잘못된 토큰이 들어오면 500 Internal Server Error 발생
- `users.py`의 `get_current_user` 함수는 이 문제를 그대로 전파받아 로그인/인증 실패 시 적절한 401 응답 대신 500 에러 발생

**낮은 영향도:**
- 다른 API 엔드포인트(orders, products)도 `get_current_user`에 의존하므로 간접적 영향

### 위험도 평가: 🔴 높음

**주요 위험:**
1. 만료된 JWT 토�

---

