# Raw vs Context Capsule — 전체 비교

**날짜**: 2026-06-29  
**모델**: claude-haiku-4-5-20251001, claude-sonnet-4-6

## 요약

| 레포 | ID | 태스크 | 모델 | Raw토큰 | CC토큰 | 절감 | Raw점수 | CC점수 |
|---|---|---|---|---|---|---|---|---|
| dummy-repo | D-T1 | auth_service 500 에러  | haiku | ~4,468 | ~2,406 | 46.2% | 3/3 | 3/3 |
| dummy-repo | D-T1 | auth_service 500 에러  | sonnet | ~4,468 | ~2,406 | 46.2% | 3/3 | 3/3 |
| dummy-repo | D-T2 | 결제 실패 고쳐줘 | haiku | ~4,468 | ~2,258 | 49.5% | 3/3 | 3/3 |
| dummy-repo | D-T2 | 결제 실패 고쳐줘 | sonnet | ~4,468 | ~2,258 | 49.5% | 3/3 | 3/3 |
| dummy-repo | D-T3 | 로그인 안돼 | haiku | ~4,468 | ~2,561 | 42.7% | 0/3 | 3/3 |
| dummy-repo | D-T3 | 로그인 안돼 | sonnet | ~4,468 | ~2,561 | 42.7% | 0/3 | 3/3 |
| procurement-logistics-ai | P-T1 | ML 모델 정확도가 몇 %야? | haiku | ~107,524 | ~2,732 | 97.5% | 0/4 | 1/4 |
| procurement-logistics-ai | P-T1 | ML 모델 정확도가 몇 %야? | haiku | ~107,524 | ~2,732 | 97.5% | CC only | 1/4 |
| procurement-logistics-ai | P-T1 | ML 모델 정확도가 몇 %야? | sonnet | ~107,524 | ~2,732 | 97.5% | CC only | 2/4 |
| procurement-logistics-ai | P-T2 | QA 리포트에 나온 성능 수치 알려줘 | haiku | ~107,524 | ~2,751 | 97.4% | 0/4 | 3/4 |
| procurement-logistics-ai | P-T2 | QA 리포트에 나온 성능 수치 알려줘 | haiku | ~107,524 | ~2,751 | 97.4% | CC only | 3/4 |
| procurement-logistics-ai | P-T2 | QA 리포트에 나온 성능 수치 알려줘 | sonnet | ~107,524 | ~2,751 | 97.4% | CC only | 3/4 |
| procurement-logistics-ai | P-T3 | 프로젝트 모델 성능 요약해줘 | haiku | ~107,524 | ~2,723 | 97.5% | 0/4 | 3/4 |
| procurement-logistics-ai | P-T3 | 프로젝트 모델 성능 요약해줘 | haiku | ~107,524 | ~2,723 | 97.5% | CC only | 3/4 |
| procurement-logistics-ai | P-T3 | 프로젝트 모델 성능 요약해줘 | sonnet | ~107,524 | ~2,723 | 97.5% | CC only | 3/4 |
| rainbow-bridge | R-T1 | auth 로그인 JWT 만료 처리 수 | haiku | - | ~2,195 | 0% | CC only | 3/3 |
| rainbow-bridge | R-T1 | auth 로그인 JWT 만료 처리 수 | sonnet | - | ~2,195 | 0% | CC only | 3/3 |
| rainbow-bridge | R-T2 | docker-compose.yml 배 | haiku | - | ~2,374 | 0% | CC only | 3/3 |
| rainbow-bridge | R-T2 | docker-compose.yml 배 | sonnet | - | ~2,374 | 0% | CC only | 3/3 |
| rainbow-bridge | R-T3 | users 테이블 마이그레이션 추가해 | haiku | - | ~2,750 | 0% | CC only | 3/3 |
| rainbow-bridge | R-T3 | users 테이블 마이그레이션 추가해 | sonnet | - | ~2,750 | 0% | CC only | 3/3 |

---

## 상세 응답

### [D-T1] auth_service 500 에러 고쳐줘 — haiku

선택 파일: src/services/auth_service.py, src/services/payment_service.py, src/services/notification_service.py, src/utils/cache.py

**Raw 응답** (3/3)

# auth_service 500 에러 분석 및 해결방안

## 🔴 문제 원인

### 파일: `src/services/auth_service.py` - `decode_token()` 함수

```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

**만료되거나 유효하지 않은 JWT 토큰**이 들어오면 `JWTError`가 발생하는데, 이를 처리하지 않아 **핸들링되지 않은 예외 → 500 에러**로 응답됩니다.

---

## 🔗 연쇄 영향

### 파일: `src/api/routes/users.py` - `get_current_user()` 함수

```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # decode_token이 JWTError를 안 잡아서 만료 토큰 → 500 터짐
    payload = decode_token(token)  # ❌ 여기서 예외 발생
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

`decode_token()`에서 발생한 예외가 잡히지 않으면서, 엔드포인트에 `401 Unauthorized`를 반환해야 하는 상황에서 **500 Internal Server Error**를 반환하게

**CC 응답** (3/3)

# 분석 결과: auth_service 500 에러

## 📋 문제 진단

**근본 원인**: `src/services/auth_service.py`의 `decode_token()` 함수가 JWT 예외를 처리하지 않음

