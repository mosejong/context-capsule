# Raw vs Context Capsule — 전체 비교

**날짜**: 2026-07-04  
**Provider**: nvidia_nim  
**모델**: nvidia/nemotron-3-ultra-550b-a55b, deepseek-ai/deepseek-v4-flash

## 실험 요약 수치

- CC 전체 정답률: 18/18 (100.0%)
- Raw 전체 정답률: not measured (CC-only run)
- 평균 토큰 절감: not measured (Raw baseline was not sent)
- 핵심 메시지: 이번 실행은 대형 레포 CC-only 검증이다. Raw baseline은 전송하지 않았으므로 정확도/토큰 절감 비교로 해석하지 않는다.

## Provider Cost Observation

NVIDIA NIM Build endpoints are treated as prototype/testing endpoints in this report. No product-operation cost guarantee is claimed, and API keys are read only from `NVIDIA_API_KEY` without being written to reports or metadata.

## Actual API Cost (computed from response `usage`)

No local price table is configured for this provider. Usage can be captured when the endpoint returns token usage, but this report does not convert it to billing cost.

## Run Scope

- Selected repos: rainbow
- Task limit per repo: none
- The table below is generated only from this run's measured rows.
- If `--task-limit` is set, treat this as a smoke test, not a full benchmark.
- Provider calls retry transient 429/5xx/timeout errors up to 2 times before recording an error.

## Repo/Model Summary

| Repo | Model | Raw measured | Raw score | CC score | Avg token reduction |
|---|---|---:|---:|---:|---:|
| rainbow-bridge (대형 451파일) | deepseek-v4-flash | 0 | not measured | 9/9 | not measured |
| rainbow-bridge (대형 451파일) | nemotron-3-ultra-550b-a55b | 0 | not measured | 9/9 | not measured |

## 요약

| 레포 | ID | 태스크 | 모델 | Raw토큰 | CC토큰 | 절감 | Raw점수 | CC점수 | Raw비용 | CC비용 |
|---|---|---|---|---|---|---|---|---|---:|---:|
| rainbow-bridge | R-T1 | auth 로그인 JWT 만료 처리 수 | nemotron-3-ultra-550b-a55b | - | ~1,561 | not measured | CC only | 3/3 | - | $0.0000 |
| rainbow-bridge | R-T1 | auth 로그인 JWT 만료 처리 수 | deepseek-v4-flash | - | ~1,561 | not measured | CC only | 3/3 | - | $0.0000 |
| rainbow-bridge | R-T2 | docker-compose.yml 배 | nemotron-3-ultra-550b-a55b | - | ~1,825 | not measured | CC only | 3/3 | - | $0.0000 |
| rainbow-bridge | R-T2 | docker-compose.yml 배 | deepseek-v4-flash | - | ~1,825 | not measured | CC only | 3/3 | - | $0.0000 |
| rainbow-bridge | R-T3 | users 테이블 마이그레이션 추가해 | nemotron-3-ultra-550b-a55b | - | ~2,407 | not measured | CC only | 3/3 | - | $0.0000 |
| rainbow-bridge | R-T3 | users 테이블 마이그레이션 추가해 | deepseek-v4-flash | - | ~2,407 | not measured | CC only | 3/3 | - | $0.0000 |

---

## 상세 응답

### [R-T1] auth 로그인 JWT 만료 처리 수정해줘 — nemotron-3-ultra-550b-a55b

선택 파일: frontend-rn/api/auth.js, backend/app/schemas/auth.py, backend/app/services/auth.py, frontend-rn/app/(auth)/login.jsx

**CC 응답** (3/3)

The user is asking me to fix JWT expiration handling for auth login. Let me analyze the context provided to understand the current implementation and identify what needs to be fixed.

From the context:
1. `backend/app/services/auth.py` - Contains JWT token creation with `_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))` - tokens expire in 24 hours by default
2. `frontend-rn/app/(auth)/login.jsx` - Login screen that stores access_token in AsyncStorage
3. `frontend-rn/api/auth.js` and `frontend/src/api/auth.js` - API auth modules
4. `backend/app/api/v1/endpoints/auth.py` - Auth endpoints

The issue seems to be about JWT expiration handling. Common issues could be:
1. No refresh token mechanism - when access token expires, user gets logged out
2. No automatic token refresh on 401 responses
3. Frontend doesn't handle expired tokens gracefully
4. Token expiration time might be too short/long

Let me look at what files might need changes:
- Backend: May need refresh token implementation
- Frontend: Need to handle 401 errors

---

### [R-T1] auth 로그인 JWT 만료 처리 수정해줘 — deepseek-v4-flash

선택 파일: frontend-rn/api/auth.js, backend/app/schemas/auth.py, backend/app/services/auth.py, frontend-rn/app/(auth)/login.jsx

**CC 응답** (3/3)

우선 사용자의 요청은 "auth 로그인 JWT 만료 처리 수정해줘"입니다. 관련 컨텍스트를 보면 backend/app/services/auth.py에 JWT 만료 시간 관련 설정이 보입니다. _EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "24"))로 24시간 기본값입니다. 또한 frontend-rn/app/(auth)/login.jsx에서 로그인 후 access_token을 AsyncStorage에 저장하고 있습니다.

