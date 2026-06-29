# Context Capsule 엣지케이스 검증 보고서

**버전**: v0.2.13 (+ 구어체 패치)
**테스트 일자**: 2026-06-29
**목적**: 강사님 전달 전 자체 검증 — 대형 레포·모호 쿼리·구어체 경계 케이스

---

## 테스트 환경

| 구분 | 레포 | 파일 수 (CC 스캔) |
|---|---|---|
| 소형 | dummy-repo (FastAPI 이커머스) | 16개 |
| 대형 | TEAM_2/rainbow-bridge (React Native + FastAPI) | 451개 |

이전 테스트(dummy 10태스크, procurement 86파일)에서 검증 안 된 축을 채운다:

- **레포 크기**: 대형(200+ 파일) ← 이번에 추가
- **쿼리 명확도**: 완전 모호 / 구어체 / 반구어체+도메인 / 파일명 명시

---

## 결과 요약

| ID | 태스크 | 레포 | 기대 동작 | 결과 |
|---|---|---|---|---|
| L1 | "버그 있어" | 대형 451 | clarification_only | ✅ PASS |
| L2 | "auth JWT 만료 수정해줘" | 대형 451 | HIGH risk + auth 파일 | ✅ PASS |
| L3 | "결제 오류 수정해줘" (payment 파일 없는 레포) | 대형 451 | MEDIUM risk, hit 없어도 OK | ✅ PASS |
| L4 | "docker-compose.yml 프로덕션 배포 수정해줘" | 대형 451 | HIGH risk + docker 파일 | ✅ PASS |
| L5 | "users 테이블 last_login 마이그레이션" | 대형 451 | HIGH risk + model 파일 | ✅ PASS |
| D1 | "이거 왜 500 뜨냐" | 소형 16 | clarification_only | ✅ PASS |
| D2 | "로그인 안돼" | 소형 16 | MEDIUM + auth_service | ✅ PASS |
| D3 | "결제 이상해" | 소형 16 | MEDIUM + payment_service | ✅ PASS |
| D4 | "버그 있어" | 소형 16 | clarification_only | ✅ PASS |
| D5 | "500 에러 고쳐줘" | 소형 16 | MEDIUM + payment/auth | ✅ PASS |
| D6 | "auth_service 500 에러 고쳐줘" | 소형 16 | HIGH + auth_service mandatory | ✅ PASS |
| D7 | "결제 실패 고쳐줘" | 소형 16 | MEDIUM + payment_service | ✅ PASS |
| D8 | "JWT 만료 토큰 500 터져" | 소형 16 | MEDIUM + auth_service | ✅ PASS |

**13/13 PASS** | 기존 pytest 138개 회귀 없음

---

## 발견된 버그 및 수정

### 버그: "결제 실패 고쳐줘" → clarification_only (D7)

**증상**: `confidence 0.2 (low)`, `intent: general`, `clarification_only` 반환.
결제 도메인 + 수정 의도가 명확한데 파일을 못 찾아줌.

**원인 1** (`simple_retriever.py`):
`"실패"`, `"이상해"`, `"터져"` 등 구어체 장애 표현이 `MULTILINGUAL_DOMAIN_TERMS`에 없어서 retriever가 관련 용어로 확장 불가.

**원인 2** (`request_understanding.py`):
`INTENT_HINTS["bug_investigation"]`에 `"고쳐"`, `"실패"` 등 한국어 수정/장애 표현이 없어서 `intent = "general"`로 판정.
`is_ambiguous_request()`에서 `intent == "general" and len(tokens) <= 3` 조건에 걸려 ambiguous 처리됨.

**수정 내용**:

```python
# simple_retriever.py — MULTILINGUAL_DOMAIN_TERMS 추가
"실패": ("fail", "error", "failure"),
"이상해": ("broken", "fail", "error"),
"이상함": ("broken", "fail", "error"),
"터져": ("crash", "fail", "error"),
"죽어": ("crash", "fail", "error"),
```

