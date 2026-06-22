# Context Capsule Project Plan

## 1. 프로젝트 목적

Context Capsule은 AI 코딩 도구에 레포를 넘기기 전에 필요한 프로젝트 맥락, 관련 파일, 위험 영역, 금지사항, 승인 체크리스트를 하나의 작업 패킷으로 정리하는 도구다.

핵심 목표는 자동 개발이 아니라 **통제 가능한 AI 협업**이다.

## 2. 문제 정의

AI 코딩 도구를 사용할 때 다음 문제가 반복된다.

1. 프로젝트 목적과 구조를 매번 다시 설명해야 한다.
2. AI가 관련 없는 파일을 수정한다.
3. DB, 인증, 배포 설정 같은 위험 영역을 쉽게 건드린다.
4. 사용자가 금지한 규칙을 잊는다.
5. 작업 범위가 커지고 검토 비용이 증가한다.

## 3. 해결 방식

Context Capsule은 레포를 스캔하고 작업 요청에 맞는 컨텍스트만 검색한 뒤, 다음 산출물을 생성한다.

- `PROJECT_CONTEXT.md`
- `AI_HANDOFF_PROMPT.md`
- `RISK_CHECKLIST.md`
- `DO_NOT_TOUCH.md`
- `NEXT_TASKS.md`

## 4. MVP 범위

### 포함

- 로컬 레포 경로 입력
- README/docs/code/config 파일 스캔
- 파일 유형 분류
- 작업 요청 기반 관련 파일 검색
- 위험 키워드/파일 패턴 탐지
- Markdown capsule 생성
- Streamlit UI

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
→ Capsule Generator
→ Markdown Output
```

## 6. 자체모델/RAG 확장 계획

### Phase 1: 규칙 기반 MVP

- 파일 확장자 기반 분류
- 키워드 기반 검색
- 위험도 규칙 엔진

### Phase 2: Local RAG

- Sentence Transformers 임베딩
- Chroma 또는 FAISS 벡터 DB
- 작업 요청 기반 top-k retrieval
- 문서/코드 chunk metadata 관리

### Phase 3: Risk Classifier

작업 요청과 관련 파일을 입력으로 받아 위험도를 분류하는 작은 자체 모델을 학습한다.

라벨 예시:

| Label | 의미 |
| --- | --- |
| LOW | 문서 수정, 주석 정리, README 개선 |
| MEDIUM | UI 문구, API 호출부, 비핵심 로직 변경 |
| HIGH | DB 스키마, 인증, 결제, 배포 설정 변경 |
| BLOCKED | secret 노출, production data 삭제, 보안 설정 제거 |

### Phase 4: Local LLM

- Ollama 기반 로컬 LLM 연동
- 생성 품질 비교
- 외부 API 없는 실행 옵션 제공

## 7. 평가 기준

### 검색 품질

- 작업 요청별 관련 파일 top-5 포함 여부
- 불필요 파일 검색 비율

### 위험 감지

- 위험 작업 탐지 정확도
- 금지 파일/환경변수 탐지 여부

### 출력 품질

- AI에게 바로 넘길 수 있는 프롬프트인가
- 사람이 승인/거절 판단을 할 수 있는가
- 추정과 사실이 구분되는가

## 8. 샘플 테스트셋

초기 테스트셋은 사용자가 직접 만든 프로젝트를 기준으로 구성한다.

- Rainbow Bridge
- SchoolBridge 관련 실험 레포
- procurement-logistics-ai

작업 요청 예시:

```text
로그인 API 오류를 수정하려고 한다.
README를 포트폴리오용으로 다듬고 싶다.
DB schema 변경 없이 mission API 응답만 개선하고 싶다.
Docker 배포 설정을 확인하고 싶다.
```

## 9. 포트폴리오 포인트

이 프로젝트는 다음 역량을 보여준다.

- RAG 기반 컨텍스트 검색 설계
- 레포 구조 분석
- 작업 위험도 분류
- human-in-the-loop AI 워크플로우 설계
- 외부 API 없이 로컬 모델로 확장 가능한 구조 설계
- 실제 개발 과정에서 발생한 문제를 제품화하는 능력
