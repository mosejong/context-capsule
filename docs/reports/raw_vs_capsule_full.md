# Raw vs Context Capsule — 전체 비교

**날짜**: 2026-06-29  
**모델**: claude-haiku-4-5-20251001, claude-sonnet-4-6

## 요약

| 레포 | ID | 태스크 | 모델 | Raw토큰 | CC토큰 | 절감 | Raw점수 | CC점수 |
|---|---|---|---|---|---|---|---|---|
| dummy-repo | D-T1 | auth_service 500 에러  | haiku | ~4,468 | ~2,406 | 46.2% | 3/3 | 3/3 |
| dummy-repo | D-T1 | auth_service 500 에러  | sonnet | ~4,468 | ~2,406 | 46.2% | 3/3 | 3/3 |
| dummy-repo | D-T2 | 결제 실패 고쳐줘 | haiku | ~4,468 | ~2,258 | 49.5% | 3/3 | 2/3 |
| dummy-repo | D-T2 | 결제 실패 고쳐줘 | sonnet | ~4,468 | ~2,258 | 49.5% | 2/3 | 3/3 |
| dummy-repo | D-T3 | 로그인 안돼 | haiku | ~4,468 | ~2,561 | 42.7% | 3/3 | 3/3 |
| dummy-repo | D-T3 | 로그인 안돼 | sonnet | ~4,468 | ~2,561 | 42.7% | 0/3 | 3/3 |
| procurement-logistics-ai | P-T1 | ML 모델 정확도가 몇 %야? | haiku | ~107,524 | ~2,658 | 97.5% | 0/4 | 0/4 |
| procurement-logistics-ai | P-T1 | ML 모델 정확도가 몇 %야? | haiku | ~107,524 | ~2,658 | 97.5% | CC only | 0/4 |
| procurement-logistics-ai | P-T1 | ML 모델 정확도가 몇 %야? | sonnet | ~107,524 | ~2,658 | 97.5% | CC only | 0/4 |
| procurement-logistics-ai | P-T2 | QA 리포트에 나온 성능 수치 알려줘 | haiku | ~107,524 | ~2,520 | 97.7% | 0/4 | 2/4 |
| procurement-logistics-ai | P-T2 | QA 리포트에 나온 성능 수치 알려줘 | haiku | ~107,524 | ~2,520 | 97.7% | CC only | 2/4 |
| procurement-logistics-ai | P-T2 | QA 리포트에 나온 성능 수치 알려줘 | sonnet | ~107,524 | ~2,520 | 97.7% | CC only | 2/4 |
| procurement-logistics-ai | P-T3 | 프로젝트 모델 성능 요약해줘 | haiku | ~107,524 | ~2,485 | 97.7% | 0/4 | 0/4 |
| procurement-logistics-ai | P-T3 | 프로젝트 모델 성능 요약해줘 | haiku | ~107,524 | ~2,485 | 97.7% | CC only | 0/4 |
| procurement-logistics-ai | P-T3 | 프로젝트 모델 성능 요약해줘 | sonnet | ~107,524 | ~2,485 | 97.7% | CC only | 0/4 |
| rainbow-bridge | R-T1 | auth 로그인 JWT 만료 처리 수 | haiku | - | ~2,195 | 0% | CC only | 3/3 |
| rainbow-bridge | R-T1 | auth 로그인 JWT 만료 처리 수 | sonnet | - | ~2,195 | 0% | CC only | 3/3 |
| rainbow-bridge | R-T2 | docker-compose.yml 배 | haiku | - | ~2,374 | 0% | CC only | 2/3 |
| rainbow-bridge | R-T2 | docker-compose.yml 배 | sonnet | - | ~2,374 | 0% | CC only | 3/3 |
| rainbow-bridge | R-T3 | users 테이블 마이그레이션 추가해 | haiku | - | ~2,750 | 0% | CC only | 2/3 |
| rainbow-bridge | R-T3 | users 테이블 마이그레이션 추가해 | sonnet | - | ~2,750 | 0% | CC only | 2/3 |

---

## 상세 응답

### [D-T1] auth_service 500 에러 고쳐줘 — haiku

선택 파일: src/services/auth_service.py, src/services/payment_service.py, src/services/notification_service.py, src/utils/cache.py

**Raw 응답** (3/3)

# auth_service 500 에러 분석 및 해결

## 📍 문제 원인

**파일**: `src/services/auth_service.py` → `decode_token()` 함수

```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

**문제점**: 
- 만료되거나 유효하지 않은 토큰이 들어오면 `jose.JWTError` 예외 발생
- 이를 처리하지 않아 서버 500 에러로 반환됨
- 클라이언트는 401(Unauthorized)을 받아야 함

---

## 🔗 영향받는 파일

**`src/api/routes/users.py`** → `get_current_user()` 함수

```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)  # ← 여기서 예외 발생 시 500 에러
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

---

## ✅ 해결책

### 1️⃣ **auth_service.py 수정**

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt  # ← JWTError import 필수
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.db.models import User
from src.config

**CC 응답** (3/3)

# 분석 결과: auth_service 500 에러

## 📋 수정 대상 파일
- `src/services/auth_service.py` (decode_token 함수)
- `src/api/routes/users.py` (get_current_user 함수)

---

## 🔍 문제 분석

### 근본 원인
**`decode_token()` 함수가 JWT 예외를 처리하지 않음**

