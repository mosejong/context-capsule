# 처음 읽어주세요

Context Capsule을 처음 실행하는 KDT 테스터용 한국어 안내입니다.

## 1. 먼저 이것만 하세요

```text
1. ZIP 압축을 풉니다.
2. run_context_capsule.bat 를 더블클릭합니다.
3. 브라우저에서 http://localhost:8501 을 엽니다.
4. Local repository path에 테스트할 프로젝트 폴더를 넣습니다.
5. Task request에 아래 문장 중 하나를 넣고 Generate Capsule을 누릅니다.
```

추천 테스트 문장:

```text
리드미 손보자
로컬 실행 안돼
로그인이 모바일에서만 안돼
auth는 건드리지 말고 문서만 바꾸자
이거 왜그래?
```

터미널 명령어는 선택사항입니다. 첫 테스트는 대시보드만 써도 됩니다.

## 2. 이 도구가 토큰을 줄이는 방식

Context Capsule이 실제 Claude/GPT 요금을 직접 줄여주는 것은 아닙니다.

대신 작업 요청을 먼저 해석해서 관련 파일 후보와 위험 영역만 골라낸 뒤, AI에게 넘길 프롬프트를 작게 만듭니다.

예를 들어 그냥 AI에게 이렇게 말하면:

```text
이 프로젝트 전체 보고 로그인 오류 고쳐줘
```

AI가 README, 문서, 코드, 설정을 넓게 보면서 토큰을 많이 쓸 수 있습니다.

Context Capsule을 쓰면:

```text
관련 파일:
- backend/auth/login.py
- frontend/src/api/auth.ts

건드리지 말 것:
- .env
- DB schema
- JWT secret

요청:
먼저 원인 후보와 수정 계획만 제안하세요.
```

이런 식으로 AI가 볼 범위와 금지사항을 먼저 좁혀줍니다.

현재 토큰 수치는 `Estimated only`입니다. 실제 Claude/GPT provider 사용량과 완전히 같은 값이 아니며, 나중에 Token Analyzer adapter로 정밀 비교할 예정입니다.

## 3. 결과에서 볼 것

대시보드에서 Generate Capsule을 누르면 결과 영역에 생성 상태가 뜹니다.

완료 후에는 이 탭을 보면 됩니다.

```text
Overview
- Context Capsule이 요청을 어떻게 이해했는지 확인

AI Handoff
- Claude, Codex, ChatGPT에 복붙할 프롬프트

Junior Guide
- 주니어/팀원이 바로 시작할 수 있게 쪼갠 작업 안내

Risk & Approval
- 위험 파일, 금지 영역, 사람 승인 체크리스트

GitHub Issue
- 이슈 초안
```

## 4. 인덱스는 꼭 해야 하나요?

아니요.

인덱스 없이도 기본 keyword/path 검색으로 동작합니다.

인덱스는 같은 레포를 여러 번 테스트할 때 검색 후보를 재사용하기 위한 선택 기능입니다.

```powershell
.\context_capsule_cli.bat index --repo-path . --json
```

doctor에서 `Index not built yet`가 WARN으로 떠도 첫 테스트를 막는 오류는 아닙니다.

## 5. 피드백 줄 때 필요한 것

아래 양식으로 보내주면 제일 좋습니다.

```text
[Context Capsule Beta Feedback]
Version: v0.1.8
OS / Python:
사용한 레포:

입력한 문장:

기대한 파일:

실제 top files:

Risk 결과:

헷갈린 부분:

다시 쓸 의향:
```

중요:

```text
.env
API token
GitHub token
개인정보
회사/팀 비공개 코드
```

이런 값은 피드백에 붙이지 마세요. Context Capsule은 시크릿처럼 보이는 값은 최대한 `[REDACTED_SECRET]`로 가리지만, 원본을 직접 공유하지 않는 것이 가장 안전합니다.

## 6. 더 자세한 문서

```text
README.md
docs/kdt_beta_quickstart.md
docs/local_app.md
docs/releases/v0.1.8.md
```

영어 문서가 부담되면 이 파일부터 보면 됩니다.