```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

만료되거나 유효하지 않은 토큰 → `JWTError` 발생 → 핸들링 없음 → 500 Internal Server Error

이는 `src/api/routes/users.py`의 `get_current_user()` 의존성에서 호출될 때 발생:
```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_token(token)  # ← 여기서 500 터짐
```

---

## 🎯 수정 대상 파일

1. **`src/services/auth_service.py`** (필수 수정)
2. **`src/api/routes/users.py`** (의존성 함수 에러 처리 강화)

---

## ⚠️ 예상 영향도

| 영향 범위 | 심각도 | 설명 |
|---------|--------|------|
| **API 응답 상태 코드** | 🔴 HIGH | 인증 실패 시 500 → **401 Unauthorized** 로 변경 |
| **클라이언트 동작** | 🟡 MEDIUM | 401 에러 처리 로직 검증 필요 (토큰 갱신

---

### [D-T1] auth_service 500 에러 고쳐줘 — sonnet

선택 파일: src/services/auth_service.py, src/services/payment_service.py, src/services/notification_service.py, src/utils/cache.py

**Raw 응답** (3/3)

## 원인 분석

### 문제 파일: `src/services/auth_service.py` + `src/api/routes/users.py`

**핵심 원인:** `decode_token()`이 `JWTError`를 전혀 잡지 않아서, 만료/변조된 토큰이 들어오면 예외가 그대로 위로 전파되어 FastAPI가 500으로 처리합니다.

```python
# auth_service.py - 현재 코드
def decode_token(token: str) -> dict:
    # JWTError를 잡지 않음 → 만료 토큰 시 ExpiredSignatureError 발생
    # FastAPI가 처리 못하고 → 500 Internal Server Error
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

`jose`의 예외 계층은 아래와 같습니다.
- `ExpiredSignatureError` (토큰 만료) ← 가장 흔한 케이스
- `JWTClaimsError` (클레임 검증 실패)
- `JWTError` (위 둘의 부모, 변조/형식 오류 포함)

---

## 수정 코드

### `src/services/auth_service.py`

```python
from datetime import datetime, timedelta
from jose import JWTError, ExpiredSignatureError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from src.db.models import User
from src.config.settings import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed

**CC 응답** (3/3)

## 분석 결과

### 🔍 버그 원인 확인

**이슈 #61** 과 일치하는 버그입니다. 원인은 두 파일에 걸쳐 있습니다.

---

### 📁 수정 대상 파일

| 파일 | 위치 | 문제 |
|------|------|------|
| `src/services/auth_service.py` | `decode_token()` 함수 | `JWTError` 미처리 → 500 발생 |
| `src/api/routes/users.py` | `get_current_user()` 함수 | `decode_token()` 호출 시 예외 미처리 → 500 전파 |

---

### 🐛 구체적 문제

**[1] `auth_service.py` — `decode_token()`**

```python
# 현재 (문제)
def decode_token(token: str) -> dict:
    # JWTError를 잡지 않아서 만료/위조 토큰 → 500 에러
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

`jwt.decode()`는 만료(`ExpiredSignatureError`)·서명 불일치·형식 오류 시
`JWTError`(또는 하위 예외)를 던집니다. 이게 아무것도 잡히지 않고 그대로 올라가면 FastAPI가 500으로 응답합니다.

**[2] `users.py` — `get_current_user()`**

```python
# 현재 (문제)
def get_current_user(...):
    payload = decode_token(token)   # JWTError 터지면 500 전파
    ...
```

`decode_token()`이 예외를 던져도 여

---

### [D-T2] 결제 실패 고쳐줘 — haiku

선택 파일: src/services/payment_service.py, src/services/notification_service.py, README.md, src/utils/cache.py

**Raw 응답** (3/3)

# 결제 실패 문제 분석 및 해결방안

## 🔴 문제점 분석

README의 이슈 `#58`에 명시되어 있듯이, **결제 실패 시 재시도 로직이 없습니다**. 현재 구조의 문제점:

### 1. **단일 시도 후 즉시 실패 처리** (`src/services/payment_service.py`)
```python
def process_order_payment(db: Session, order_id: int, card_token: str) -> Order:
    # ...
    try:
        result = charge_payment(order_id, order.total_amount, card_token)
        order.status = "paid"
        order.payment_id = result.get("payment_id")
    except RuntimeError:
        order.status = "failed"  # ❌ 재시도 없이 즉시 실패
```

### 2. **JWT 토큰 만료 시 500 에러** (`src/services/auth_service.py`)
```python
def decode_token(token: str) -> dict:
    # ❌ JWTError를 catch하지 않음 → 만료/유효하지 않은 토큰 → 500 에러
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

### 3. **주문 생성 후 결제 실패 시 원자성 문제** (`src/api/routes/orders.py`)
```python
# 주문이 이미 DB에 저장되고 재고 감소됨
db.commit()
db.refresh(order)

# 여기서 결제 실패 → 주문은 pending 상태로 남음
order = process_order_payment(db, order.id, body.card_token)
```

---

## ✅ 해결방안

### **

**CC 응답** (3/3)

# 결제 실패 문제 분석

## 📋 작업 범위 확인
요청: **"결제 실패 고쳐줘"** (불명확한 요청)
- 증상이나 구체적 오류가 명시되지 않음
- README.md의 `#58` 이슈와 연관된 것으로 추정

---

## 🔍 발견된 결제 관련 문제들

### 1. **재시도 로직 부재** (README #58)
- `src/services/payment_service.py`의 `charge_payment()` 함수는 실패 시 즉시 에러 발생
- `MAX_RETRY_COUNT`, `RETRY_DELAY_SECONDS` 설정이 있지만 **사용되지 않음**
- 타임아웃/네트워크 오류에 취약

### 2. **불완전한 코드**
- `payment_service.py` 66줄에서 `refund_payment()` 함수가 잘려있음
- `notification_service.py` 43줄에서 `notify_order_failed()` 함수가 잘려있음
- `orders.py` 80줄에서 라우트 구현이 잘려있음