```python
def decode_token(token: str) -> dict:
    # ❌ JWTError를 잡지 않음
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

만료되었거나 invalid한 토큰이 들어오면 `JWTError` 예외가 발생하고, 이를 catch하지 않아서 **500 Internal Server Error**가 반환됩니다.
- 올바른 동작: **401 Unauthorized** 반환

### 영향받는 흐름
1. 클라이언트가 만료된 토큰으로 요청
2. `get_current_user()` → `decode_token()` 호출
3. `JWTError` 예외 발생 (처리 안 됨)
4. FastAPI가 500 에러로 응답

---

## ⚠️ 예상 영향도

| 항목 | 수준 | 설명 |
|------|------|------|
| **기능 영향** | HIGH | 토큰 검증 로직 변경 → 모든 인증된 엔드포인트 영향 |
| **API 응답** | HIGH | 401 에러로 변경 (클라이언트 예외 처리 필요할 수 있음) |
| **보안** | POSITIVE | 올바른 401 응

---

### [D-T1] auth_service 500 에러 고쳐줘 — sonnet

선택 파일: src/services/auth_service.py, src/services/payment_service.py, src/services/notification_service.py, src/utils/cache.py

**Raw 응답** (3/3)

## 원인 분석

### 문제 파일: `src/services/auth_service.py` + `src/api/routes/users.py`

**`decode_token()`에서 `JWTError`를 잡지 않아서** JWT가 만료되거나 변조됐을 때 예외가 그대로 위로 올라가고, `get_current_user()`도 이를 처리하지 않아 FastAPI가 500으로 응답합니다.

```python
# auth_service.py — 현재 코드
def decode_token(token: str) -> dict:
    # JWTError가 터지면 아무도 안 잡음 → 500
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

```python
# users.py — 현재 코드
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # decode_token이 JWTError를 안 잡아서 만료 토큰 → 500 터짐
    payload = decode_token(token)  # 여기서 JWTError 그냥 전파
    ...
```

---

## 수정 코드

### `src/services/auth_service.py`

