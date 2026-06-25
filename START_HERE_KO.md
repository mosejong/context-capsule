# 처음 읽어주세요

Context Capsule을 처음 실행하는 KDT 테스터용 한국어 안내입니다.

## 1. 먼저 이것만 하세요

```text
1. ZIP 압축을 풉니다.
2. run_context_capsule.bat 를 더블클릭합니다.
3. 브라우저에서 http://localhost:8501 을 엽니다.
4. Local repository path에 테스트할 프로젝트 폴더를 넣습니다.
5. `작업 하나 넘기기`에서 `작업 요청 입력칸`에 아래 문장 중 하나를 넣고 `작업 패킷 생성`을 누릅니다.
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

대시보드의 `Token Evidence`는 아래처럼 읽으면 됩니다.

```text
Candidate files
검색으로 잡힌 후보 파일 전체 내용을 AI에게 그대로 붙인다고 가정한 토큰

Handoff prompt
Context Capsule이 만든 복붙용 작업 브리프 토큰

Reduction
후보 파일 전체 대신 handoff prompt만 넘길 때 줄어드는 것으로 추정되는 비율
```

중요:

```text
이 숫자는 실제 Claude/GPT 결제 토큰이 아니라 로컬 추정치입니다.
그래도 "프롬프트가 무엇을 얼마나 압축했는지"를 보는 데는 쓸 수 있습니다.
```

더 자세한 설명은 `docs/token_evidence.md`를 보세요.

## 3. 결과에서 볼 것

대시보드에서 생성 버튼을 누르면 결과 영역에 생성 상태가 뜹니다.

완료 후에는 이 탭을 보면 됩니다.

```text
요약
- Context Capsule이 요청을 어떻게 이해했는지 확인

관련 파일
- AI나 팀원이 먼저 볼 후보 파일 확인

AI용 프롬프트
- Claude, Codex, ChatGPT에 복붙할 프롬프트

작업 흐름
- 레포 스캔, 요청 해석, 검색, 위험 분석, 승인 게이트가 어떻게 지나갔는지 확인

팀원용 / 내일의 나
- 팀원이나 미래의 나에게 넘길 메모

위험/승인
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

## 5. v0.2 협업 모드도 테스트해보세요

v0.2는 단일 작업 요청뿐 아니라 회의/스크럼/아이디어 회의를 작업 패킷으로 바꾸는 흐름을 테스트합니다.

첫 화면의 큰 카드에서 아래 모드를 선택할 수 있습니다.

```text
회의록 정리
프로젝트 시작 정리
준비도 점검
```

확인할 것:

```text
결정사항이 잡히는지
막힌 점이 잡히는지
다음 작업이 작게 쪼개지는지
GitHub Issue 초안이 쓸만한지
역할 논의 질문이 사람 평가처럼 보이지 않는지
자동 배정/자동 평가 금지 문구가 보이는지
MVP/프로토타입 준비도가 납득 가능한지
내 파트인지 다른 사람 파트인지 확인 질문이 나오는지
```

주의:

```text
Context Capsule은 팀원을 평가하거나 자동 배정하지 않습니다.
회의 내용을 정리하고 팀장이 물어볼 질문을 제안할 뿐입니다.
```

## 6. 피드백 줄 때 필요한 것

아래 양식으로 보내주면 제일 좋습니다.

```text
[Context Capsule Beta Feedback]
Version: v0.2.3
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

## 7. 더 자세한 문서

```text
README.md
docs/kdt_beta_quickstart.md
docs/local_app.md
docs/project_health_check.md
docs/workflow_graph.md
docs/releases/v0.2.3.md
```

## 8. v0.2.2+ 피드백 저장 기능

테스트하다가 결과가 이상하거나 헷갈리면 Discord에만 적지 말고, 대시보드 아래의 `이 결과가 이상했나요?` 영역에도 남겨주세요.

적으면 좋은 내용:

```text
기대한 파일:
실제로 나온 top files:
헷갈린 화면/버튼/탭:
토큰 설명이 이해됐는지:
위험 경고가 적절했는지:
다시 쓸 의향:
```

Context Capsule은 이 피드백을 `outputs/feedback` 아래에 `FEEDBACK.md`와 `feedback.json`으로 저장합니다.

나중에 `피드백 리뷰` 탭을 누르면 저장된 피드백을 모아서 다음 패치 우선순위와 회귀 테스트 후보를 뽑을 수 있습니다.

주의:

```text
피드백 리뷰는 팀원 평가가 아닙니다.
자동 역할 배정이 아닙니다.
자동 수정이 아닙니다.
다음 개선점을 정리하기 위한 참고 자료입니다.
```

영어 문서가 부담되면 이 파일부터 보면 됩니다.