### 3. **결제 프로세스 호출 불명확**
- `orders.py`에서 `process_order_payment()`를 호출하지만 함수 정의를 찾을 수 없음
- 실제 결제 흐름이 어떻게 동작하는지 불명확

---

## 📊 수정 대상 파일 및 영향도

| 파일 | 변경 유형 | 영향도 | 위험도 |
|------|---------|--------|--------|
| `src/services/payment

---

### [D-T2] 결제 실패 고쳐줘 — sonnet

선택 파일: src/services/payment_service.py, src/services/notification_service.py, README.md, src/utils/cache.py

**Raw 응답** (3/3)

# 결제 실패 재시도 로직 수정

## 문제 분석

README 이슈 `#58`에 명시된 **"결제 실패 시 재시도 로직 없음"** 문제입니다.

### 원인이 되는 코드

**`src/services/payment_service.py` — `process_order_payment()`**
```python
# 재시도 로직 없음 — 한 번 실패하면 바로 failed 처리
try:
    result = charge_payment(order_id, order.total_amount, card_token)
    order.status = "paid"
    order.payment_id = result.get("payment_id")
except RuntimeError:
    order.status = "failed"   # 한 번 실패하면 즉시 failed
```

**`src/api/routes/orders.py`**
```python
# 결제 처리 (재시도 없음)
order = process_order_payment(db, order.id, body.card_token)
```

네트워크 순단, 결제 서버 일시적 과부하 등 **일시적 오류(transient error)** 임에도
재시도 없이 즉시 `failed` 처리되고 재고도 돌아오지 않는 이중 문제가 있습니다.

### 추가로 발견한 연계 버그

`process_order_payment` 실패 시 **차감된 재고가 복구되지 않습니다.**
`orders.py`에서 재고를 먼저 차감하고 `db.commit()` 후 결제를 시도하는데,
결제가 `failed`로 끝나도 재고를 원복하는 코드가 없습니다.

---

## 수정 코드

### `src/services/payment_service.

**CC 응답** (3/3)

# 결제 실패 분석 보고서

## 1. 문제 파악

"결제 실패"는 요청이 너무 광범위합니다. 컨텍스트 분석 결과 **두 가지 독립적인 문제**가 확인됩니다.

---

## 2. 확인된 문제 목록

### 문제 A — 재시도 로직 없음 (README 이슈 #58) ★ 주요
```
payment_service.py: 타임아웃/HTTP 오류 발생 시 즉시 RuntimeError 발생
→ 일시적 네트워크 오류에도 결제가 바로 실패 처리됨
```

### 문제 B — `process_order_payment` 함수 미존재 (Import 오류)
```python
# orders.py Line 7
from src.services.payment_service import process_order_payment
# ↑ payment_service.py에는 charge_payment 만 있음
#   process_order_payment 는 정의되어 있지 않음
# → 서버 기동 시 또는 첫 호출 시 ImportError 발생 가능
```

---

## 3. 수정 후보 파일

| 파일 | 수정 이유 | 위험도 |
|---|---|---|
| `src/services/payment_service.py` | 재시도 로직 추가 + `process_order_payment` 함수 추가 | **MEDIUM** |
| `src/api/routes/orders.py` | import 경로는 유지 (함수명 맞춰줌) | LOW |

---

## 4. 예상 영향도

### 문제 B (ImportError) 수정 영향
- `orders.py`가 현재 `process_order_

---

### [D-T3] 로그인 안돼 — haiku

선택 파일: src/services/payment_service.py, src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py

**Raw 응답** (0/3)

# 로그인 불가 문제 분석

## 🔴 핵심 원인

**`src/api/routes/users.py`의 `login` 엔드포인트에서 `OAuth2PasswordRequestForm`을 사용하고 있는데, 클라이언트가 JSON으로 요청하면 작동하지 않습니다.**

### 문제 코드
```python
@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form.username, form.password)  # ← form.username 기대
    ...
```

**`OAuth2PasswordRequestForm`은 `application/x-www-form-urlencoded` 형식만 지원합니다.**

---

## 📋 상세 분석

### 1️⃣ 클라이언트 요청 형식

**❌ 안 되는 방식 (JSON)**
```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "123456"}'
```

**✅ 되는 방식 (Form Data)**
```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=123456"
```

---

## 🔧 해결 방안

### **방법 1: JSON 요청 지원 (권장)**

**`src/api/routes/users.py` 수정**

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from src.db.database import get

**CC 응답** (3/3)

# 분석 결과: "로그인 안돼" 문제

## 📋 수정 대상 파일
1. `src/services/auth_service.py` - `decode_token()` 함수
2. `src/api/routes/users.py` - `get_current_user()` 함수

---

## 🔍 문제 진단

**근본 원인: JWT 토큰 만료 시 500 에러 발생**

### 현재 동작 흐름
```
사용자 로그인 요청 → 토큰 발급 ✅
토큰 사용 (만료됨) → decode_token() 호출
  ↓
JWTError 미처리 → 예외 발생 → 500 Internal Server Error ❌
  (401 Unauthorized 이어야 함)
```

### 코드 문제점

**[src/services/auth_service.py - line 26-28]**
```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```
✗ `JWTError`, `ExpiredSignatureError` 예외를 처리하지 않음

**[src/api/routes/users.py - line 30-32]**
```python
def get_current_user(token: str = Depends(oauth2_scheme), ...):
    # decode_token이 JWTError를 안 잡아서 만료 토큰 → 500 터짐
    payload = decode_token(token)