```python
from datetime import datetime, timedelta
from jose import JWTError, ExpiredSignatureError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from src.db.models import User
from src.config.settings import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    

**CC 응답** (3/3)

## 분석 결과

### 문제 원인 파악

**이슈 #61** (README 확인)과 코드 주석이 일치합니다.

`src/services/auth_service.py`의 `decode_token()` 함수가 `JWTError`를 catch하지 않아서, 만료되거나 잘못된 JWT 토큰이 들어오면 예외가 그대로 전파되어 **500 Internal Server Error**가 발생합니다. 올바른 동작은 **401 Unauthorized**를 반환하는 것입니다.

---

### 수정 대상 파일

| 파일 | 수정 이유 |
|---|---|
| `src/services/auth_service.py` | `decode_token()`에 JWTError 예외 처리 추가 |
| `src/api/routes/users.py` | `get_current_user()`에서 decode_token 예외를 401로 변환 |

---

### 예상 영향도

**변경 위험도: HIGH (인증/권한 로직)**

- `decode_token()`은 인증 미들웨어 역할을 하는 `get_current_user()`에서 호출됨
- `get_current_user()`는 `orders.py`의 모든 주문 엔드포인트에서 `Depends`로 사용됨
- 즉, **인증이 필요한 모든 라우트에 영향**

---

### 수정 후보 (2가지 방법)

#### 방법 A — `decode_token()` 내부에서 처리 (권장)

`auth_service.py`의 `decode_token()`을 아래처럼 변경합니다.

```python
# 변경 전
def decode_token(token

---

### [D-T2] 결제 실패 고쳐줘 — haiku

선택 파일: src/services/payment_service.py, src/services/notification_service.py, README.md, src/utils/cache.py

**Raw 응답** (3/3)

# 결제 실패 문제 분석 및 해결

## 🔴 문제점

README.md의 **이슈 #58**에서 언급된 대로, 결제 실패 시 **재시도 로직이 없어서** 일시적 네트워크 오류도 즉시 실패 처리됩니다.

---

## 📋 원인 분석

### 1. `src/services/payment_service.py` - `process_order_payment()`

```python
def process_order_payment(db: Session, order_id: int, card_token: str) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    
    # ❌ 재시도 없이 한 번 실패하면 바로 failed 처리
    try:
        result = charge_payment(order_id, order.total_amount, card_token)
        order.status = "paid"
        order.payment_id = result.get("payment_id")
    except RuntimeError:
        order.status = "failed"  # 즉시 실패 처리
```

**문제:**
- 타임아웃이나 일시적 오류도 구분 없이 처리
- 설정에서 `MAX_RETRY_COUNT=3`, `RETRY_DELAY_SECONDS=1.0`가 있는데 미사용

### 2. `src/api/routes/orders.py` - `create_order()`

```python
# 결제 처리 (재시도 없음)
order = process_order_payment(db, order.id, body.card_token)

if order.status == "paid":
    notify_order_paid(...)
else:
    notify_order_failed(...)  # 즉시 실패 알림
```

**문제:**
- 결제 실패 알림이 즉시 발송되어

**CC 응답** (2/3)

# 결제 실패 문제 분석

## 📋 문제 진단

제공된 컨텍스트에서 **결제 실패의 근본 원인**으로 보이는 이슈들:

1. **재시도 로직 부재** (README.md #58)
   - `charge_payment()`에서 실패 시 즉시 예외 발생
   - 일시적 네트워크 오류에 대한 복구 불가

2. **불완전한 에러 처리**
   - `payment_service.py`의 `refund_payment()` 함수가 **컷오프**됨 (불완전)
   - `process_order_payment()` 함수 **누락** (orders.py에서 호출하지만 정의 없음)

3. **트랜잭션 관리 불명확**
   - 결제 성공 후 DB 반영 전 실패 시 데이터 불일치 가능성

---

## 🎯 수정 대상 파일

```
1. src/services/payment_service.py
2. src/api/routes/orders.py (호출 로직 확인)
3. src/services/notification_service.py (알림 로직 확인)
```

---

## 📊 예상 영향도

| 항목 | 영향 범위 | 심각도 |
|------|---------|--------|
| `charge_payment()` 재시도 추가 | payment 결제 흐름 | **HIGH** |
| `process_order_payment()` 구현 | order 생성 전체 흐름 | **HIGH** |
| 트랜잭션 관리 추가 | DB 데이터 무결성 | **MEDIUM** |
| 에러 메시지 개선 | 로

---

### [D-T2] 결제 실패 고쳐줘 — sonnet

선택 파일: src/services/payment_service.py, src/services/notification_service.py, README.md, src/utils/cache.py

**Raw 응답** (2/3)

# 결제 실패 관련 버그 분석 및 수정

README의 이슈 `#58`(재시도 없음)과 연관된 `#61`(만료 JWT → 500 에러)까지 결제 흐름 전체에 걸쳐 문제가 있습니다. 각각 원인과 수정 코드를 설명합니다.

---

## 문제 1: 결제 재시도 로직 없음 (이슈 #58)

### 원인

**`src/services/payment_service.py`**

```python
# 현재 코드 — 한 번 실패하면 바로 failed 처리
try:
    result = charge_payment(order_id, order.total_amount, card_token)
    order.status = "paid"
    order.payment_id = result.get("payment_id")
except RuntimeError:
    order.status = "failed"   # ← 네트워크 순간 장애여도 즉시 실패
```

네트워크 순간 장애, 결제 서버 일시적 과부하 등 **재시도하면 성공할 수 있는 상황**에서도 즉시 `failed` 처리합니다.

추가로 `charge_payment` 내부에서 타임아웃/HTTP 에러가 아닌 **다른 예외**(예: `ConnectionError`, `json.JSONDecodeError`)는 `RuntimeError`로 변환되지 않아 `process_order_payment`의 `except RuntimeError`에 잡히지 않고 **500 에러로 터집니다.**

### 수정

```python
# src/services/payment_service.py

import httpx
import logging
import time
from sqlalchemy.orm import Session
from src.db.models import Order
from src.config.settings import (

**CC 응답** (3/3)

# 결제 실패 분석 보고서

## 1. 문제 진단

컨텍스트를 분석한 결과, **"결제 실패"**는 단일 버그가 아니라 복합적인 문제입니다.

### 확인된 이슈 목록

| # | 위치 | 문제 | 심각도 |
|---|------|------|--------|
| A | `payment_service.py` | `process_order_payment` 함수가 **존재하지 않음** (routes에서 import하지만 정의 없음) | 🔴 Critical |
| B | `payment_service.py` | `refund_payment` 함수가 **중간에 잘림** (컨텍스트 truncate) | 🟡 확인 필요 |
| C | `README.md #58` | 결제 실패 시 **재시도 로직 없음** | 🟠 Medium |
| D | `settings.py` | `MAX_RETRY_COUNT`, `RETRY_DELAY_SECONDS`가 정의돼 있으나 **실제로 사용되는 곳 없음** | 🟠 Medium |
| E | `payment_service.py` | 타임아웃/HTTP 에러 발생 시 **DB Order 상태가 rollback되지 않을 가능성** | 🟠 Medium |

---

## 2. 핵심 문제 상세

### 🔴 [A] `process_order_payment` 미정의 — 즉시 500 에러 원인

```python
# src/api/routes/orders.py
from src.services.payment_service import process_order_payment  # ← 이 함수가 없음!
```

`payment_service.py`에는 `charge_payment`와 `refund_payment`만 

---

### [D-T3] 로그인 안돼 — haiku

선택 파일: src/services/payment_service.py, src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py

**Raw 응답** (3/3)

# 로그인 문제 분석

## 🔴 발견된 문제

**원인: `src/api/routes/users.py`의 `get_current_user()` 함수에서 JWT 토큰 만료 시 예외 처리 부족**

---

## 📋 구체적인 문제점

### 1️⃣ **decode_token()이 JWTError를 처리하지 않음**

**파일**: `src/services/auth_service.py` (라인 23-25)

```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

**문제**:
- 토큰이 만료되거나 유효하지 않으면 `JWTError` 예외 발생
- 이 예외가 처리되지 않아 **500 에러**로 반환됨
- 정상적으로는 **401 Unauthorized**를 반환해야 함

---

### 2️⃣ **get_current_user()가 예외를 감싸지 않음**

**파일**: `src/api/routes/users.py` (라인 24-34)

```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # decode_token이 JWTError를 안 잡아서 만료 토큰 → 500 터짐
    payload = decode_token(token)  # ⬅️ JWTError 발생 시 미처리
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    user =

**CC 응답** (3/3)

# 분석 결과: "로그인 안돼" 문제 진단

## 🔍 문제 식별

사용자 요청 "로그인 안돼"는 **인증/로그인 기능 장애**를 의미합니다.
코드 분석 결과 **명확한 버그 2개**를 발견했습니다.

---

## 📋 수정 대상 파일

1. **src/services/auth_service.py** (라인 23-24)
2. **src/api/routes/users.py** (라인 34-35)

---

## ⚠️ 예상 영향도

| 구분 | 내용 |
|------|------|
| **즉각적 영향** | 만료되거나 유효하지 않은 JWT 토큰 → **500 Internal Server Error** 반환 (401이어야 함) |
| **사용자 경험** | 로그인 직후 또는 토큰 갱신 실패 시 "서버 오류" 메시지 → 실제는 인증 실패 |
| **디버깅 난이도** | HTTP 500은 예외 처리 실패로 보이므로 인증 로직 버그로 인식 어려움 |
| **영향 범위** | `/orders`, `/users` 등 `get_current_user` 의존하는 모든 보호된 엔드포인트 |

README.md의 **이슈 #61**에서도 같은 문제를 언급하고 있습니다.

---

## 🔧 문제 분석

### **버그 1: decode_token()에서 JWTError 미처리**

**src/services/auth_service.py:23-24**
```python
def decode_token(token

---

### [D-T3] 로그인 안돼 — sonnet

선택 파일: src/services/payment_service.py, src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py

**Raw 응답** (0/3)

# 로그인 안 되는 문제 분석

## 먼저 확인할 것: 어떤 증상인가요?

"로그인 안 된다"는 게 여러 가지일 수 있어서, 코드 기준으로 **가능한 원인 전부** 짚어드립니다.

---

## 원인 1: 가장 유력 — `SECRET_KEY` 기본값 문제

### 파일: `src/config/settings.py`

```python
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-prod")
```

### 파일: `.env.example`

```
SECRET_KEY=your-secret-key-here
```

`.env` 파일을 만들지 않았거나, `.env`에 `SECRET_KEY`를 실제 값으로 바꾸지 않은 채 실행하면
토큰 생성/검증은 되지만 **서버 재시작 시 토큰 무효화**가 일어납니다.

→ **`.env` 파일 존재 여부 먼저 확인하세요.**

```bash
ls -la .env          # 파일 있는지
cat .env | grep SECRET_KEY  # 실제 값 들어있는지
```

---

## 원인 2: 회원가입 안 한 상태에서 로그인 시도

### 파일: `src/api/routes/users.py`

```python
@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), ...):
    user = authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(status_code=401, detail="이메일 또는 비밀번호가 틀렸습니다")
