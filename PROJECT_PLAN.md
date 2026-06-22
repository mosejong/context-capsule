# Context Capsule Project Plan

## 1. 프로젝트 목적

Context Capsule은 레포와 작업 요청을 분석해 AI 코딩 도구, 팀원, 미래의 나에게 넘길 수 있는 최소 컨텍스트 기반 작업 브리프를 생성하는 RAG 기반 인수인계 도구다.

핵심 목표는 자동 개발이 아니라 **통제 가능한 작업 인수인계**다. AI가 똑똑해지길 기대하는 대신, AI나 사람이 멍청해질 여지를 줄이는 구조를 만든다.

## 2. 문제 정의

AI 코딩 도구나 팀원에게 작업을 맡길 때 다음 문제가 반복된다.

1. 프로젝트 목적과 구조를 매번 다시 설명해야 한다.
2. 관련 파일과 시작점이 불명확하다.
3. DB, 인증, 배포 설정 같은 위험 영역을 쉽게 건드린다.
4. 금지사항과 팀 규칙을 잊는다.
5. 완료 기준이 없어 결과물이 엇나간다.
6. 레포 전체를 찾고 읽느라 토큰과 시간이 낭비된다.

팀 프로젝트에서도 결과가 잘 나오지 않는 이유는 능력 부족보다 작업 범위, 시작점, 완료 기준, 질문해야 할 지점이 명확하지 않은 경우가 많다.

## 3. 해결 방식

Context Capsule은 레포를 스캔하고 작업 요청에 맞는 컨텍스트만 검색한 뒤, 대상별 산출물을 생성한다.

- `AI_HANDOFF_PROMPT.md`
- `TEAMMATE_BRIEF.md`
- `SELF_HANDOFF.md`
- `RISK_CHECKLIST.md`
- `DO_NOT_TOUCH.md`
- `NEXT_TASKS.md`

대상별로 같은 컨텍스트를 다르게 압축한다.

| Target | 목적 | 출력 특징 |
| --- | --- | --- |
| `ai_tool` | Claude/Codex/ChatGPT 작업 정확도 향상 | 수정 범위, 금지사항, 검증 명령, 승인 조건 |
| `teammate` | 팀원에게 실행 가능한 작업 전달 | 오늘 할 일, 먼저 볼 파일, 완료 기준, 질문 목록 |
| `junior_developer` | 막힌 사람이 시작할 수 있게 돕기 | 작은 단계, 예시, 체크리스트, 질문 가이드 |
| `future_me` | 다음날 이어서 작업하기 | 현재 상태, 막힌 점, 다음 작업, 주의사항 |

## 4. MVP 범위

### 포함

- 로컬 레포 경로 입력
- README/docs/code/config 파일 스캔
- 파일 유형 분류
- 작업 요청 기반 관련 파일 검색
- 위험 키워드/파일 패턴 탐지
- Markdown capsule 생성
- Streamlit UI
- Python 3.13 기준 실행 환경

### 제외

- AI 자동 코드 수정
- 외부 LLM API 필수 의존
- GitHub PR 자동 생성
- secret 값 수집
- production DB 접속

## 5. 시스템 구성

```text
Repo Scanner
→ File Classifier
→ Chunk Builder
→ Task-aware Retriever
→ Risk Analyzer
→ Token Budget Analyzer
→ Target-specific Handoff Generator
→ Markdown Output
```

## 6. 토큰 분석기 연동 방향

강사님이 만든 토큰 분석기는 Context Capsule의 평가 장치로 붙인다.

비교할 값:

- 레포 전체 또는 긴 수동 설명을 그대로 넘겼을 때의 예상 토큰 수
- Context Capsule이 생성한 handoff prompt의 예상 토큰 수
- 관련 파일 검색 전후 컨텍스트 크기
- 작업별 평균 절약률

목표 문장:

> 레포 전체를 외부 AI 모델에 반복적으로 설명하지 않고, 로컬 검색과 압축을 통해 작업에 필요한 최소 컨텍스트만 전달한다.

평가 지표:

1. 입력 토큰 감소율
2. 관련 파일 포함률
3. 불필요 파일 제외율
4. 금지사항 보존율
5. 수정 계획 정확도
6. 승인 전 위험 수정 시도 여부

## 7. 자체모델/RAG 확장 계획

### Phase 1: 규칙 기반 MVP

- 파일 확장자 기반 분류
- 키워드 기반 검색
- 위험도 규칙 엔진
- Markdown 템플릿 생성

### Phase 2: Handoff Target

- `handoff_target` 필드 추가
- AI/Human/Self 템플릿 분리
- 팀원용 완료 기준과 질문 목록 생성
- 미래의 나용 작업 상태 요약 생성

### Phase 3: Local RAG