```
✗ 상위 함수도 예외 처리 없음

---

## 📊 예상 영향도

| 항목 | 영향도 | 설

---

### [D-T3] 로그인 안돼 — sonnet

선택 파일: src/services/payment_service.py, src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py

**Raw 응답** (0/3)

# 로그인 안 되는 문제 분석

## 가능한 원인 목록 (확률 순)

---

## 1순위 — DB 테이블이 없음 (가장 흔한 원인)

### 원인
`src/db/database.py`와 `src/db/models.py`를 봤을 때 **테이블 자동 생성 코드가 없습니다.**

```python
# src/db/database.py — 현재 코드
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

`Base.metadata.create_all()` 호출도 없고, alembic 마이그레이션을 돌렸다는 근거도 없습니다.  
→ `users` 테이블 자체가 없으면 `/users/register`도, `/users/login`도 전부 **500** 납니다.

### 확인 방법
```bash
# 서버 로그에서 아래와 같은 에러 확인
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.UndefinedTable) 
  relation "users" does not exist
```

### 해결
```bash
# alembic 쓰는 경우
alembic upgrade head

# 빠른 로컬 테스트용 (임시)
# src/db/database.py 맨 아래에 추가
from src.db.models import Base
Base.metadata.create_all(bind=engine)
```

---

## 2순위 — `.env` 파일 없음 / DATABASE_URL 연결 실패

### 원인
```bash
cp .env.example .env  # README에는 있지만 실제로 안 했을 가능성
```

`.env`가 없으면 `settings

**CC 응답** (3/3)

# 로그인 안 되는 문제 분석

## 1. 원인 파악

"로그인 안 됨"이라는 증상에 대해 컨텍스트를 분석한 결과, **확인된 버그가 2개** 있습니다.

---

### 🔴 버그 A — 만료된 JWT 토큰 → 500 에러 (이슈 #61)

**위치:** `src/services/auth_service.py` L27-29

```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

- `jwt.decode()`는 토큰 만료 시 `JWTError`를 raise하는데, 이를 잡지 않음
- 결과적으로 FastAPI가 처리하지 못한 예외로 **500 Internal Server Error** 반환
- 정상 동작이면 **401 Unauthorized**를 반환해야 함
- `src/api/routes/users.py` L31의 `get_current_user`도 같은 이유로 영향받음

---

### 🟡 버그 B — `authenticate_user` 함수 코드가 잘림

**위치:** `src/services/auth_service.py` L34-35 (컨텍스트 잘림)

```python
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hash  ← 여기서 잘림
```

- `user.hash` 뒤가

---

### [P-T1] ML 모델 정확도가 몇 %야? — haiku

선택 파일: docs/data_dictionary.md, docs/numbers_reference.md, docs/score_model.md, docs/presentation_script.md

**Raw 응답** (0/4)

[ERROR] Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'prompt is too long: 219016 tokens > 200000 maximum'}, 'request_id': 'req_011CcWi5WWjGhe7yYLxviqkB'}

**CC 응답** (1/4)

# ML 모델 정확도 분석

## 📋 요청 범위 확인
**질문**: ML 모델 정확도가 몇 %야?  
**작업 범위**: 제공된 컨텍스트 내에서 정확도 수치 검색 및 검증

---

## 🔍 발견된 정확도 수치

컨텍스트에서 **3개의 정확도 수치**가 발견되었습니다:

| 출처 파일 | 수치 | 설명 | 신뢰도 |
|---|---|---|---|
| `docs/numbers_reference.md:68` | **98%** | ML 품목 분류기 / 홀드아웃 테스트셋 14,070건 기준 | ✅ 기준명시 |
| `docs/rubric_alignment.md:34` | **98.6%** | TF-IDF + LogReg / 홀드아웃 방식 | ✅ 기준명시 |
| `check.md:430` | **98.58%** | 검증 정확도 / 86,991건 훈련 데이터 | ⚠️ 주의사항 있음 |

---

## ⚠️ 수치 불일치 분석

### 문제점
- **98% vs 98.6% vs 98.58%** — 세 값이 서로 다름
- 같은 모델을 다른 기준으로 측정했거나, 모델 버전이 다를 가능성

### 각 수치의 맥락