```

`OAuth2PasswordRequestForm`

**CC 응답** (3/3)

# 로그인 안 되는 문제 분석

코드를 직접 수정하기 전에 원인과 영향도를 먼저 설명합니다.

---

## 🔍 식별된 원인 (2개)

### 원인 1 — 만료된 JWT 토큰 → 500 에러 (주요 원인)

**파일:** `src/services/auth_service.py` (27~29줄), `src/api/routes/users.py` (30~32줄)

```python
# 현재 코드 (auth_service.py)
def decode_token(token: str) -> dict:
    # JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

- `JWTError` (토큰 만료, 서명 불일치 등)를 전혀 잡지 않음
- 예외가 그대로 올라가 FastAPI가 500으로 응답
- README 이슈 `#61`에도 이미 기록된 알려진 버그

---

### 원인 2 — `authenticate_user` 함수 코드 잘림 (잠재적 원인)

**파일:** `src/services/auth_service.py` (43줄~)

```python
# 컨텍스트가 잘린 부분
if not verify_password(password, user.hash  # ← 여기서 끊김
```

- `user.hashed_password` 필드명이 실제 DB 모델과 불일치할 가능성
- `hashed_password` vs `hash_password` vs `password_hash` 등 네이밍 확인 필요

---

## 📋 수정 후보 

---

### [P-T1] ML 모델 정확도가 몇 %야? — haiku

선택 파일: check.md, README_portfolio.md, src/preprocess/classify_agency.py, README.md

**Raw 응답** (0/4)

[ERROR] Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'prompt is too long: 219016 tokens > 200000 maximum'}, 'request_id': 'req_011CcWecyYpaTmzdZpp55h7A'}

**CC 응답** (0/4)

# 분석 결과

## 작업 요청 검토
**Q: "ML 모델 정확도가 몇 %야?"**

---

## 답변: 수치 불일치 발견 ⚠️

컨텍스트에서 **동일한 ML 모델에 대해 서로 다른 정확도 수치**가 기록되어 있습니다:

| 출처 파일 | 기록된 수치 | 상세 내용 |
|---|---|---|
| `check.md:401-480` | **98.58%** | 검증 세트(val set) 기준, 훈련 데이터 86,991건 |
| `docs/numbers_reference.md` | **98%** | 홀드아웃 테스트셋 14,070건 기준 |
| `docs/rubric_alignment.md` | **98.6%** | (반올림 표기) |
| `docs/presentation_5min.md` | **98%** | 5분 발표 대본 버전 |

---

## 정확도 수치 선택 가이드

각 수치의 **맥락과 제약**:

### 1️⃣ **98.58%** (check.md)
- **측정 방식**: 검증 세트(validation set)
- **주의사항**: 
  - 훈련 레이블 자체가 "기존 키워드 규칙의 결과"이므로  
  - 실제로는 "**규칙 재현율(Rule Reproduction Rate)**에 가까움"
  - 검증 세트가 훈련 데이터와 같은 분포에서 나온 것
- **사용 대상**: 내부 기술 문서, 상세 검수 기록

### 2️⃣

---

### [P-T1] ML 모델 정확도가 몇 %야? — haiku

선택 파일: check.md, README_portfolio.md, src/preprocess/classify_agency.py, README.md

**CC 응답** (0/4)

# 분석 결과

## 📋 작업 요청 해석
"ML 모델 정확도가 몇 %야?" → 컨텍스트에서 ML 모델 성능 지표 조회

---

## 📊 답변

제공된 컨텍스트에서 **공고명 분류 ML 모델의 정확도**는 다음과 같습니다:

