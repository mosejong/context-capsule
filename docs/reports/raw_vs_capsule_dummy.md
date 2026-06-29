# Raw vs Context Capsule 비교 — dummy-repo

**모델**: claude-haiku-4-5-20251001  
**날짜**: 2026-06-29  
**레포**: dummy-repo (16파일, FastAPI 이커머스)  

## 요약

| ID | 태스크 | Raw 토큰 | CC 토큰 | 절감 | Raw 점수 | CC 점수 |
|---|---|---|---|---|---|---|
| T1 | auth_service 500 에러 고쳐줘 | ~4,468 | ~2,406 | 46.2% | 3/3 | 3/3 |
| T2 | 결제 실패 고쳐줘 | ~4,468 | ~2,258 | 49.5% | 3/3 | 3/3 |
| T3 | 로그인 안돼 | ~4,468 | ~2,561 | 42.7% | 3/3 | 3/3 |

---

## [T1] auth_service 500 에러 고쳐줘

- 선택 파일: src/services/auth_service.py, src/services/payment_service.py, src/services/notification_service.py, src/utils/cache.py
- 토큰: Raw ~4,468 → CC ~2,406 (46.2% 절감)

### Raw 응답 (3/3)

# 분석 결과

## 🐛 버그 위치
**파일**: `src/services/auth_service.py`  
**함수**: `decode_token()`  
**라인**: JWT 디코딩 부분

---

## 📋 문제 설명

### 원인
```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

**`jwt.decode()`가 발생시킬 수 있는 예외들**:
- `ExpiredSignatureError` - 만료된 토큰
- `JWTError` - 유효하지 않은 토큰
- `JWTClaimsError` - claim 검증 실패

이들이 **처리되지 않으면** 애플리케이션까지 전파되어 **500 Internal Server Error**가 발생합니다.

### 호출 체인
```
get_current_user() 
  → decode_token() [예외 발생]
    → HTTPException으로 변환 안 됨
      → 500 에러
```

README의 `#61` 이슈와도 일치합니다:
> `#61` 만료된 JWT 토큰 → 500 에러 (401이어야 함)

---

## ✅ 수정 방안

### 방법 1: `decode_token()`에서 예외 처리 (권장)

```python
from jose import JWTError, jwt
from fastapi import HTTPException, status

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        # JWTError는 ExpiredSignatureError, JWTClaimsError 등의 부모 클래스
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

**장점**:
- 예외를 명시적으로 처리
- 401 상태 코드 반환
- 재사용 가능한 함수

---

### 방법 2: `get_current_user()`에서 예외 처리

```python
from jose import JWTError

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

---

## 🎯 권장 사항

**방법 1을 추천합니다** 이유:
1. **단일 책임**: 각 함수가 자신의 예외만 처리
2. **재사용성**: `decode_token()`을 다른 곳에서 사용할 때도 안전
3. **명확성**: 토큰 디코딩 실패의 책임이 분명함

### 추가 개선 사항
`src/config/settings.py` import 추가:
```python
from fastapi import status
```

그리고 다른 

### CC 응답 (3/3)

# 분석 완료: auth_service 500 에러

## 📋 수정 대상 파일
- **src/services/auth_service.py** (주 수정 대상)
- **src/api/routes/users.py** (연쇄 영향)

---

## 🔍 문제점 분석

### 근본 원인
**src/services/auth_service.py의 `decode_token()` 함수** (라인 23-26)

```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

**문제:**
- JWT 토큰 만료 시 `JWTError` 예외가 발생하지만 처리되지 않음
- 예외가 응답 핸들러까지 전파되어 **500 Internal Server Error** 반환
- 올바른 HTTP 응답은 **401 Unauthorized**여야 함

**영향받는 플로우:**
1. 사용자가 만료된 토큰으로 요청
2. `get_current_user()` → `decode_token()` 호출 (users.py 라인 29)
3. JWTError 미처리 → 500 에러 발생

---

## 💥 예상 영향도

| 구간 | 심각도 | 설명 |
|------|--------|------|
| **사용자 인증** | 🔴 HIGH | 모든 토큰 검증 엔드포인트 영향 |
| **주문 생성** | 🔴 HIGH | `/orders` POST는 `get_current_user` 의존 |
| **API 응답** | 🟡 MEDIUM | 에러 상태 코드 변경 (500→401) |
| **로깅/모니터링** | 🟡 MEDIUM | 기존 500 에러 로그에서 401로 변경 |

---

## 🛠️ 수정 방안 (2가지 선택지)

### **방안 A: 예외 처리 추가 (권장)**

**src/services/auth_service.py에서:**

```python
from jose import JWTError, jwt

