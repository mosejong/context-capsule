# Sample Capsule — Rainbow Bridge

> 이 문서는 Context Capsule이 생성할 수 있는 출력 예시다. 실제 자동 생성 결과가 아니라 MVP 설계를 설명하기 위한 샘플이다.

## Project Summary

Rainbow Bridge는 펫로스 보호자를 위한 AI 애프터케어 서비스다. 감정 체크인, AI 추모 메시지, TTS/GIF, 회복 미션, 타임라인, 회복 리포트 기능을 하나의 사용자 흐름으로 연결한다.

## Task Request

로그인 API가 서버 터미널에서는 정상인데 모바일 앱에서는 실패하는 문제를 분석하고, AI 코딩 도구에 넘길 작업 브리프를 생성한다.

## Retrieved Context

- `backend/auth/router.py:1-80`
- `backend/models/user.py:1-120`
- `frontend/src/api/client.ts:1-60`
- `frontend/src/pages/Login.tsx:1-140`
- `docker-compose.yml:1-70`
- `nginx/sites-enabled/rainbow.conf:1-80`
- `.env.example:1-40`

## Risk Findings

- **HIGH** — 인증/JWT 로직 영향 가능성 / `backend/auth/router.py`
- **MEDIUM** — API 응답 형식 변경 가능성 / `frontend/src/pages/Login.tsx`
- **HIGH** — 배포/프록시 설정 영향 가능성 / `nginx/sites-enabled/rainbow.conf`
- **BLOCKED** — secret/env 변경 또는 노출 가능성 / `.env.example`

## Human Approval Checklist

- [ ] 서버 터미널 로그인 성공과 모바일 로그인 실패가 같은 API base URL을 사용하는지 확인했는가?
- [ ] HTTPS/nginx 프록시 경로와 Expo 앱의 API URL이 일치하는가?
- [ ] JWT secret 또는 실제 환경변수를 출력하지 않았는가?
- [ ] API 응답 스키마를 바꿀 경우 프론트 로그인 처리 영향도를 설명했는가?
- [ ] 수정 전 변경 파일 목록을 사용자에게 먼저 제시했는가?

## AI Handoff Prompt

```text
당신은 사용자의 승인 없이 코드를 직접 수정하지 않는 AI 코딩 어시스턴트입니다.

작업 요청:
로그인 API가 서버 터미널에서는 정상인데 모바일 앱에서는 실패하는 문제를 분석하세요.

관련 컨텍스트:
- backend/auth/router.py
- backend/models/user.py
- frontend/src/api/client.ts
- frontend/src/pages/Login.tsx
- docker-compose.yml
- nginx/sites-enabled/rainbow.conf

주의사항:
- JWT secret과 실제 .env 값은 출력하거나 수정하지 마세요.
- API 응답 구조를 바꾸기 전 프론트 영향도를 설명하세요.
- nginx/HTTPS 설정을 바꿀 경우 배포 영향도를 설명하세요.
- 수정안을 바로 적용하지 말고, 원인 후보와 확인 순서를 먼저 제시하세요.

응답 형식:
1. 원인 후보
2. 확인할 파일과 이유
3. 수정 후보
4. 위험도
5. 사용자 승인 필요 여부
```