| 지표 | 수치 | 출처 |
|---|---|---|
| **검증 정확도 (홀드아웃)** | **98.58%** | check.md [1] |
| **발표자료 표기** | **98.6%** (반올림) | docs/numbers_reference.md [6], presentation_5min.md [7] |
| **테스트셋 규모** | 14,070건 | docs/numbers_reference.md [6] |
| **훈련 데이터** | 86,991건 | check.md [1] |

---

## ⚠️ 주의: 수치 정합성 문제 감지

컨텍스트 내에서 **상충하는 해석**이 존재합니다:

### 1️⃣ 정확도의 의미
- **check.md [1]**: "검증 정확도 98.58%는 훈련 레이블 자체가 키워드 규칙 결과이므로 **'규칙 재현율'에 가까움**"
  - 즉, 실제 정확도가 아니라 기존 키워드 규칙을 얼마나 잘 재현하는지의 지표
  
- **docs/numbers_reference.md [6]**: "홀드아웃 테스트셋 14,070건 기준" (98%)
  - 같은 테스

---

### [P-T1] ML 모델 정확도가 몇 %야? — sonnet

선택 파일: check.md, README_portfolio.md, src/preprocess/classify_agency.py, README.md

**CC 응답** (0/4)

## ML 모델 정확도 답변

### 핵심 수치

**검증 정확도: 98.58% (반올림 표기 시 98.6% 또는 약 98%)**

---

### 출처별 수치 정리

| 출처 파일 | 표기 수치 | 비고 |
|---|---|---|
| `check.md` | **98.58%** | 가장 상세한 원본 수치 |
| `README_portfolio.md` | **98.6%** | 소수점 1자리 반올림 |
| `docs/rubric_alignment.md` | **98.6%** | 동일 |
| `docs/numbers_reference.md` | **98%** | 정수 표기 |
| `docs/presentation_5min.md` | **98%** | 발표용 간략 표기 |

---

### ⚠️ 중요한 해석 주의사항

컨텍스트 내 `check.md`에 다음 주의 문구가 명시되어 있습니다:

> **"검증 정확도 98.58%는 훈련 레이블 자체가 키워드 규칙 결과이므로 '규칙 재현율'에 가까움"**

즉, 이 수치의 실제 의미는:

- ✅ **"키워드 규칙이 분류한 결과를 ML이 얼마나 잘 재현하는가"** → 98.58%
- ❌ **"실제 품목을 얼마나 정확히 분류하는가"** 라는 의미는 **아님**

또한 `docs/rubric_alignment.md`에는 약점도 명시되어 있습니다:
> "사무용품 Recall 0

---

### [P-T2] QA 리포트에 나온 성능 수치 알려줘 — haiku

선택 파일: docs/numbers_reference.md, docs/slides_ppt_content.md, docs/presentation_script.md, docs/rubric_alignment.md

**Raw 응답** (0/4)

[ERROR] Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'prompt is too long: 219016 tokens > 200000 maximum'}, 'request_id': 'req_011CcWeeeZsBNHG8EnKYAdXq'}

**CC 응답** (2/4)

# QA 리포트 성능 수치 분석

## 📋 작업 범위 확인
사용자 요청: **"QA 리포트에 나온 성능 수치"**
- ✅ 요청이 명확함 (문서 내 성능 수치 조회)
- ✅ 관련 컨텍스트 범위 내 (제공된 문서들에서 추출 가능)
- ⚠️ **주의**: "QA 리포트"라는 명시적 파일이 없으므로, 컨텍스트에서 성능 지표로 언급된 수치들을 조합 제시

---

## 🔍 추출된 성능 수치 (출처별 정리)

### **1단계: ML 모델 분류 정확도**
| 수치 | 의미 | 출처 | 신뢰도 |
|---|---|---|---|
| **98%** | ML 품목 분류기 정확도 | `docs/numbers_reference.md` | ✅ 높음 |
| **98.08%** | ML 분류 모델(TF-IDF + Logistic Regression) 정확도 | `docs/presentation_script.md` | ✅ 높음 |
| **0.57** | 사무용품 Recall 약점 | `docs/data_dictionary.md` | ⚠️ 부분 지표 |

**분석**: 두 수치가 98% vs 98.08%로 약간 차이 → **소수점 반올림 차이로 보임**. 모두 홀드아웃 테스트셋 ~14,070건 기준

---

### **2단계: 데이터 수집 규모**
| 수치 | 의미 

---

### [P-T2] QA 리포트에 나온 성능 수치 알려줘 — haiku

선택 파일: docs/numbers_reference.md, docs/slides_ppt_content.md, docs/presentation_script.md, docs/rubric_alignment.md

**CC 응답** (2/4)

# QA 리포트 성능 수치 분석

## 작업 범위 확인
요청: **"QA 리포트에 나온 성능 수치 알려줘"**  
→ 컨텍스트 내 성능 관련 수치 조회만 수행 (코드 수정 없음) ✅

---

## 발견된 성능 수치

### 1️⃣ **ML 분류기 정확도 — 98%**
| 항목 | 값 |
|---|---|
| **정확도** | 98.08% |
| **테스트 기준** | 홀드아웃 테스트셋 14,070건 |
| **모델** | TF-IDF + Logistic Regression |
| **분류 대상** | 공고명 → 18개 품목군 자동 분류 |
| **출처** | `src/modeling/train_classifier.py` |
| **알려진 약점** | 사무용품 Recall 0.57 (낮음) |

---

### 2️⃣ **데이터 수집 완성도**

| 수치 | 설명 | 출처 |
|---|---|---|
| **100,083건** | 전국 나라장터 입찰공고 전체 (2년, 전처리 완료) | `bid_cleaned_national.csv` |
| **72,103건** | feature_table 집계 bid_count 합계 | `feature_table_national.csv` |
| **285,552건** | aT 학교급식 BID(입찰) 5년치 | eAT 시스템 |
| **448,690건** | aT 학교급식 AWARD(낙찰) 3년치 | eAT 시스템 |
| **5,911개