```python
# request_understanding.py — INTENT_HINTS bug_investigation 확장
("bug_investigation", (
    "안됨", "안돼", "오류", "에러", "왜",
    "bug", "error", "fix",
    "고쳐", "고치", "실패", "터져", "죽어", "이상해", "이상함"  # 추가
)),
```

**수정 후**: `confidence 0.58 (medium)`, `intent: bug_investigation`, `payment_service.py` 1순위 반환.

---

## 축별 분석

### 쿼리 명확도

| 명확도 | 예시 | CC 동작 |
|---|---|---|
| 완전 모호 | "버그 있어", "이거 왜 500 뜨냐" | clarification_only ✅ |
| 구어체+도메인 | "로그인 안돼", "결제 이상해" | 도메인 파일 반환 ✅ |
| 반구어체+액션 | "결제 실패 고쳐줘", "500 에러 고쳐줘" | 도메인 파일 반환 ✅ |
| 파일명 명시 | "auth_service 500 에러 고쳐줘" | mandatory 포함 + HIGH ✅ |
| 명확한 기술 요청 | "JWT 만료 처리 수정해줘" | HIGH + auth 파일 ✅ |

**결론**: 파일명이나 도메인 키워드 하나만 있어도 파일 선별 가능. 아무 힌트 없는 2토큰 이하 요청만 clarification.

### 레포 크기

| 크기 | 파일 수 | clarification | 파일 선별 | 위험도 |
|---|---|---|---|---|
| 소형 | 16개 | 정상 | 정상 | 정상 |
| 중형 (기존 검증) | 86개 | 정상 | hit@1 9/10 | 정상 |
| 대형 | 451개 | 정상 | auth/docker/migration 정확 | HIGH 정확 |

451파일 레포에서도 `mode=keyword` 기본값으로 auth 파일 4개 포함, docker-compose 정확 반환. 성능 저하 없음.

### 위험도 정확도 (대형 레포)

| 태스크 | 예상 | 실제 | 근거 |
|---|---|---|---|
| JWT 수정 | HIGH | HIGH | change_risk: auth |
| docker 배포 수정 | HIGH | HIGH | change_risk: docker |
| DB 마이그레이션 | HIGH | HIGH | change_risk: login/model |
| 결제 오류 수정 | MEDIUM | MEDIUM | mention_risk만 (payment 파일 없음) |

---

## 한계 및 주의사항

### L3: 레포에 해당 도메인이 없을 때

"결제 오류 수정해줘"를 rainbow-bridge(교통앱)에 날리면 devlog README가 반환됨.
CC는 없는 파일을 만들어내지 않고 가장 유사한 파일을 반환한다. 이는 올바른 동작.
→ **CC가 틀린 게 아니라, 레포에 해당 기능이 없는 것임을 사용자가 인지해야 함.**

### "500 에러 고쳐줘" 는 clarification 없이 파일 반환

`"고쳐"` → `bug_investigation` intent → clarification 없이 payment_service, auth_service 반환.
어느 파일에서 500이 나는지 모르지만 두 파일 모두 후보이므로 실용적으로 맞는 동작.
→ 더 정확하게 하려면 "auth_service 500 에러 고쳐줘"처럼 파일명 포함 권장.

---

## 현재까지 전체 검증 현황

| 검증 축 | 상태 | 레포 | 결과 |
|---|---|---|---|
| 소형 레포 (16파일) | ✅ 완료 | dummy-repo | 10태스크 8/10 + 엣지케이스 8/8 |
| 중형 레포 (86파일) | ✅ 완료 | procurement-logistics-ai | hit@1 9/10, risk 10/10 |
| 대형 레포 (451파일) | ✅ 완료 | rainbow-bridge | 5/5 PASS |
| 모호/구어체 쿼리 | ✅ 완료 | dummy-repo | 8/8 PASS |
| 위험도 탐지 | ✅ 완료 | 전 레포 | 전 케이스 정확 |
| pytest 자동화 | ✅ 138 PASS | — | 회귀 없음 |

---

*자체 검증 기준: 강사님 전달 전 경계 케이스 전 범위 커버 확인 목적*