**① 98% (numbers_reference.md)**
```
출처: src/modeling/train_classifier.py
기준: 홀드아웃 테스트셋 14,070건
용도: 공식 발표

---

### [P-T1] ML 모델 정확도가 몇 %야? — haiku

선택 파일: docs/data_dictionary.md, docs/numbers_reference.md, docs/score_model.md, docs/presentation_script.md

**CC 응답** (1/4)

# 분석 결과

## 작업 요청 해석
**"ML 모델 정확도가 몇 %야?"** → 제공된 컨텍스트에서 ML 성능 수치 조회

---

## 발견된 수치

관련 컨텍스트에서 **ML 분류기 정확도**에 대해 **2가지 상이한 값**이 보고되고 있습니다:

| 출처 | 정확도 | 측정 방식 | 설명 |
|---|---|---|---|
| **docs/numbers_reference.md** | **98%** | 홀드아웃 테스트셋 14,070건 | "ML 품목 분류기 정확도" |
| **check.md** (분류기 상세) | **98.58%** | 검증 정확도 (Validation Accuracy) | TF-IDF + LogReg, 훈련 레이블 재현율 |
| **docs/rubric_alignment.md** | **98.6%** | (같은 모델 참조) | 기술성 평가 근거 |

---

## ⚠️ 주의: 수치 불일치 감지

**check.md의 위험 신호:**
```
MEDIUM risk: 문서 간 수치 값이 서로 달라 확인 필요
- 98% (numbers_reference.md)
- 98.58% (check.md)  
- 98.6% (rubric_alignment.md)
```

---

## 답변

### 공식 보고 수치
**98%** (numbers_reference.md 기준)
- 측정 기준: 홀드아웃 테스트셋 14,070건
- 출처: `src/modeling/train_classifier.py`

### 상세 기술 수치

---

### [P-T1] ML 모델 정확도가 몇 %야? — sonnet

선택 파일: docs/data_dictionary.md, docs/numbers_reference.md, docs/score_model.md, docs/presentation_script.md

**CC 응답** (2/4)

## ML 모델 정확도 답변

컨텍스트 문서들을 분석한 결과, **수치가 문서마다 미세하게 다릅니다.** 정리해 드립니다.

---

### 📊 문서별 수치 비교

| 출처 문서 | 기재 수치 | 비고 |
|---|---|---|
| `docs/numbers_reference.md` | **98%** | "홀드아웃 테스트셋 14,070건 기준" |
| `docs/presentation_script.md` | **98.08%** | 발표 대본 슬라이드 6 |
| `docs/rubric_alignment.md` | **98.6%** | 심사 Q&A 대비 자료 |
| `check.md` | **98.58%** | 훈련 결과 상세 테이블, "검증 정확도" |

---

### ⚠️ 주의해야 할 맥락

`check.md`에 아래 경고가 명시되어 있습니다:

> *"검증 정확도 98.58%는 훈련 레이블 자체가 키워드 규칙 결과이므로 **'규칙 재현율'에 가까움**"*
> *"발표/README에는 수치보다 구조(3단계 fallback)를 강조하는 것이 적합"*

즉, **98.58%는 독립적인 정답 레이블 기준이 아니라, 키워드 규칙이 만든 레이블을 얼마나 잘 재현하는지를 측정한 수치**입니다.

---

### ✅ 요약

- **대외 발표용 공식 수치:** `98%` 

---

### [P-T2] QA 리포트에 나온 성능 수치 알려줘 — haiku

선택 파일: docs/numbers_reference.md, docs/data_dictionary.md, docs/score_model.md, docs/slides_ppt_content.md

**Raw 응답** (0/4)

[ERROR] Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'prompt is too long: 219016 tokens > 200000 maximum'}, 'request_id': 'req_011CcWi7RVR37RsJFCX51FKn'}

**CC 응답** (3/4)

# QA 리포트 성능 수치 분석

## 📋 요청 범위 확인
사용자 요청: **"QA 리포트에 나온 성능 수치 알려줘"**

제공된 컨텍스트에서 **QA 리포트 문서 없음**을 확인했습니다.
대신 성능 관련 수치가 포함된 참고 문서들을 발견했으므로 아래와 같이 정리하겠습니다.

---

## 🔍 수집된 성능 수치 (컨텍스트 기반)

### 1️⃣ **ML 모델 성능**
| 지표 | 수치 | 출처 | 설명 |
|------|------|------|------|
| 품목 분류기 정확도 | **98%** | `docs/numbers_reference.md` | TF-IDF + Logistic Regression 모델 / 홀드아웃 테스트셋 14,070건 기준 |
| 정확도 (상세) | **98.08%** | `docs/presentation_script.md` | 동일 모델의 더 정밀한 수치 |

### 2️⃣ **데이터 수집 성능**
| 지표 | 수치 | 출처 | 설명 |
|------|------|------|------|
| 전국 입찰공고 처리 | **100,083건** | `docs/numbers_reference.md` | 전처리 완료 기준 (최근 2년) |
| Feature table 집계 | **72,103건** | `docs/numbers_reference.md` | district × item_category 교차집계 |
| 시군구 커버리지 | **205개** | `docs/numbers_reference

---

### [P-T2] QA 리포트에 나온 성능 수치 알려줘 — haiku

선택 파일: docs/numbers_reference.md, docs/data_dictionary.md, docs/score_model.md, docs/slides_ppt_content.md

**CC 응답** (3/4)

# 분석 결과: QA 리포트 성능 수치

## 📋 작업 범위 확인
사용자 요청: **"QA 리포트에 나온 성능 수치 알려줘"**

✅ 작업 범위 내 (문서 검토 및 수치 제시만 해당 - 코드 수정 불포함)

---

## 🔍 제공 컨텍스트에서 추출된 성능 수치

### 1️⃣ **ML 품목 분류기 정확도**
- **98%** (정확히: 98.08%)
- 테스트 기준: 홀드아웃 테스트셋 14,070건
- 모델: TF-IDF + Logistic Regression
- 출처: `src/modeling/train_classifier.py` (docs/numbers_reference.md)

### 2️⃣ **데이터 수집 완성도**

| 항목 | 수치 | 기준 |
|------|------|------|
| 전국 입찰공고 | 100,083건 | 전국 / 전 품목 / 최근 2년 / 전처리 완료 |
| 공고 수집 지역 | 205개 | 공고 1건 이상 시군구 수 |
| 소상공인 상가정보 | 231개 지역 | 소상공인 API 지원 지역 |
| 목표 수집 지역 | 253개 | 전국 255개 중 99.2% |
| 물류창고 등록정보 | 5,911개소 | 국토부 기준 |