def decode_token(token: str) -> dict:
    """
    JWT 토큰을 디코딩합니다.
    
    Raises:
        JWTError: 토큰이 유효하지 않거나 만료된 경우
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        # 호출자(get_current_user)에서 처리하도록 예외 전파
        raise e
```

**src/api/routes/users.py에서:**

```python
from jose import JWTError

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=401, 
            detail="Token expired or invalid"
        )
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

**장점:**
- 책임 분리 명확 (decode vs 에러 처리)
- 다른 곳에서

---

## [T2] 결제 실패 고쳐줘

- 선택 파일: src/services/payment_service.py, src/services/notification_service.py, README.md, src/utils/cache.py
- 토큰: Raw ~4,468 → CC ~2,258 (49.5% 절감)

### Raw 응답 (3/3)

# 결제 실패 문제 분석

## 🔴 버그 위치 및 원인

### 1. **주요 버그: 재시도 로직 부재**
**파일**: `src/services/payment_service.py`  
**함수**: `process_order_payment()`

```python
def process_order_payment(db: Session, order_id: int, card_token: str) -> Order:
    # ...
    try:
        result = charge_payment(order_id, order.total_amount, card_token)
        order.status = "paid"
        order.payment_id = result.get("payment_id")
    except RuntimeError:
        order.status = "failed"  # ❌ 일회성 실패 → 바로 failed 처리
```

**문제점**:
- 결제 API 호출이 **네트워크 오류, 타임아웃, 일시적 에러**로 실패해도 재시도 없이 즉시 `failed`로 변경
- `.env`에 `MAX_RETRY_COUNT=3`, `RETRY_DELAY_SECONDS=1.0`이 정의되어 있지만 **사용되지 않음**
- README의 이슈 `#58`에서도 명시: "결제 실패 시 재시도 로직 없음"

---

### 2. **부차 버그: 예외 처리 범위 제한**
**파일**: `src/services/payment_service.py`  
**함수**: `charge_payment()`

```python
except httpx.HTTPStatusError as e:
    logger.error(f"결제 실패: {e.response.status_code}")
    raise RuntimeError(f"결제 실패: {e.response.text}")
```

**문제점**:
- `httpx.RequestError`, `httpx.ConnectError` 등 다른 네트워크 예외는 **상위로 전파**되어 500 에러 발생
- 일시적 오류와 영구적 오류를 구분하지 않음

---

### 3. **간접 영향: 비동기 처리 부재**
**파일**: `src/api/routes/orders.py`  
**함수**: `create_order()`

```python
order = process_order_payment(db, order.id, body.card_token)  # 동기 블로킹
```

**문제점**:
- 결제 처리가 동기로 진행되어 **결제 서버 지연 시 전체 주문 생성이 블로킹**
- 재시도 로직이 추가되면 지연 시간이 더 늘어남 (3회 × 1초 = 최대 3초)

---

## ✅ 수정 방향

### **방안 1: 기본 재시도 로직 추가 (권장)**

`payment_service.py`에 재시도 메커니즘 추가:

```python
import asyncio
from src.config.settings import MAX_RETRY_COUNT, RETRY_DELAY_SECONDS

def process_order_payment(db: Session, order_id: int, card_token: str) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise ValueError(f"주문 없음: {order_id}")
    if order.status != "pending":
        raise ValueError(f"결제 불가 상태: {order.status}")

    for attempt in range(1, MAX_RETRY_COUNT + 1):
        try:
            result = charge_payment(order_id, order.total_amount, card_token)
            order.status = "paid"
            order.payment_id = result.get("payment_id")
            db.

### CC 응답 (3/3)

# 결제 실패 문제 분석

## 📋 작업 범위 확인
**요청:** "결제 실패 고쳐줘"  
**분석 대상:** `payment_service.py`, `orders.py`, 관련 설정 및 알려진 이슈

---

## 🔍 식별된 문제점

### 1. **재시도 로직 부재** (README.md #58)
- `charge_payment()` 함수에서 타임아웃/실패 시 **즉시 예외 발생**
- 환경변수 `MAX_RETRY_COUNT`, `RETRY_DELAY_SECONDS`가 정의되어 있으나 **사용 안 됨**
- 일시적 네트워크 오류 시 주문 실패 처리됨

### 2. **에러 처리 불충분**
```python
except httpx.HTTPStatusError as e:
    raise RuntimeError(f"결제 실패: {e.response.text}")
```
- `e.response.text`가 JSON이면 파싱 필요
- 특정 HTTP 상태코드별 처리 없음 (4xx vs 5xx 구분 안 함)

### 3. **불완전한 코드 (컨텍스트 [1])**
- `refund_payment()` 함수가 **잘려있음**
- `orders.py`의 `process_order_payment()` 함수가 **정의되지 않은 상태**로 호출됨

### 4. **주문 상태 관리 불명확**
- 결제 실패 시 Order 상태를 무엇으로 설정할지 불명확
- 데이터베이스 트랜잭션 롤백 처리 보이지 않음

---

## 📊 영향도 평가

| 항목 | 영향도 | 사유 |
|------|--------|------|
| **payment_service.py** | 🔴 HIGH | 결제 핵심 로직 변경 |
| **orders.py** | 🟡 MEDIUM | 에러 처리 플로우 수정 필요 |
| **settings.py** | 🟡 MEDIUM | 재시도 설정값 사용 시작 |
| **DB schema** | ⚠️ 주의 | Order 상태값 검증 필요 |

---

## 💡 수정 후보 방안

### **방안 A: 지수 백오프 재시도 로직 추가** (권장)
```
변경 범위:
- payment_service.py에 retry_with_exponential_backoff() 함수 추가
- charge_payment()를 이 함수로 래핑
- 환경변수 MAX_RETRY_COUNT, RETRY_DELAY_SECONDS 활용
- 특정 에러만 재시도 (타임아웃, 5xx)

위험: 결제 중복 요청 가능성 → idempotency key 필요
```

### **방안 B: 상태 머신 패턴 도입**
```
변경 범위:
- Order 모델에 결제 상태 세분화 (pending → processing → success/failed)
- orders.py에서 각 단계별 상태 업데이트
- 알림 서비스 호출 시점 명확히

위험: DB migration 필요, 기존 데이터 상태값 변환 필요
```

### **방안 C: 결제 실패 후 재시도 UI 제공** (최소 변경)
```
변경 범위:
-

---

## [T3] 로그인 안돼

- 선택 파일: src/services/payment_service.py, src/services/auth_service.py, src/api/routes/users.py, src/services/notification_service.py
- 토큰: Raw ~4,468 → CC ~2,561 (42.7% 절감)

### Raw 응답 (3/3)

# 🔍 "로그인 안돼" 문제 분석

## 🐛 발견된 버그

### 1. **PRIMARY BUG: `decode_token()` 예외 처리 누락**

**파일:** `src/services/auth_service.py` (라인 27-30)

```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

**문제점:**
- JWT 토큰이 **만료되거나 유효하지 않으면** `JWTError` 예외 발생
- 예외를 처리하지 않아서 **500 Internal Server Error** 반환
- 클라이언트는 로그인 상태를 알 수 없음

**영향받는 엔드포인트:**
- `GET /users/me` (인증 필요)
- `POST /orders/` (인증 필요)
- `GET /orders/{order_id}` (인증 필요)

---

### 2. **SECONDARY BUG: `get_current_user()` 불완전한 에러 처리**

**파일:** `src/api/routes/users.py` (라인 32-43)

```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # decode_token이 JWTError를 안 잡아서 만료 토큰 → 500 터짐
    payload = decode_token(token)  # ← JWTError 터질 수 있음
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

**문제점:**
- `decode_token()`에서 예외 발생 시 처리 불가능
- `JWTError` 예외가 상위로 전파되어 FastAPI가 500 응답 반환

---

## 🔧 수정 방향

### **Option A: `auth_service.py`에서 예외 처리 (권장)**

```python
from jose import JWTError, jwt
from fastapi import HTTPException, status

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
```

**장점:**
- 한 곳에서 JWT 예외 처리 통일
- 재사용 가능한 구조

---

### **Option B: `users.py`에서 예외 처리**

```python
from jose import JWTError

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=401, 
            detail="Invalid or expired token"
        )
    
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
```

**단점:** 다른 곳에서 `decode_token()` 사용 시 또 

### CC 응답 (3/3)

# 분석: "로그인 안돼" 문제 진단

## 📋 작업 범위 확인
✅ 사용자 요청: 로그인 기능 문제 분석  
✅ 관련 컨텍스트: 인증 관련 코드 포함됨  
✅ 범위: 분석 및 제안 단계 (승인 전까지 수정 금지)

---

## 🎯 근본 원인 분석

컨텍스트에서 **명확한 로그인 실패 원인**이 식별됩니다:

### **주요 문제 (우선순위 높음)**

**[문제 1] JWT 토큰 검증 실패 → 500 에러**  
📍 위치: `src/services/auth_service.py:22-24` (decode_token)
```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```
- **영향**: 만료되거나 유효하지 않은 토큰 → `JWTError` 예외 → 500 에러 (클라이언트는 401 기대)
- **현상**: 로그인 후 요청 시 "로그인 안됨" 처럼 보임

**[문제 2] 에러 처리 누락**  
📍 위치: `src/api/routes/users.py:23-31` (get_current_user)
```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # decode_token이 JWTError를 안 잡아서 만료 토큰 → 500 터짐
    payload = decode_token(token)
    ...
```
- decode_token에서 JWTError가 발생해도 처리되지 않음

**[문제 3] 사용자 정보 누락**  
📍 위치: `src/services/auth_service.py:27-31` (authenticate_user - 코드 잘림)
```python
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not verify_password(password, user.hash  # ← 코드 끝남
```
- 함수가 불완전함 (user.hash 뒤 로직 누락)

---

## 📊 영향도 평가

| 파일 | 변경 범위 | 위험도 | 영향도 |
|------|---------|-------|------|
| `auth_service.py` | decode_token, authenticate_user | **HIGH** | 로그인 전체 실패 |
| `users.py` | get_current_user | **HIGH** | 토큰 검증 실패 |
| `README.md` | 이슈 #61 참조 | LOW | 문서만 |

---

## ✅ 수정 후보안

### **[필수] 1단계: JWT 예외 처리 추가**
```python
# src/services/auth_service.py - decode_token 수정
from jose import JWTError, jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")
```

### **[필수] 2단

---