- Sentence Transformers 임베딩
- Chroma 또는 FAISS 벡터 DB
- 작업 요청 기반 top-k retrieval
- 문서/코드 chunk metadata 관리
- 한국어/영어 혼합 레포 대응

### Phase 4: Risk Classifier

작업 요청과 관련 파일을 입력으로 받아 위험도를 분류하는 작은 자체 모델을 학습한다.

| Label | 의미 |
| --- | --- |
| LOW | 문서 수정, 주석 정리, README 개선 |
| MEDIUM | UI 문구, API 호출부, 비핵심 로직 변경 |
| HIGH | DB 스키마, 인증, 결제, 배포 설정 변경 |
| BLOCKED | secret 노출, production data 삭제, 보안 설정 제거 |

### Phase 5: Local LLM / Closed Network

- No-AI Mode: 레포 스캔, 키워드 검색, 위험도 분석, 대상별 브리프 생성
- Local-AI Mode: llama.cpp/Ollama/로컬 임베딩 provider adapter 설계
- External-AI Mode: Claude/Codex/OpenAI handoff prompt 전달
- 모델과 wheel 패키지 사전 반입 방식 정리
- 폐쇄망 설치 번들 설계

### Phase 6: Meeting-to-Execution Pipeline

Status update:

- GitHub Issue body generation: implemented
- Saved output packet under `outputs/YYYYMMDD_HHMMSS_slug/`: implemented

- Discord 회의 결정 입력
- Decision Record 생성
- GitHub Issue body 생성
- AI/팀원/미래의 나 대상별 brief 생성
- approval gate 이후 Claude/Codex adapter 연결

원칙:

- 자동 정리와 자동 준비는 가능하다.
- 자동 코드 수정은 사람 승인 뒤에만 가능하다.
- 자동 merge, production deploy, credential 변경은 하지 않는다.

## 8. 보안/폐쇄망 원칙

1. 기본은 local-first다.
2. `.env`, secret, credential 파일은 기본 제외한다.
3. 외부 API 호출은 선택 기능으로 분리한다.
4. 외부 AI가 없어도 팀원 작업지시서, 내일의 나 메모, 위험 체크리스트, GitHub Issue 본문은 생성되어야 한다.
5. 로컬 임베딩과 로컬 vector DB는 선택 확장이다.
6. LLM 요약이 필요하면 provider adapter를 통해 llama.cpp/Ollama 같은 로컬 런타임을 선택한다.
7. 생성된 capsule을 외부 AI에 보내기 전 사용자가 확인한다.

## 9. 평가 기준

### 검색 품질

- 작업 요청별 관련 파일 top-5 포함 여부
- 불필요 파일 검색 비율

### 위험 감지

- 위험 작업 탐지 정확도
- 금지 파일/환경변수 탐지 여부
- 한 파일 안의 복수 위험 신호 감지 여부

### 출력 품질

- AI에게 바로 넘길 수 있는 프롬프트인가
- 팀원이 바로 시작할 수 있는 작업 지시인가
- 미래의 내가 다음날 이어서 볼 수 있는가
- 사람이 승인/거절 판단을 할 수 있는가
- 추정과 사실이 구분되는가

### 토큰 효율

- 수동 설명 대비 capsule 토큰 수 감소율
- 검색된 chunk 수 대비 최종 prompt 크기
- 모델별 handoff prompt 길이 비교

## 10. 샘플 테스트셋

초기 테스트셋은 사용자가 직접 만든 프로젝트를 기준으로 구성한다.

- Rainbow Bridge
- SchoolBridge 관련 실험 레포
- procurement-logistics-ai
- context-capsule 자체 레포

작업 요청 예시:

```text
로그인 API 오류를 수정하려고 한다.
README를 포트폴리오용으로 다듬고 싶다.
DB schema 변경 없이 mission API 응답만 개선하고 싶다.
Docker 배포 설정을 확인하고 싶다.
팀원이 미션 기능에서 막혔는데 오늘 할 수 있는 작업으로 쪼개고 싶다.
내일 이어서 작업할 수 있게 현재 상태를 정리하고 싶다.
```

## 11. 포트폴리오 포인트

이 프로젝트는 단순한 AI 활용 서비스가 아니라, AI 코딩 도구를 더 안전하고 효율적으로 사용하기 위한 **메타 개발 도구**다.

보여줄 수 있는 역량:

- RAG 기반 컨텍스트 검색 설계
- 레포 구조 분석
- 작업 위험도 분류
- 토큰 사용량 최적화 실험
- human-in-the-loop AI 워크플로우 설계
- 팀원/주니어 개발자를 위한 작업 브리프 설계
- 폐쇄망에서도 확장 가능한 local-first 구조 설계
- 실제 개발 과정에서 발생한 문제를 제품화하는 능력