---

### [P-T2] QA 리포트에 나온 성능 수치 알려줘 — sonnet

선택 파일: docs/numbers_reference.md, docs/slides_ppt_content.md, docs/presentation_script.md, docs/rubric_alignment.md

**CC 응답** (2/4)

## QA 리포트 성능 수치 정리

요청하신 "QA 리포트"에 해당하는 별도 파일은 제공된 컨텍스트에 포함되어 있지 않습니다.

다만 관련 컨텍스트에서 **성능/품질 수치로 확인되는 항목**들을 아래에 정리했습니다.

---

### 확인된 성능 수치

| 수치 | 내용 | 출처 컨텍스트 |
|---|---|---|
| **98%** (정확도) | ML 품목 분류기 정확도 / 홀드아웃 테스트셋 14,070건 기준 | `docs/numbers_reference.md`, `docs/data_dictionary.md` |
| **98.08%** | TF-IDF + Logistic Regression 기반 공고명 → 18개 품목군 분류 정확도 | `docs/presentation_script.md` |
| **사무용품 Recall 0.57** | ML 분류기의 약점 항목 (명시적 약점 수치) | `docs/data_dictionary.md` |

---

### 주의사항

- 위 수치는 **발표 자료 및 참조 카드** 문서에서 추출된 것이며, 독립된 QA 리포트 파일은 컨텍스트에 없습니다.
- `docs/slides_growth_potential.md` 하단의 **위험 신호 항목**에 다음이 명시되어 있습니다:
  > 문서 간 수치 값이 서로 달라 확인 필요 (15% / 20% / 25% / 40% — `docs/presentation_script.md` vs `docs/qa

---

### [P-T3] 프로젝트 모델 성능 요약해줘 — haiku

선택 파일: check.md, README.md, README_portfolio.md, docs/presentation_5min.md

**Raw 응답** (0/4)

[ERROR] Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'prompt is too long: 219016 tokens > 200000 maximum'}, 'request_id': 'req_011CcWegPkSYVYfWs8RQVCu6'}

**CC 응답** (0/4)

# 프로젝트 모델 성능 분석 요약

## 작업 범위 확인
✅ **범위 내**: 모델 성능 분석 및 요약 (코드 수정 없음)  
✅ **데이터 출처**: 제공된 컨텍스트 문서 (check.md, README.md, presentation_script.md 등)

---

## 📊 프로젝트 모델 성능 현황

### 1️⃣ **공고명 분류기 (ML 보조 모델)**

| 지표 | 값 | 평가 |
|---|---|---|
| **훈련 데이터** | 86,991건 / 전국 100,083건 중 규칙 매칭분 | ✅ 충분 |
| **검증 정확도** | **98.58%** | ✅ 높음 |
| confidence ≥ 0.55 비율 | 98.8% | ✅ 매우 높음 |
| **기타/미분류 재분류 가능** | 13,092건 중 3,857건 (29.5%) | ✅ 의미 있음 |
| **최종 기타/미분류 비율** | 13.1% → **9.2%** (전국 기준) | ✅ 4.2%p 개선 |

**구조**: 3단계 Fallback
```
공고명 → [1단계] 키워드 규칙 매칭 
       → [2단계] 미매칭 시 TF-IDF + Logistic Regression 
       → [3단계] confidence < 0.55 시 기타/미분류 유지
```

**⚠️ 주의**:
- 98.58%는 "규칙 

---

### [P-T3] 프로젝트 모델 성능 요약해줘 — haiku

선택 파일: check.md, README.md, README_portfolio.md, docs/presentation_5min.md

**CC 응답** (0/4)

# 프로젝트 모델 성능 요약

**작업 범위 확인:** "모델 성능 요약" 요청으로 분석 전용이며, 코드 수정은 포함되지 않습니다.

---

## 📊 핵심 성능 지표

### 1) **공고명 분류기 (ML 보조 모델)**
| 항목 | 수치 | 평가 |
|------|------|------|
| 훈련 데이터 | 86,991건 | 전국 100,083건 중 규칙 매칭분 |
| **검증 정확도** | **98.58%** | ⚠️ "규칙 재현율"에 가까움* |
| confidence ≥ 0.55 비율 | 98.8% | 높은 신뢰도 |
| **기타/미분류 개선** | 13,092건 중 3,857건 (29.5%) | 전체 9.2%로 저감 |

**⚠️ 주의사항:**
- 98.58% 정확도는 훈련 레이블이 **키워드 규칙 결과 자체**이므로 "규칙을 얼마나 잘 재현했는가"에 가까움
- 실제 비즈니스 임팩트는 "미분류 공고를 의미 있는 카테고리로 편입(29.5%)"하는 데 있음
- **발표/README에서는 수치보다 구조(3단계 fallback)를 강조하는 것이 적절**

---

### 2) **데이터 범위 확대 (서울 → 전국)**
| 항목 | 이전 | 현재 | 변

---

### [P-T3] 프로젝트 모델 성능 요약해줘 — sonnet

선택 파일: check.md, README.md, README_portfolio.md, docs/presentation_5min.md

**CC 응답** (0/4)

# 프로젝트 모델 성능 요약

컨텍스트 내 문서들을 분석해 모델별로 정리했습니다.

---

## 1. 공고명 분류기 (TF-IDF + Logistic Regression)

| 항목 | 값 |
|---|---|
| 훈련 데이터 | 86,991건 (전국 100,083건 중 키워드 규칙 매칭분) |
| 검증 정확도 | **98.58%** |
| confidence 임계값 | 0.55 |
| confidence ≥ 0.55 비율 | **98.8%** |
| 기타/미분류 재분류 대상 | 13,092건 중 3,857건 (29.5%) |
| 기타/미분류 비율 변화 | **13.1% → 9.2%** |

### ⚠️ 해석 주의사항
- 검증 정확도 98.58%는 **키워드 규칙 결과를 레이블로 사용**했기 때문에, 실제 정확도가 아닌 **"규칙 재현율"에 가까움**
- 실질적 개선 지표는 수치보다 **"기타/미분류 → 유효 카테고리 편입"** 구조

---

## 2. 수요예측 모델 (선형 회귀 + 계절 성분)

| 항목 | 값 |
|---|---|
| 모델 | 선형 회귀 + 가법 계절 성분 (월별 잔차 평균) |
| 학습 기간 | 24개월 (2년치) |
| 예측 방향 | 향후 3

---

### [R-T1] auth 로그인 JWT 만료 처리 수정해줘 — haiku

선택 파일: frontend-rn/api/auth.js, backend/app/schemas/auth.py, backend/app/services/auth.py, frontend-rn/app/(auth)/login.jsx

**CC 응답** (3/3)

# JWT 만료 처리 수정 - 분석 보고서

## 📋 작업 범위 확인
**요청**: auth 로그인 JWT 만료 처리 수정  
**현재 상태**: 컨텍스트에서 JWT 관련 코드는 발견되었으나, **만료 처리 로직이 불완전**합니다.

---

## 🎯 수정 대상 파일

| 파일 | 현재 상태 | 문제점 |
|------|---------|-------|
| `frontend-rn/api/auth.js` | ✅ 로그인 함수만 존재 | JWT 갱신 함수 없음 |
| `frontend-rn/app/(auth)/login.jsx` | ✅ 토큰 저장만 수행 | 만료 감지 및 재발급 로직 없음 |
| `backend/app/services/auth.py` | ⚠️ 토큰 생성만 구현 | 토큰 검증 및 갱신 엔드포인트 없음 |
| `backend/app/api/v1/endpoints/auth.py` | ❌ 갱신 엔드포인트 없음 | POST /api/v1/auth/refresh 필요 |
| `frontend-rn/api/axiosInstance.js` | 📍 컨텍스트 미제공 | **인터셉터 추가 필요** (만료 감지) |

---

## ⚠️ 예상 영향도

### **HIGH RISK** - 아래 변경 필요
1. **Backend 토큰 검증 함수** 추가
   - `_verify_token()` 함수 필요 (JWT 검증 및 만료 확인)
   - `_refresh_token

---

### [R-T1] auth 로그인 JWT 만료 처리 수정해줘 — sonnet

선택 파일: frontend-rn/api/auth.js, backend/app/schemas/auth.py, backend/app/services/auth.py, frontend-rn/app/(auth)/login.jsx

**CC 응답** (3/3)

## 분석 결과 — 적용 전 검토 요청

---

### 🔍 먼저 확인이 필요한 사항

**"JWT 만료 처리"** 가 정확히 어떤 증상/문제인지 컨텍스트에 명시되어 있지 않습니다.
아래 두 가지 시나리오 중 어느 것을 의도하신 건지 확인이 필요합니다.

| # | 시나리오 | 해당 레이어 |
|---|----------|------------|
| A | 토큰이 만료됐을 때 **프론트엔드에서 자동 로그아웃 / 에러 처리** 가 안 됨 | 프론트엔드 |
| B | 백엔드에서 **만료된 토큰을 검증할 때 예외 처리** 가 누락되어 있음 | 백엔드 |
| C | **만료 시간 설정(`JWT_EXPIRE_HOURS`)** 자체를 바꾸고 싶음 | 백엔드 설정 |

---

### 📂 수정 후보 파일 (컨텍스트 내 존재하는 것만)

| 파일 | 역할 | 수정 가능 여부 |
|------|------|--------------|
| `frontend-rn/api/auth.js` | 로그인 API 호출 | ✅ 낮은 위험 |
| `frontend-rn/app/(auth)/login.jsx` | 로그인 화면 / 토큰 저장 | ✅ 낮은 위험 |
| `backend/app/services/auth.py` | JWT 생성 / 만료 설정 | ⚠

---

### [R-T2] docker-compose.yml 배포 설정 알려줘 — haiku

선택 파일: .claude/settings.json, .vscode/settings.json, backend/docker-compose.yml, .github/workflows/deploy.yml

**CC 응답** (2/3)

# docker-compose.yml 배포 설정 분석

## 📋 현재 설정 요약

**파일**: `backend/docker-compose.yml` (54줄)

### 구성 서비스
| 서비스 | 이미지 | 포트 | 상태 |
|--------|--------|------|------|
| **mongo** | mongo:7 | 127.0.0.1:27017 | healthcheck ✓ |
| **redis** | redis:7-alpine | 127.0.0.1:6379 | healthcheck ✓ |
| **backend** | Custom Dockerfile | 8000:8000 | depends_on both |

---

## 🔍 설정 상세 분석

### 1️⃣ MongoDB (mongo_data 볼륨)
```yaml
healthcheck:
  test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
  interval: 10s / timeout: 5s / retries: 5
```
- **로컬 바인드**: `127.0.0.1:27017` (localhost 전용)
- **헬스체크**: mongosh 명령어로 연결 검증
- **재시작 정책**: `always`

### 2️⃣ Redis (휘발성)
```yaml
healthcheck:
  test: ["CMD", "redis-cli", "ping"]
```
- **로컬 바인드**: `127.0.0.1:6379` (localhost 전용)
- **캐시용**: 영구 볼륨 없음 (의도적)
- **재시작**: `always`

### 3️⃣ Backend 앱
```yaml
env_file: ../.env  # 외부 환경변수
environment:
  MONGO_URI: mongodb://rainbow_mongo:27017
  REDIS_URL: redis://rainbow_redis:6379
volumes:
  - ../uploads:/app/backend

---

### [R-T2] docker-compose.yml 배포 설정 알려줘 — sonnet

선택 파일: .claude/settings.json, .vscode/settings.json, backend/docker-compose.yml, .github/workflows/deploy.yml

**CC 응답** (3/3)

# `docker-compose.yml` 배포 설정 분석

> **읽기 전용 분석**입니다. 수정 제안 없이 현재 설정을 설명합니다.

---

## 📄 대상 파일

- `backend/docker-compose.yml` (컨텍스트 [3])
- `.github/workflows/deploy.yml` (컨텍스트 [4], CI/CD 연동)

---

## 🐳 `backend/docker-compose.yml` 구성 요약

### 전체 구조

```
name: backend
services:
  ├── mongo        (MongoDB 7)
  ├── redis        (Redis 7 Alpine)
  └── backend      (FastAPI 앱)
volumes:
  ├── mongo_data
  └── sqlite_data
```

---

### 서비스별 상세

#### 1. `mongo`
| 항목 | 값 |
|---|---|
| 이미지 | `mongo:7` |
| 컨테이너명 | `rainbow_mongo` |
| 포트 | `127.0.0.1:27017:27017` (로컬호스트만 노출) |
| 볼륨 | `mongo_data:/data/db` (named volume, 영속) |
| 재시작 | `always` |
| 헬스체크 | `mongosh --eval db.adminCommand('ping')` / 10s 간격 / 5회 재시도 |

#### 2. `redis`
| 항목 | 값 |
|---|---|
| 이미지 | `redis:7-alpine` |
| 컨테이너명 | `rainbow_redis` |
| 포트 | `127.0.0.1:6379:6379` (로컬호스트만 노출) |
| 재시작 | `always` |
| 헬스체

---

### [R-T3] users 테이블 마이그레이션 추가해줘 — haiku

선택 파일: backend/app/models/user.py, docs/devlog/members/김윤한.md, docs/devlog/members/반소람.md, backend/app/api/v1/endpoints/pets.py

**CC 응답** (2/3)

# 분석 결과: users 테이블 마이그레이션

## 📋 작업 범위 확인
요청: **users 테이블 마이그레이션 추가**
- 범위가 명확하지 않습니다. 다음 중 어느 것을 의도하셨나요?
  1. **신규 마이그레이션 파일 생성** (Alembic으로 users 테이블 생성)
  2. **기존 마이그레이션에 users 추가**
  3. **User 모델 변경 후 마이그레이션 생성**

---

## 🔍 현재 상태 분석

### 1️⃣ 수정 대상 파일
```
backend/app/models/user.py          (SQLAlchemy ORM 모델 - 기존)
backend/alembic/versions/*.py       (마이그레이션 파일 - 없음 또는 부분)
backend/alembic/env.py              (마이그레이션 설정 - 확인 필요)
```

### 2️⃣ 예상 영향도

| 영역 | 영향 | 심각도 |
|------|------|--------|
| **DB Schema** | users 테이블 생성/수정 | 🔴 높음 |
| **인증 로직** | `backend/app/services/auth.py`의 User 쿼리 | 🟡 중간 |
| **마이그레이션 체인** | 기존 마이그레이션이 있으면 conflicts 가능 | 🟡 중간 |
| **배포** | 운영 DB에 적용 필요 (NCP 배포 영향) | 🔴 높음 |
| **기타 모델** | Pet

---

### [R-T3] users 테이블 마이그레이션 추가해줘 — sonnet

선택 파일: backend/app/models/user.py, docs/devlog/members/김윤한.md, docs/devlog/members/반소람.md, backend/app/api/v1/endpoints/pets.py

**CC 응답** (2/3)

## 분석 결과

### 1. 수정 대상 파일 (신규 생성)

| 파일 | 작업 |
|------|------|
| `backend/alembic/versions/xxxx_create_users_table.py` | 신규 생성 (마이그레이션 파일) |

> **참고**: `alembic/` 디렉터리 및 `alembic.ini` 존재 여부가 컨텍스트에 없습니다.  
> Alembic이 아직 초기화되지 않았다면 `alembic init` 단계가 선행되어야 합니다.  
> 확인이 필요합니다.

---

### 2. 근거 — User 모델 스키마 파악

컨텍스트 `[1] backend/app/models/user.py` 기준:

| 컬럼 | 타입 | 제약 |
|------|------|------|
| `id` | INTEGER | PK, AUTO INCREMENT |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL, INDEX |
| `password_hash` | VARCHAR(255) | NOT NULL |
| `nickname` | VARCHAR(50) | NOT NULL |
| `is_active` | BOOLEAN | DEFAULT TRUE |
| `created_at` | DATETIME(timezone) | DEFAULT UTC NOW |

---

### 3. 예상 영향도

| 항목 | 수준 | 설명 |
|------|------|------|
| DB 스키마 변경 | **MEDIUM** | `users` 테이블 신규 생성. 기존 테이블 없으면 무해하지만, 이미 테이블이 존재하는 환경(운영 DB)에서 실행 시 충돌 가능 |
| 인증/권한 로직 | **LOW** | `auth

---