사용자가 "JWT 만료 처리 수정"이라고 했으니, 아마도 만료 시간을 변경하거나, 만료 시 리프레시 토큰을 도입하거나, 만료 시 자동 로그아웃 처리 등을 원할 수 있습니다. 하지만 구체적인 요구사항이 명확하지 않습니다. "수정"이라는 말이 모호합니다.

위험 신호에 따르면 인증/권한 로직 영향 가능성이 HIGH로 표시되어 있습니다. 따라서 변경 전에 영향도와 수정 후보를 먼저 설명해야 합니다.

또한 사람 승인 체크리스트에 따라 AI가

---

### [R-T2] docker-compose.yml 배포 설정 알려줘 — nemotron-3-ultra-550b-a55b

선택 파일: .claude/settings.json, .vscode/settings.json, backend/docker-compose.yml, .github/workflows/deploy.yml

**CC 응답** (3/3)

# docker-compose.yml 배포 설정 분석

## 📁 관련 파일
- **`backend/docker-compose.yml`** - 백엔드 서비스 구성 (메인 설정)
- **`.github/workflows/deploy.yml`** - 배포 파이프라인에서 docker-compose 사용 방식

---

## 🐳 backend/docker-compose.yml 상세 분석

```yaml
name: backend

services:
  # 1. MongoDB 7
  mongo:
    image: mongo:7
    container_name: rainbow_mongo
    ports:
      - "127.0.0.1:27017:27017"  # 호스트 루프백만 바인딩 (외부 노출 안 함)
    volumes:
     

---

### [R-T2] docker-compose.yml 배포 설정 알려줘 — deepseek-v4-flash

선택 파일: .claude/settings.json, .vscode/settings.json, backend/docker-compose.yml, .github/workflows/deploy.yml

**CC 응답** (3/3)

We need to respond to the user's request: "docker-compose.yml 배포 설정 알려줘" which means "Tell me about docker-compose.yml deployment settings". The user wants information about the docker-compose.yml deployment configuration. We should analyze the provided context, specifically the backend/docker-compose.yml file (context [3]) and the deploy.yml (context [4]) which shows how it's used in deployment. We should explain the configuration, services, volumes, healthchecks, etc. Also note the user's request is just to "알려줘" (tell me), not to modify anything. So we should provide an explanation of the docker-compose.yml setup and how it's used in deployment. We must follow the instructions: do not modify code without approval, analyze only, explain impact and alternatives if needed. Since this is just an informational request, we can answer directly. But we need to be careful about the context: there are risk signals about docker and deployment. We should provide a clear explanation.

We'll structure the response: first list the relevant files (backend/docker-compose.yml, .github/workflows/deploy.yml), then explain the docker-compose configuration, then explain how it's used in the deployment pipeline

---

### [R-T3] users 테이블 마이그레이션 추가해줘 — nemotron-3-ultra-550b-a55b

선택 파일: backend/app/models/user.py, docs/devlog/members/반소람.md, docs/devlog/members/김윤한.md, .claude/settings.json

**CC 응답** (3/3)

The user is asking me to add a migration for the users table. Let me analyze the context to understand what's needed.

From the context, I can see:
1. `backend/app/models/user.py` - This is the User model file (lines 1-8 shown)
2. Various devlogs showing recent work but not directly related to user table migration

The user wants to add a migration for the users table. Since this is a SQLAlchemy model (based on the imports), they're likely using Alembic for migrations.

Let me first check what the current User model looks like and what might need to be migrated. The context only shows the first 8 lines of the user model, which includes imports but not the actual model definition.

I need to:
1. Look at the full User model to understand the schema
2. Check if there's an existing Alembic setup
3. Determine what migration needs to be created

Since I can't directly read files beyond what's in the context, I should ask for more information or explain what I would need to do.

However, the user is asking me to "add a migration for the users table" - this typically means:
1. Creating an Alembic migration script that creates the

---

### [R-T3] users 테이블 마이그레이션 추가해줘 — deepseek-v4-flash

선택 파일: backend/app/models/user.py, docs/devlog/members/반소람.md, docs/devlog/members/김윤한.md, .claude/settings.json

**CC 응답** (3/3)

We need to analyze the request: "users 테이블 마이그레이션 추가해줘" which means "Add users table migration". The context includes backend/app/models/user.py which shows a SQLAlchemy model for User (likely). The request is to add a migration for the users table. This implies we need to create a database migration file (likely using Alembic) that creates the users table based on the model.

We need to identify the relevant files: likely there is an existing migration directory (e.g., backend/alembic/versions/). We need to check if there is already a migration for users. If not, we need to create one.

But the instruction says: "당신은 사용자의 승인 없이 코드를 직접 수정하지 않는 AI 코딩 어시스턴트입니다." So we must not directly modify code. We need to first explain the impact and proposed changes, then wait for user approval.

We should list the files that would be modified or created, explain the impact (e.g., new migration file, potential conflicts with existing migrations, need to run migration), and then ask for approval.

Also note the risk signals: mention_risk / MEDIUM: DB schema or migration 영향 가능성

---

