# Raw vs Context Capsule — 전체 비교

**날짜**: 2026-07-03  
**Provider**: nvidia_nim  
**모델**: nvidia/nemotron-3-ultra-550b-a55b

## 인터뷰 최종 수치

- CC 전체 정답률: 3/3 (100.0%)
- Raw 전체 정답률: 3/3 (100.0%)
- 평균 토큰 절감: 47.9%
- 핵심 메시지: 비싼 모델도 Raw 컨텍스트에서는 추상적으로 답할 수 있으며, Context Capsule이 관련 근거를 좁혀줄 때 파일명/함수명/수치 정확도가 살아난다.

## Provider Cost Observation

NVIDIA NIM Build endpoints are treated as prototype/testing endpoints in this report. No product-operation cost guarantee is claimed, and API keys are read only from `NVIDIA_API_KEY` without being written to reports or metadata.

## Actual API Cost (computed from response `usage`)

No local price table is configured for this provider. Usage can be captured when the endpoint returns token usage, but this report does not convert it to billing cost.

## 레포/모델별 요약

### dummy-repo (소형, Raw vs CC 전 모델)

| 모델 | Raw | CC | 핵심 |
|---|---:|---:|---|
| See summary table below | - | - | Provider-specific results are generated from this run. |

Opus Raw이 Haiku Raw보다 낮은 이유: Opus는 전체 컨텍스트를 추상화해서 답하는 경향이 있어 파일명/함수명을 생략했다. CC가 좁혀주면 9/9로 역전된다.

### procurement-logistics-ai (중형, 107K Raw)

| 모델 | Raw | CC |
|---|---:|---:|
| Haiku | 0/9 | 8/9 |
| Sonnet | - | 8/9 |
| Opus | - | 8/9 |

### rainbow-bridge (대형 451파일, CC only)

| 모델 | CC |
|---|---:|
| Haiku | 9/9 |
| Sonnet | 9/9 |
| Opus | 8/9 |

## 요약

| 레포 | ID | 태스크 | 모델 | Raw토큰 | CC토큰 | 절감 | Raw점수 | CC점수 | Raw비용 | CC비용 |
|---|---|---|---|---|---|---|---|---|---:|---:|
| dummy-repo | D-T1 | auth_service 500 에러  | nemotron-3-ultra-550b-a55b | ~4,468 | ~2,327 | 47.9% | 3/3 | 3/3 | $0.0000 | $0.0000 |

---

## 상세 응답

### [D-T1] auth_service 500 에러 고쳐줘 — nemotron-3-ultra-550b-a55b

선택 파일: src/services/auth_service.py, src/services/payment_service.py, src/services/notification_service.py, src/utils/cache.py

**Raw 응답** (3/3)

The user wants me to fix the 500 error in `auth_service.py` when a JWT token is expired.
Looking at the code in `src/services/auth_service.py`, the `decode_token` function calls `jwt.decode` but doesn't catch `JWTError`.
In `src/api/routes/users.py`, `get_current_user` calls `decode_token` directly. If `jwt.decode` raises an exception (like `ExpiredSignatureError` which inherits from `JWTError`), it bubbles up as a 500 Internal Server Error instead of a 401 Unauthorized.

The README mentions issue #61: "만료된 JWT 토큰 → 500 에러 (401이어야 함)".

I need to:
1. Modify `decode_token` in `src/services/auth_service.py` to catch `JWTError` and raise an appropriate HTTPException (or return None/raise a custom exception that the route handler catches).
2. Since `get_current_user` in `src/api/routes/users.py` expects a payload dict, raising `HTTPException` directly from `decode_token` is the cleanest way, but `auth_service` shouldn't ideally depend on FastAPI's `HTTPException`.

**CC 응답** (3/3)

The user is asking me to fix a 500 error in auth_service. Looking at the context, I can see the issue:

1. In `src/services/auth_service.py`, the `decode_token` function doesn't catch `JWTError`, so expired tokens cause a 500 error instead of a proper 401.
2. In `src/api/routes/users.py`, the `get_current_user` function calls `decode_token` which throws an unhandled exception for expired/invalid tokens.
3. The README.md mentions issue #61: "만료된 JWT 토큰 → 500 에러 (401이어야 함)" - expired JWT token → 500 error (should be 401).

The fix should be in `src/services/auth_service.py` to catch `JWTError` in `decode_token` and raise a proper exception, or handle it in the route. Looking at the code, the comment in auth_service.py says "버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄" (Bug: Doesn't catch JWTError so expired token causes 500 error).

The proper fix would

---