### 3️⃣ **aT(학교급식) 데이터 수집**
- BID(

---

### [P-T2] QA 리포트에 나온 성능 수치 알려줘 — sonnet

선택 파일: docs/numbers_reference.md, docs/data_dictionary.md, docs/score_model.md, docs/slides_ppt_content.md

**CC 응답** (3/4)

## QA 리포트 성능 수치 정리

제공된 컨텍스트에서 **"QA 리포트"라는 별도 문서는 확인되지 않습니다.**

다만, 관련 컨텍스트 내에서 성능(품질/정확도) 관련 수치로 볼 수 있는 항목들을 아래에 정리합니다.

---

### 확인된 성능 수치

| 수치 | 항목 | 출처 컨텍스트 |
|---|---|---|
| **98%** (98.08%) | ML 품목 분류기 정확도 (홀드아웃 테스트셋 14,070건 기준) | `docs/numbers_reference.md`, `docs/presentation_script.md` |

---

### 함께 확인된 데이터 규모 수치 (참고용)

| 수치 | 항목 |
|---|---|
| **100,083건** | 전국 나라장터 입찰공고 전체 |
| **72,103건** | feature_table 집계 bid_count 합계 |
| **205개** | 공고 수집 완료 시군구 |
| **253개** | 전국 수집 대상 목표 시군구 |

---

### ⚠️ 주의사항

1. **"QA 리포트"라는 파일이 컨텍스트에 없습니다.** 별도의 QA 리포트 파일(`qa_report.md` 등)이 있다면 해당 파일을 공유해 주셔야 정확한 수치를 확인할 수 있습니다.

2. **위험 신호로 등록된 항목이 있습니다.**
   - `

---

### [P-T3] 프로젝트 모델 성능 요약해줘 — haiku

선택 파일: docs/data_dictionary.md, docs/score_model.md, docs/numbers_reference.md, src/features/build_opportunity_matrix.py

**Raw 응답** (0/4)

[ERROR] Error code: 400 - {'type': 'error', 'error': {'type': 'invalid_request_error', 'message': 'prompt is too long: 219016 tokens > 200000 maximum'}, 'request_id': 'req_011CcWi95skxwcGqnKyuiVJ2'}

**CC 응답** (3/4)

# 프로젝트 모델 성능 분석

작업 범위 확인: **요청은 "모델 성능 요약"**이며, 코드 수정 없이 **분석만** 수행합니다.

---

## 📊 현재 문서에서 확인된 성능 지표

### 1. **ML 품목 분류 모델**
| 지표 | 값 | 출처 |
|---|---|---|
| 모델 유형 | TF-IDF + Logistic Regression | docs/presentation_script.md:81-160 |
| 정확도(Accuracy) | **98.08%** | docs/numbers_reference.md:72 |
| 테스트셋 규모 | 14,070건 | docs/numbers_reference.md:72 |
| 품목군 분류 클래스 | 18개 | docs/presentation_script.md:86 |

### 2. **점수 모델 성능**
| 컴포넌트 | 설명 | 상태 |
|---|---|---|
| opportunity_score | 4개 지표 가중합 (count 40% + amount 25% + recency 15% + competition 20%) | ✅ 공식 정의됨 |
| adjusted_score | opportunity_score × 생존율 보정 | ✅ 공식 정의됨 |
| hub_score | 물류 거점 점수 (부분 문서) | ⚠️ 설명 불완전 |
| anomaly 탐지 | Isolation Forest 수요공백 검출 | ✅ 구현됨 |

### 3. **데이터 품질 지표**
| 항목 | 값 | 평가 |
|---|---|---|
| 입찰공고 수집(나라장터) | 

---

### [P-T3] 프로젝트 모델 성능 요약해줘 — haiku

선택 파일: docs/data_dictionary.md, docs/score_model.md, docs/numbers_reference.md, src/features/build_opportunity_matrix.py

**CC 응답** (3/4)

# 프로젝트 모델 성능 분석 보고서

## 📋 작업 범위 확인
✅ **요청:** 프로젝트 모델 성능 요약  
✅ **분석 대상:** 제공된 컨텍스트 내 성능 지표 추출 및 정리  
✅ **범위:** 읽기 전용 분석 (코드 수정 없음)

---

## 🎯 식별된 성능 지표

### 1. **ML 품목 분류 모델 (Classification)**
| 지표 | 값 | 출처 |
|------|-----|------|
| **정확도 (Accuracy)** | **98.08%** | `docs/numbers_reference.md` |
| **모델 구조** | TF-IDF + Logistic Regression | `docs/presentation_script.md` |
| **테스트셋 규모** | 14,070건 (홀드아웃) | `docs/numbers_reference.md` |
| **분류 대상** | 18개 품목군 | `docs/presentation_script.md` |

**평가:** ✅ 우수 수준. 공고명 자동 분류가 안정적입니다.

---

### 2. **점수 모델 (Scoring Model)**

#### A. opportunity_score (공공수요 기회 점수)
```
= count_score × 0.40 
+ amount_score × 0.25 
+ recency_score × 0.15 
+ competition_score × 0.20
```

| 컴포넌트 | 가중치 | 검증 상태 |
|---------|------|---------|
| count_score | 40% | ✅ 명시적 공식 |
| amount_score | 25% | ✅ 명시적

---

### [P-T3] 프로젝트 모델 성능 요약해줘 — sonnet

선택 파일: docs/data_dictionary.md, docs/score_model.md, docs/numbers_reference.md, src/features/build_opportunity_matrix.py

**CC 응답** (3/4)

# 프로젝트 모델 성능 요약

컨텍스트에서 확인 가능한 모델 관련 정보를 분석하여 요약합니다.

---

## 1. ML 품목 분류 모델

| 항목 | 내용 |
|---|---|
| **모델 유형** | TF-IDF + Logistic Regression |
| **목적** | 공고명 → 18개 품목군 자동 분류 |
| **정확도** | **98.08%** (= 98%) |
| **평가 기준** | 홀드아웃 테스트셋 **14,070건** |
| **출처 파일** | `src/modeling/train_classifier.py` |

> 📌 출처: `docs/numbers_reference.md`, `docs/presentation_script.md`

---

## 2. 수요공백(블루오션) 이상탐지 모델

| 항목 | 내용 |
|---|---|
| **모델 유형** | Isolation Forest |
| **목적** | opportunity_score 높고 competition_score 낮은 지역 탐지 |
| **파라미터** | `contamination=0.1` (이상치 비율 10%), `min_bid_count=5` (노이즈 제거), `top_n=50` |
| **출력** | `outputs/tables/blue_ocean_districts.csv` |
| **출처 파일** | `src/modeling/demand_anomaly.py` |

> ⚠️ 이 모델에 대한 **정량적 성능 지표(정확도, F1 등)는 컨텍스트 내에서 확인되지 않음**

---

## 3. 점수 모델 (규칙 기반, ML 아님)

점수 모

---

### [R-T1] auth 로그인 JWT 만료 처리 수정해줘 — haiku

선택 파일: frontend-rn/api/auth.js, backend/app/schemas/auth.py, backend/app/services/auth.py, frontend-rn/app/(auth)/login.jsx

**CC 응답** (3/3)

# JWT 만료 처리 분석 및 수정안

## 📋 작업 범위 확인

요청: **"auth 로그인 JWT 만료 처리 수정"**
- JWT 토큰 만료 시 클라이언트/서버 동작 개선
- 만료된 토큰 감지 및 재발급/로그아웃 처리

---

## 🎯 수정 대상 파일

| 파일 | 역할 | 현황 |
|------|------|------|
| `frontend-rn/api/axiosInstance.js` | **HTTP 인터셉터** | 🔴 컨텍스트 누락 |
| `frontend-rn/app/(auth)/login.jsx` | 로그인 화면 | ✅ 있음 |
| `backend/app/services/auth.py` | JWT 생성/검증 | ⚠️ 일부만 있음 |
| `backend/app/api/v1/endpoints/auth.py` | 인증 엔드포인트 | ✅ 있음 |

---

## ⚠️ 예상 영향도

### **HIGH RISK 항목**

1. **인증/권한 로직 변경** (위험도: HIGH)
   - JWT 검증 실패 시 동작 방식 변경
   - 모든 API 호출에 영향 (axiosInstance 인터셉터)
   - 프론트/백엔드 간 토큰 갱신 흐름 추가

2. **환경 설정 변경 가능성** (위험도: MEDIUM)
   - JWT_EXPIRE_HOURS 설정값 조정
   - 토큰 갱신 엔드포인트 추가 필요

3. **DB/세션 로직

---

### [R-T1] auth 로그인 JWT 만료 처리 수정해줘 — sonnet

선택 파일: frontend-rn/api/auth.js, backend/app/schemas/auth.py, backend/app/services/auth.py, frontend-rn/app/(auth)/login.jsx

**CC 응답** (3/3)

# JWT 만료 처리 수정 분석

## 현황 파악

컨텍스트를 분석한 결과, **JWT 만료 관련 처리가 현재 누락**되어 있습니다.

---

## 문제점 정리

### 1. 백엔드 (`backend/app/services/auth.py`)
- `_create_token()`에서 `exp` 클레임은 생성하지만, **토큰 검증 시 만료 여부를 체크하는 로직이 컨텍스트에 보이지 않음**
- `jose` 라이브러리는 `jwt.decode()` 시 자동으로 만료 검증하지만, **만료 시 발생하는 `ExpiredSignatureError`를 별도로 핸들링하는 코드가 없음**

### 2. 프론트엔드 (`frontend-rn/app/(auth)/login.jsx`)
- 로그인 성공 시 `access_token`을 `AsyncStorage`에 저장하지만
- **저장 시점 또는 API 요청 시 토큰 만료를 확인하는 로직 없음**
- 만료된 토큰으로 요청 시 서버 401을 받아도 **자동 로그아웃/재로그인 유도 처리 없음**

### 3. API 인스턴스 (`frontend-rn/api/axiosInstance.js`)
- 컨텍스트에 포함되지 않아 **인터셉터 존재 여부 불명확** → 401 공통 처리 여부 확인 필요

---

## 수정 후보 파일 및 내용

```
[A] backend/app/services/auth.py         ← 토큰 검증 

---

### [R-T2] docker-compose.yml 배포 설정 알려줘 — haiku

선택 파일: .claude/settings.json, .vscode/settings.json, backend/docker-compose.yml, .github/workflows/deploy.yml

**CC 응답** (3/3)

# docker-compose.yml 배포 설정 분석

## 📋 현재 구성 (backend/docker-compose.yml)

**분석 대상 파일:**
- `backend/docker-compose.yml` (54줄)
- 참고: `.github/workflows/deploy.yml` (배포 자동화)
- 참고: `backend/app/core/config.py` (환경변수 연동)

---

## 🔍 현재 설정 상태

### 서비스 구성
| 서비스 | 이미지 | 포트 | 헬스체크 | 자동재시작 |
|--------|--------|------|---------|----------|
| **mongo** | mongo:7 | 127.0.0.1:27017 | ✅ (5회) | always |
| **redis** | redis:7-alpine | 127.0.0.1:6379 | ✅ (5회) | always |
| **backend** | Dockerfile 빌드 | 8000:8000 | ❌ 미설정 | always |

### 주요 특징
```yaml
✅ 강점:
  • 로컬바인드(127.0.0.1) → 외부 노출 차단
  • 헬스체크로 서비스 의존성 관리 (depends_on: condition: service_healthy)
  • 볼륨 마운트로 데이터 영속성 보장
  • .env 파일 읽기로 동적 설정

⚠️ 주의사항:
  • backend 헬스체크 미설정 (mongo/redis만 체크)
  • 백엔드 빌드 시 상위 디렉토리 context (../Dockerfile)
  • /uploads 볼륨 마운트 → 배포 후 파일 관리 필요
```

---

### [R-T2] docker-compose.yml 배포 설정 알려줘 — sonnet

선택 파일: .claude/settings.json, .vscode/settings.json, backend/docker-compose.yml, .github/workflows/deploy.yml

**CC 응답** (3/3)

# `docker-compose.yml` 배포 설정 분석

> **읽기 전용 분석**입니다. 코드 수정은 없으며, 설정 내용을 설명합니다.

---

## 📄 대상 파일

- `backend/docker-compose.yml` (컨텍스트 [3])
- `.github/workflows/deploy.yml` (컨텍스트 [4]) — CI/CD 배포 파이프라인

---

## 🐳 `backend/docker-compose.yml` 구성 설명

### 프로젝트명
```yaml
name: backend
```

---

### 서비스 구성 (3개)

#### 1. `mongo` — MongoDB 7
| 항목 | 값 |
|---|---|
| 이미지 | `mongo:7` |
| 컨테이너명 | `rainbow_mongo` |
| 포트 바인딩 | `127.0.0.1:27017:27017` (로컬호스트만 노출) |
| 볼륨 | `mongo_data:/data/db` (named volume) |
| 재시작 정책 | `always` |
| 헬스체크 | `mongosh --eval db.adminCommand('ping')` / 10s 간격 / 5회 재시도 |

> ⚠️ **보안 포인트**: `127.0.0.1`로 바인딩되어 외부 직접 접근은 차단됩니다.

---

#### 2. `redis` — Redis 7 Alpine
| 항목 | 값 |
|---|---|
| 이미지 | `redis:7-alpine` |
| 컨테이너명 | `rainbow_redis` |
| 포트 바인딩 | `127.0.0.1:6379:6379` (로컬호

---

### [R-T3] users 테이블 마이그레이션 추가해줘 — haiku

선택 파일: backend/app/models/user.py, docs/devlog/members/김윤한.md, docs/devlog/members/반소람.md, docs/devlog/members/정환주.md

**CC 응답** (3/3)

# 분석 결과: users 테이블 마이그레이션 추가

## 📋 작업 범위 확인
**요청**: users 테이블 마이그레이션 추가
**관련 코드**: User 모델([1] backend/app/models/user.py) 기반 마이그레이션 파일 생성

---

## 🔍 현재 상태 분석

### 존재하는 User 모델 구조
```python
id (Integer, PK, autoincrement)
email (String(255), unique, indexed)
password_hash (String(255))
nickname (String(50))
is_active (Boolean, default=True)
created_at (DateTime with timezone, UTC default)
```

### 마이그레이션 시스템 확인 필요
컨텍스트에서 **마이그레이션 도구/경로 정보 부재**:
- Alembic 설정 파일(`alembic.ini`, `migrations/` 구조) 미제시
- DB 초기화 방식(자동/수동) 미확인
- 기존 마이그레이션 파일 존재 여부 불명

---

## ⚠️ 예상 영향도

| 항목 | 위험도 | 설명 |
|------|:------:|------|
| **스키마 정합성** | 🔴 MEDIUM | 기존 DB가 있으면 마이그레이션 전략(upgrade path) 필요 |
| **배포 프로세스** | 🔴 MEDIUM | CI/CD에서 마이그레이션 실행 시점 확인 필요 ([4]정환주 devlog에서 배포 관련) |
| **개발/운영 DB** | 🟡 LOW | 로컬/스테이징/프로

---

### [R-T3] users 테이블 마이그레이션 추가해줘 — sonnet

선택 파일: backend/app/models/user.py, docs/devlog/members/김윤한.md, docs/devlog/members/반소람.md, docs/devlog/members/정환주.md

**CC 응답** (3/3)

## 분석 결과

### 1. 수정 대상 파일 (신규 생성)

| 파일 | 작업 | 비고 |
|------|------|------|
| `backend/alembic/versions/xxxx_create_users_table.py` | **신규 생성** | Alembic 마이그레이션 파일 |

> ⚠️ 현재 컨텍스트에 `alembic/` 디렉터리나 `alembic.ini`의 존재 여부가 확인되지 않습니다. **Alembic이 이미 세팅되어 있는지 먼저 확인이 필요합니다.**

---

### 2. 마이그레이션 대상 스키마 (근거: `backend/app/models/user.py`)

```
테이블명: users

컬럼:
- id            INTEGER       PK, autoincrement
- email         VARCHAR(255)  NOT NULL, UNIQUE, INDEX
- password_hash VARCHAR(255)  NOT NULL
- nickname      VARCHAR(50)   NOT NULL
- is_active     BOOLEAN       DEFAULT TRUE
- created_at    TIMESTAMPTZ   DEFAULT now() (UTC)
```

---

### 3. 예상 영향도

| 항목 | 내용 | 위험도 |
|------|------|--------|
| DB 스키마 변경 | `users` 테이블 신규 생성 | **MEDIUM** — 이미 테이블이 존재하면 충돌 |
| 인증 로직 | `auth.py`가 `users` 테이블에 의존 중 → 마이그레이션 전엔 서비스 불가 | MEDIUM |
| 기존 데이터 | 신규 테이블이므로 데이터 손실 위험 없음 | LOW |

---

