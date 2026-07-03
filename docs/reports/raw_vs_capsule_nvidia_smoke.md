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

## Run Scope

- Selected repos: dummy
- Task limit per repo: 1
- The table below is generated only from this run's measured rows.
- If `--task-limit` is set, treat this as a smoke test, not a full benchmark.

## Repo/Model Summary

| Repo | Model | Raw measured | Raw score | CC score | Avg token reduction |
|---|---|---:|---:|---:|---:|
| dummy-repo (소형 16파일) | nemotron-3-ultra-550b-a55b | 1 | 3/3 | 3/3 | 47.9% |

## 요약

| 레포 | ID | 태스크 | 모델 | Raw토큰 | CC토큰 | 절감 | Raw점수 | CC점수 | Raw비용 | CC비용 |
|---|---|---|---|---|---|---|---|---|---:|---:|
| dummy-repo | D-T1 | auth_service 500 에러  | nemotron-3-ultra-550b-a55b | ~4,468 | ~2,327 | 47.9% | 3/3 | 3/3 | $0.0000 | $0.0000 |

---

## 상세 응답

### [D-T1] auth_service 500 에러 고쳐줘 — nemotron-3-ultra-550b-a55b

선택 파일: src/services/auth_service.py, src/services/payment_service.py, src/services/notification_service.py, src/utils/cache.py

**Raw 응답** (3/3)

The user wants me to fix the 500 error in `auth_service.py` when an expired JWT token is used. Let me analyze the issue.

From the README.md known issues:
- `#61` 만료된 JWT 토큰 → 500 에러 (401이어야 함)

Looking at `src/services/auth_service.py`, the `decode_token` function:
```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return payload
```

The comment even says it doesn't catch JWTError, so expired tokens cause a 500 error.

And in `src/api/routes/users.py`, the `get_current_user` function:
```python
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # decode_token이 JWTError를 안 잡아서 만료 토큰 → 500 터짐
    payload = decode_token(token)
    email = payload.get("sub")
    if not

**CC 응답** (3/3)

The user is asking me to fix a 500 error in auth_service. Looking at the context, I can see:

1. In `src/services/auth_service.py`, the `decode_token` function doesn't catch `JWTError`, which causes expired tokens to throw a 500 error instead of a proper 401.

2. In `src/api/routes/users.py`, the `get_current_user` function calls `decode_token` without handling the exception.

3. The README.md mentions issue #61: "만료된 JWT 토큰 → 500 에러 (401이어야 함)" - Expired JWT token → 500 error (should be 401).

The fix should be in `src/services/auth_service.py` to catch `JWTError` in the `decode_token` function and raise an appropriate exception, or handle it in the `get_current_user` function in `src/api/routes/users.py`.

Let me analyze the code:

In `auth_service.py`:
```python
def decode_token(token: str) -> dict:
    # 버그: JWTError를 잡지 않아서 만료된 토큰이 500 에러를 냄


---

