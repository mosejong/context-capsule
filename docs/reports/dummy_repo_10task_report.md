# Context Capsule 외부 더미 레포 스팟 체크 — 10가지 현업 태스크

**대상 레포**: dummy-repo (FastAPI 이커머스 백엔드, 파일 15개)  
**테스트 일자**: 2026-06-28  
**목적**: "쓸만한가?"에 대한 태스크별 파일 선별 정확도 점검

주의: 이 문서는 작은 더미 레포에서 진행한 스팟 체크다. 정식 벤치마크나 일반화된 성능 보장이 아니라, 현재 제품의 강점과 약점을 찾기 위한 테스트 기록이다.

---

## 테스트 환경

```
dummy-repo/
├── main.py
├── src/
│   ├── api/routes/  users.py · products.py · orders.py · middleware.py
│   ├── services/    auth_service.py · payment_service.py · notification_service.py
│   ├── db/          models.py · database.py
│   ├── utils/       cache.py · logger.py
│   └── config/      settings.py
├── .env.example
├── requirements.txt
└── README.md
```

의도적으로 심어둔 문제:
- `auth_service.py` — `JWTError` 미처리 → 만료 토큰 시 500 에러
- `payment_service.py` — 재시도/fallback 없음
- `products.py` — 페이지네이션 없음
- `models.py` — `last_login` 컬럼 없음 (이슈 #47)

---

## 결과 요약

| # | 태스크 | 위험도 | 선택 파일 수 | 핵심 파일 포함 | 평가 |
|---|---|:---:|:---:|:---:|---|
| T1 | README 포폴 수정 | MEDIUM | 1개 | ✅ README.md | ✅ 정확 |
| T2 | 결제 fallback 구조 | MEDIUM | 8개 | ✅ payment_service.py | ✅ 정확 |
| T3 | 서비스 레이어 리팩토링 | MEDIUM | 8개 | ✅ orders.py | ✅ 정확 |
| T4 | JWT 500 버그 수정 | MEDIUM | 8개 | ✅ auth_service.py | ✅ 정확 |
| T5 | 페이지네이션 추가 | MEDIUM | 8개 | ⚠️ products.py 3번째 | ⚠️ 부분 |
| T6 | auth_service 단위 테스트 | HIGH | 8개 | ⚠️ auth_service.py 3번째 | ⚠️ 부분 |
| T7 | last_login 마이그레이션 | HIGH | 8개 | ✅ models.py | ✅ 정확 |
| T8 | 환경변수 가이드 | MEDIUM | 3개 | ✅ .env.example · settings.py | ✅ 정확 |
| T9 | payment_service 코드 리뷰 | MEDIUM | 8개 | ✅ payment_service.py | ✅ 정확 |
| T10 | 결제 재시도 GitHub 이슈 | MEDIUM | 8개 | ✅ payment_service.py | ✅ 정확 |

**핵심 파일 포함: 8/10 (80%)**

---

## 잘한 것

### 1. 위험도 탐지가 큰 틀에서 태스크에 맞게 작동
- T6 (테스트 작성), T7 (DB 마이그레이션) → **HIGH** 자동 탐지
  - 테스트가 auth 로직에 접근 = 인증 관련
  - 마이그레이션 = DB 스키마 변경
- 나머지 → **MEDIUM** (코드 변경이 있지만 critical은 아님)

### 2. 연관 파일 그루핑
- T2 (fallback): `payment_service.py` + `orders.py` + `models.py` 함께 선택  
  → 결제 로직이 세 파일에 걸쳐있는 걸 파악함
- T8 (환경변수 가이드): `.env.example` + `settings.py` + `README.md` 만 뽑음  
  → 불필요한 소스 파일 안 끌어들임

### 3. First Action이 태스크별로 다름
- 문서 작업 → "README.md 기준으로 수정 범위 잡고"
- 코드 변경 → "수정 전 계획을 먼저 제안하세요"
- 위험 작업 → "위험/승인 탭에서 차단 사유 먼저 확인"

---

## 부족한 것

### T5 — 페이지네이션: products.py가 1순위가 아님
```
선택된 순서: orders.py → main.py → db/database.py → products.py
```
"페이지네이션"이라는 키워드가 products보다 order/db 쪽 키워드와 매칭이 더 높은 것으로 보임.  
→ **API 경로명 힌트(`/products`)를 태스크 텍스트에 넣으면 개선 가능**  
→ 혹은 CC가 `TODO` 주석 파싱을 강화하면 자동 해결 (products.py에 `# TODO` 있음)

### T6 — auth 테스트: auth_service.py가 1순위가 아님
```
선택된 순서: orders.py → main.py → payment_service.py → auth_service.py
```
"단위 테스트"라는 키워드가 auth보다 전체 파일을 다 끌어당기는 경향.  
→ **파일명을 명시하면 해결**: "auth_service.py 단위 테스트" 대신  
  "tests/test_auth_service.py 새로 만들어줘"

### 토큰 감소율이 낮음 (0~4%)
소규모 레포(15개 파일)라 전체 스캔해도 토큰이 적음.  
**실제 감소 효과는 파일 수가 많을수록 커짐** — 이전 procurement 레포(86파일)에서는 85~98% 감소.

---

## 사용자 가이드: CC 성능을 높이는 태스크 작성법

| 비교 | 낮은 정확도 | 높은 정확도 |
|---|---|---|
| 파일 특정 | `페이지네이션 추가해줘` | `GET /products 페이지네이션 추가해줘` |
| 테스트 | `auth 테스트 짜줘` | `tests/test_auth_service.py 만들어줘` |
| 버그 | `500 에러 고쳐줘` | `만료 JWT 토큰 시 500 에러 — auth_service decode_token 고쳐줘` |
| 이슈 작성 | `이슈 써줘` | `payment_service.py 재시도 없는 거 이슈 써줘` |

**파일명 또는 경로를 태스크에 포함하면 CC 선별 정확도가 크게 올라간다.**

---

## 결론

> Context Capsule은 현업 태스크 10개 중 8개에서 핵심 파일을 정확하게 선별했다.  
> 파일이 많은 레포일수록 토큰 절약 효과도 커진다.  
> 태스크 문장에 파일명/경로/API 경로를 포함하면 나머지 2개도 개선된다.

**"쓸만한가?" → 소규모 더미 레포에서도 10개 태스크 중 8개는 핵심 파일을 포함했다.**

남은 개선 포인트:

- 페이지네이션, 테스트 작성처럼 짧은 요청은 API 경로/파일명 힌트가 없으면 1순위 랭킹이 흔들릴 수 있다.
- 소규모 레포에서는 토큰 감소율이 낮게 나올 수 있으므로, 토큰 절감보다 파일 선별/작업 범위 정리가 더 큰 가치다.
- 이 결과는 외부 더미 레포 1개 기준이므로, v1.0 전에는 더 다양한 레포로 반복 검증해야 한다.
