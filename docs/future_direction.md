# Future Direction

이 문서는 Context Capsule의 앞으로 작업 방향을 정리한다. 핵심은 단순한 README 요약기가 아니라, **작업을 잘 넘기기 위한 컨텍스트 압축기**로 발전시키는 것이다.

## 1. 제품 정체성

Context Capsule은 "AI에게 일을 잘 시키는 법"을 제품으로 만든 프로젝트다.

더 정확히는 다음 역할을 한다.

```text
대충 나온 요청, 에러 로그, 채팅 기록
        ↓
레포 컨텍스트와 연결
        ↓
관련 파일, 위험 영역, 완료 기준 추출
        ↓
AI/팀원/미래의 나에게 줄 작업 브리프로 변환
```

한 줄 정의:

> Context Capsule은 레포 전체를 AI에게 넘기지 않고, 작업 요청에 필요한 최소 컨텍스트와 안전 규칙만 검색·압축해 작업 명세서로 변환하는 로컬 RAG 기반 프롬프트 컴파일러다.

## 2. 가장 먼저 할 일

### 2.1 위험 분석 테스트 수정

현재 확인된 테스트 실패가 있다.

```text
tests/test_risk_analyzer.py::test_detects_auth_and_env_risk
```

원인:

- `risk_analyzer.py`가 chunk 하나에서 첫 번째 위험 규칙만 잡고 다음 chunk로 넘어간다.
- `jwt token login password`에서 `token`이 먼저 BLOCKED로 잡혀 auth/login/password 기반 HIGH가 누락된다.

방향:

- 한 chunk에서 복수 위험 finding을 감지하게 수정한다.
- secret/env BLOCKED와 auth HIGH는 동시에 보여주는 것이 안전하다.

### 2.2 의존성 분리

현재 `requirements.txt`는 MVP 실행용 패키지와 Phase 2/4 확장 패키지를 한 번에 설치한다.

문제:

- `sentence-transformers` 때문에 `torch`까지 설치되어 무겁다.
- 단순 Streamlit MVP 실행에도 설치 시간이 길다.

방향:

```text
requirements.txt          # MVP 실행
requirements-dev.txt      # pytest, lint
requirements-rag.txt      # chromadb, sentence-transformers, torch
requirements-local-llm.txt # provider adapter notes
```

## 3. 기능 확장 순서

### Phase A: Handoff Target

`CapsuleInput`에 `handoff_target`을 추가한다.

```text
ai_tool
teammate
junior_developer
future_me
```

각 target별 출력 템플릿을 분리한다.

- AI: 수정 범위, 금지사항, 먼저 계획 보고, 테스트 명령
- 팀원: 오늘 할 일, 먼저 볼 파일, 완료 기준, 질문 목록
- 미래의 나: 현재 상태, 막힌 점, 다음 작업, 주의사항

### Phase B: Token Analyzer

강사님 토큰 분석기와 결합한다.

목표:

- 수동 설명 대비 Context Capsule prompt가 얼마나 줄었는지 보여준다.
- "토큰을 아낀다"는 주장을 숫자로 증명한다.

표시 예시:

```text
Original context estimate: 18,420 tokens
Capsule prompt estimate: 3,180 tokens
Estimated reduction: 82.7%
```

### Phase C: Chat-to-Capsule Mode

디스코드, GPT 대화, 에러 로그를 붙여넣으면 작업 요청을 추출한다.

Status: MVP implemented.

예시:

```text
"어떤 에러났는데 뭐야?"
```

출력:

```text
관련 파일:
- app/analyzers/risk_analyzer.py
- tests/test_risk_analyzer.py

에러:
- 기대값 HIGH/BLOCKED 중 HIGH 누락

수정 방향:
- chunk 하나에서 여러 위험 규칙을 감지하게 변경

검증:
- python -m pytest -q
```

### Phase C-2: Meeting-to-Execution Pipeline

Discord 회의에서 "이걸로 가자"가 확정되면 바로 실행 가능한 작업 패킷을 만든다.

Status: packet MVP implemented. Discord/GitHub API adapters remain.

출력:

- Decision Record
- GitHub Issue body
- AI handoff prompt
- Teammate brief
- Risk checklist
- Token budget report

원칙:

- Discord bot은 회의 결정 수집기 역할을 한다.
- Context Capsule은 레포 컨텍스트와 위험도를 붙여 작업 패킷으로 바꾼다.
- Claude/Codex 자동 착수는 approval gate 이후에만 실행한다.
- 자동 merge는 하지 않는다.

### Phase D: Local RAG

키워드 검색을 Chroma/FAISS 기반 검색으로 확장한다.

우선순위:

1. chunk metadata 설계
2. 로컬 임베딩 모델 선택
3. top-k 검색 품질 평가
4. 한국어/영어 혼합 문서 대응

### Phase E: Closed Network Mode

폐쇄망에서도 외부 AI API 없이 핵심 인수인계 기능이 살아있도록 설치와 실행 경로를 분리한다.

정의:

> Closed Network Mode는 AI 없이도 작업 인수인계 패킷을 만들 수 있는 모드다. 로컬 LLM이 있으면 요약까지 가능하지만, 없어도 팀원용 작업지시서, 내일의 나용 메모, 위험 체크리스트, GitHub Issue 본문은 생성되어야 한다.

필요 작업:

- offline wheel bundle
- 사전 다운로드 모델 폴더
- 외부 API 호출 차단 옵션
- secret redaction 강화
- README_OFFLINE.md

## 4. 발표/포트폴리오 메시지

강하게 밀 문장:

> Context Capsule은 막연한 작업 요청을 레포 기반 실행 브리프로 변환해, AI 코딩 도구가 더 적은 토큰으로 더 정확하게 작업하도록 돕는 프롬프트 컴파일러입니다.

사람용 확장 문장:

> Context Capsule은 AI 코딩 도구뿐 아니라 팀원과 주니어 개발자에게도 명확한 작업 브리프를 전달할 수 있도록, 레포 컨텍스트·위험 영역·완료 기준·질문 목록을 자동으로 구조화합니다.

폐쇄망/보안 문장:

> 폐쇄망에서도 레포 스캔, 작업 브리프 생성, 위험도 분석, 개발일지 생성은 외부 API 없이 동작합니다. AI 연동은 선택 기능이며, 폐쇄망에서는 로컬 LLM이 있을 때만 사용할 수 있습니다.

## 5. 조심할 표현

피해야 할 표현:

- "Sonnet을 Opus 성능으로 만든다."
- "무조건 토큰을 줄인다."
- "AI가 자동으로 안전하게 수정한다."

권장 표현:

- "모델이 헷갈릴 여지를 줄인다."
- "작업 관련 최소 컨텍스트만 전달한다."
- "토큰 사용량과 작업 실패 가능성을 줄이는 것을 목표로 한다."
- "위험 변경은 사람 승인 전까지 보류한다."

## 6. Codex 작업 원칙

이 레포를 작업할 때 Codex는 다음 원칙을 지킨다.

1. 문서/코드 수정 전 현재 git 상태를 확인한다.
2. 실행 오류가 나면 바로 고치지 않고 원인, 수정안, 영향 파일을 먼저 정리한다.
3. 위험도 분석, secret 처리, 토큰 분석 로직은 테스트를 같이 갱신한다.
4. 로컬 우선, 폐쇄망 가능성, human-in-the-loop 원칙을 흔들지 않는다.
5. 기능을 늘릴 때도 "작업을 잘 넘기기 위한 컨텍스트 압축"이라는 중심을 유지한다.
