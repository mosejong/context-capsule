# Architecture

Context Capsule은 레포 전체를 LLM에 한 번에 던지는 방식이 아니라, 작업 요청에 필요한 컨텍스트만 로컬에서 검색하고 압축해 대상별 작업 브리프를 조립하는 구조를 지향한다.

현재 MVP는 키워드/규칙 기반 검색으로 시작한다. 이후 Chroma/FAISS와 로컬 임베딩 모델을 붙여 RAG 기반 검색으로 확장한다.

## 1. High-level Flow

```text
User Task Request / Chat Log
        ↓
Repository Scan
        ↓
File Classification
        ↓
Chunking
        ↓
Task-aware Retrieval
        ↓
Risk Analysis
        ↓
Token Budget Analysis
        ↓
Target-specific Capsule Generation
        ↓
AI / Human / Self Handoff
```

## 2. Components

### Repo Scanner

로컬 레포에서 문서, 코드, 설정 파일을 수집한다.

- README/docs 문서
- Python/JS/TS 등 코드 파일
- requirements, package, docker-compose 등 설정 파일
- 테스트 파일
- 최근 git log와 변경 파일 목록

수집 제외 대상:

- `.git`
- `.venv`
- `node_modules`
- `dist`, `build`
- 대용량 파일
- `.env`, secret, credential 계열 파일

### File Classifier

파일 확장자와 파일명을 기준으로 유형을 나눈다.

| Kind | Example |
| --- | --- |
| doc | README.md, docs/*.md |
| code | *.py, *.js, *.tsx |
| config | Dockerfile, requirements.txt, package.json |
| test | test_*.py, *.spec.ts |
| history | git log, changed files |

### Chunk Builder

파일을 검색 가능한 단위로 나눈다.

초기 MVP는 단순 라인/문단 chunk를 사용한다. 이후에는 파일 유형별 전략을 나눈다.

- Markdown: heading 단위
- Python/JS/TS: 함수, 클래스, import, 라우터 단위
- Config: key/value 또는 section 단위
- Git history: commit message와 changed path 단위

### Retriever

MVP에서는 키워드 기반 검색을 사용한다. Phase 2에서는 Chroma/FAISS 기반 vector search로 확장한다.

검색 기준:

- 작업 요청과 일치하는 단어
- 파일 경로 힌트(auth, router, schema, docker 등)
- README/CONTRIBUTION 같은 설명 문서 가중치
- 최근 변경 파일 가중치
- 사용자가 지정한 금지 규칙과 관련된 파일

### Risk Analyzer

작업 요청과 검색된 chunk에서 위험 신호를 감지한다.

위험 영역:

- secret/env/credential
- auth/JWT/login/password
- DB schema/migration/model
- docker/nginx/deploy/SSL
- API response/router/endpoint
- production data

한 파일 안에 여러 위험 신호가 있을 수 있으므로, 최종 구조는 파일당 하나의 risk만 고르지 않고 복수 finding을 보존하는 방향이 맞다.

### Token Budget Analyzer

현재 MVP에서는 외부 의존성 없는 로컬 추정 방식으로 동작한다. 이후 강사님 토큰 분석기나 모델별 tokenizer가 있으면 같은 역할에 더 정확한 계산기를 붙인다.

역할:

- 원본 컨텍스트 예상 토큰 수 계산
- 검색된 chunk의 예상 토큰 수 계산
- 최종 capsule의 예상 토큰 수 계산
- 수동 설명 대비 절약률 표시

이 컴포넌트는 "토큰을 아낀다"는 주장을 실험 가능한 지표로 바꿔준다.

### Target-specific Capsule Generator

최종 Markdown 패킷을 생성한다.

공통 포함 내용:

- Task Request
- Retrieved Context
- Risk Findings
- Do Not Touch
- Completion Criteria
- Verification Commands
- Human Approval Checklist

대상별 차이:

| Target | 강조점 |
| --- | --- |
| AI Handoff | 수정 범위, 금지사항, 먼저 계획 보고, 테스트 명령 |
| Human Handoff | 오늘 할 수 있는 단위, 먼저 볼 파일, 완료 기준, 질문 목록 |
| Self Handoff | 현재 상태, 막힌 점, 다음 작업, 주의사항 |

## 3. Models and Technologies

이 프로젝트에서 말하는 "모델"은 하나가 아니다. 역할별로 작은 모델과 도구를 조합한다.

```text
검색 품질을 높이는 모델      → embedding model
검색 결과를 저장/찾는 기술   → vector DB
위험도를 분류하는 모델       → risk classifier
출력 문장을 다듬는 모델      → optional local LLM provider
토큰 사용량을 계산하는 도구  → tokenizer / token analyzer
```

### Python 3.13

프로젝트 기본 런타임이다.

역할:

- 로컬 레포 스캔
- 파일 분류와 chunk 생성
- 위험도 분석
- Streamlit UI 실행
- RAG/vector DB 연동

선택 이유:

- 개인 프로젝트와 포트폴리오에서 설명하기 쉽다.
- AI/RAG 생태계 라이브러리가 풍부하다.
- 폐쇄망에서도 wheel bundle을 준비하면 실행 경로를 만들 수 있다.

### Streamlit

초기 MVP UI다.

역할:

- 로컬 레포 경로 입력
- 작업 요청 입력
- 금지/주의 규칙 입력
- handoff target 선택
- capsule markdown 출력
- 토큰 예산과 위험 체크리스트 표시

선택 이유:

- FastAPI + frontend를 따로 만들기 전 빠르게 시연 가능하다.
- "프로토타입이 실제로 돈다"는 느낌을 주기 좋다.

### Pydantic

입출력 schema를 고정하는 데 사용한다.

주요 schema:

- `RepoFile`
- `RepoChunk`
- `RiskFinding`
- `CapsuleInput`
- `CapsuleOutput`

선택 이유:

- generator, retriever, analyzer 사이의 데이터 계약을 명확히 한다.
- 나중에 FastAPI로 옮겨도 같은 schema를 재사용할 수 있다.

### Keyword Retriever

현재 MVP의 검색 방식이다.

역할:

- 작업 요청에서 키워드를 뽑는다.
- 파일 경로와 chunk text를 비교한다.
- 관련도가 높은 chunk를 top-k로 반환한다.

장점:

- 외부 모델 없이 바로 동작한다.
- 폐쇄망에서도 가볍다.
- 동작을 설명하기 쉽다.

한계:

- 의미가 비슷하지만 단어가 다른 경우를 잘 못 찾는다.
- 한국어 요청과 영어 코드 사이 연결이 약할 수 있다.

### Embedding Model

Phase 2에서 붙일 핵심 모델이다. 문서와 코드 조각을 숫자 벡터로 바꿔 "의미가 비슷한 것"을 찾게 해준다.

후보:

| Model | 용도 | 특징 |
| --- | --- | --- |
| `intfloat/multilingual-e5-small` | 한국어/영어 혼합 검색 | 가볍고 다국어 검색 baseline으로 적합 |
| `BAAI/bge-m3` | 품질 중심 다국어 검색 | 성능 기대치는 높지만 상대적으로 무거움 |
| `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` | 빠른 다국어 baseline | 가볍게 실험하기 좋음 |
| `nomic-embed-text` | 로컬 런타임 친화 검색 | 로컬 실행 흐름과 맞추기 쉬움 |

이 프로젝트에서는 처음부터 큰 모델을 쓰지 않는다. 먼저 작은 multilingual embedding으로 검색 품질을 확인하고, 필요할 때 더 큰 모델을 비교한다.

### Vector DB: Chroma / FAISS

embedding vector를 저장하고 검색하는 계층이다.

#### Chroma

역할:

- chunk text와 metadata를 함께 저장
- path, kind, line range 같은 metadata filter 지원
- 로컬 persistent DB로 사용 가능

적합한 경우:

- 프로토타입에서 빠르게 RAG 검색을 붙이고 싶을 때
- metadata 기반 필터링이 필요할 때
- 사용법을 포트폴리오에서 설명하기 쉽게 가져가고 싶을 때

#### FAISS

역할:

- vector similarity search를 빠르게 수행
- 대량 vector 검색에 강함

적합한 경우:

- 검색 성능과 속도를 더 직접 제어하고 싶을 때
- metadata 저장은 별도 SQLite/JSON으로 관리해도 될 때
- 폐쇄망에서 단순하고 빠른 검색 엔진이 필요할 때

초기 판단:

- MVP 다음 단계는 Chroma가 더 편하다.
- 검색 성능 실험 단계에서는 FAISS도 비교 후보로 남긴다.

### Token Analyzer

현재 MVP에서는 외부 의존성 없는 로컬 추정 방식으로 동작한다. 이후 강사님 토큰 분석기나 모델별 tokenizer가 있으면 같은 역할에 더 정확한 계산기를 붙인다.

역할:

- 레포 전체 또는 수동 설명의 예상 토큰 수 계산
- 검색된 chunk의 예상 토큰 수 계산
- 최종 capsule prompt의 예상 토큰 수 계산
- 절약률 표시

예시:

```text
Original context estimate: 18,420 tokens
Capsule prompt estimate: 3,180 tokens
Estimated reduction: 82.7%
```

중요한 점:

- "토큰이 줄어든다"는 주장을 감으로 말하지 않는다.
- 같은 작업 요청에서 before/after를 비교해 수치로 보여준다.
- 모델별 tokenizer가 있으면 해당 tokenizer를 쓰고, 없으면 근사 추정으로 표시한다.

### Risk Classifier

현재는 규칙 기반 `Risk Analyzer`가 담당한다. 이후 작은 자체 모델로 확장할 수 있다.

초기 규칙 기반:

- `secret`, `.env`, `api_key`, `token` → BLOCKED 후보
- `auth`, `jwt`, `login`, `password` → HIGH 후보
- `schema`, `migration`, `database` → HIGH 후보
- `router`, `endpoint`, `response` → MEDIUM 후보

모델 확장 후보:

| Approach | 설명 | 장점 |
| --- | --- | --- |
| TF-IDF + Logistic Regression | 작업 요청과 파일 힌트로 위험도 분류 | 작고 빠르며 설명 가능 |
| TF-IDF + Linear SVM | 짧은 텍스트 분류 baseline | 데이터가 적어도 baseline으로 좋음 |
| 작은 transformer classifier | 라벨 데이터가 쌓인 뒤 fine-tuning | 문맥 이해가 더 좋을 수 있음 |

이 프로젝트에서는 처음부터 복잡한 모델을 학습하지 않는다. 규칙 기반으로 라벨 데이터를 모으고, 그 데이터로 작은 분류기를 붙이는 순서가 현실적이다.

### Local LLM Provider Adapter

외부 API 없이 요약과 문장 압축을 수행하기 위한 선택 컴포넌트다.

역할:

- 검색된 chunk를 더 짧게 요약
- AI/팀원/미래의 나 target별 문체 조정
- chat log에서 작업 의도 추출
- 폐쇄망에서 외부 API 없이 capsule 생성 품질 개선

후보 런타임:

| Provider | 장점 | 주의점 |
| --- | --- | --- |
| llama.cpp | GGUF 기반으로 단순하고 폐쇄망 배포에 유리함 | 모델 파일과 옵션을 직접 관리해야 함 |
| Ollama | 설치와 모델 실행 경험이 편하고 REST API가 단순함 | 편의성 중심 도구라 성능/운영 제어는 제한될 수 있음 |
| vLLM | GPU 서버에서 처리량 중심 serving에 강함 | 개인 PC/폐쇄망 가벼운 MVP에는 과할 수 있음 |
| Transformers | 모델 실험과 fine-tuning 흐름에 유리함 | serving/배포 계층은 별도 설계가 필요함 |

주의:

- MVP 필수 의존성이 아니다.
- 특정 provider에 종속되면 폐쇄망/성능/설치 환경에서 리스크가 커진다.
- 로컬 LLM도 내부적으로는 토큰을 사용하지만 외부 API 과금 토큰은 아니다.
- CPU 환경에서는 느릴 수 있으므로, 핵심 검색/위험 분석은 LLM 없이도 동작해야 한다.

설계 원칙:

```text
LocalLLMProvider
  summarize(chunks) -> str
  extract_task(chat_log) -> str
  rewrite_for_target(prompt, target) -> str
```

초기 구현은 provider 없이 템플릿으로 동작한다. 이후 필요할 때 `llama.cpp`, `Ollama`, `vLLM` 같은 provider를 adapter로 붙인다.

### pytest

품질 기준을 고정하는 테스트 도구다.

현재 테스트 대상:

- 위험도 분석
- 대상별 handoff prompt 생성

앞으로 테스트할 것:

- token analyzer 계산
- handoff target별 출력 형식
- secret redaction
- retriever top-k 품질
- closed network mode에서 외부 API 호출 금지

### Meeting-to-Execution Integration

Discord 회의에서 확정된 아이디어를 작업 착수 단위로 바꾸는 확장 계층이다.

역할:

- Discord message, slash command, pasted chat log를 decision input으로 받는다.
- decision record를 생성한다.
- 기존 retrieval/risk/token pipeline을 실행한다.
- GitHub Issue body, AI handoff prompt, teammate brief를 만든다.
- approval gate를 통과한 작업만 Claude/Codex adapter로 넘긴다.

초기 구현은 외부 AI를 직접 실행하지 않고 prompt export와 GitHub Issue markdown 생성까지만 담당한다.

안전 원칙:

- HIGH/BLOCKED risk는 자동 착수하지 않는다.
- 자동 merge/deploy/credential 변경은 금지한다.
- Discord 원문과 GitHub Issue 링크를 추적 정보로 남긴다.

## 4. RAG 확장 설계

Phase 2에서는 다음 구조를 추가한다.

```text
RepoChunk
  path
  kind
  text
  start_line
  end_line
  embedding
  metadata
```

Vector DB 후보:

- Chroma
- FAISS

Embedding 후보:

- intfloat/multilingual-e5-small
- BAAI/bge-m3
- sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- nomic-embed-text

한국어/영어 문서가 섞이는 레포를 고려하면 multilingual embedding 모델을 우선 검토한다.

## 5. Closed Network Mode

폐쇄망 환경에서는 외부 API 없이 핵심 기능이 동작해야 한다.

폐쇄망에서 Claude, Codex, OpenAI 같은 외부 AI 도구를 사용할 수 있다고 주장하지 않는다. Context Capsule의 폐쇄망 지원은 **외부 AI 없이도 작업을 잘 넘기는 기능이 살아있는 것**을 의미한다.

실행 모드:

| Mode | 구성 | 외부 전송 |
| --- | --- | --- |
| No-AI Mode | 로컬 레포 스캔, 파일 분류, 키워드 검색, 규칙 기반 위험도 분석, 대상별 브리프 생성 | 없음 |
| Local-AI Mode | 로컬 임베딩, 로컬 vector DB, llama.cpp/Ollama 기반 요약 | 없음 |
| External-AI Mode | Claude/Codex/OpenAI handoff prompt 전달 | 있음, 사용자 승인 필요 |

필수 구성:

- 로컬 레포 스캔
- 파일 분류
- 키워드/BM25 검색
- 규칙 기반 risk analyzer
- 로컬 토큰 분석기
- Markdown generator

선택 구성:

- 로컬 임베딩 모델
- 로컬 vector DB
- llama.cpp
- Ollama
- vLLM
- 사전 다운로드한 sentence-transformers 모델
- offline wheels bundle

오프라인 번들 예시:

```text
context-capsule-offline/
├── wheels/
├── models/
├── app/
├── README_OFFLINE.md
└── install_offline.ps1
```

## 6. Human-in-the-loop Policy

Context Capsule의 기본 정책은 다음과 같다.

1. AI는 직접 수정하지 않는다.
2. AI는 변경 파일과 영향도를 먼저 설명한다.
3. HIGH/BLOCKED 위험은 승인 전까지 보류한다.
4. secret과 production data는 수집·출력하지 않는다.
5. 작업 요청과 무관한 대규모 리팩터링은 금지한다.
6. 팀원용 브리프는 압박보다 시작점과 완료 기준을 명확히 하는 데 집중한다.

## 7. 자체 위험도 모델 계획

초기에는 규칙 기반으로 위험을 감지한다. 이후 작업 요청 라벨 데이터를 만들어 작은 분류 모델을 학습한다.

입력 예시:

```text
로그인 API 응답 구조를 바꾸고 JWT 발급 로직을 수정한다.
```

출력 예시:

```json
{
  "risk_level": "HIGH",
  "approval_required": true,
  "reasons": ["auth", "api_response"]
}
```

## 8. 모델별 Handoff 전략

같은 작업이라도 대상 모델/사람에 따라 지시문을 다르게 만든다.

| Target | Strategy |
| --- | --- |
| Claude Sonnet | 단계와 금지사항을 더 명확히 쓰고, 먼저 계획 보고를 강제 |
| Claude Opus | 설계 대안 비교와 넓은 추론 허용 |
| Codex | 파일 단위 변경 지시, 테스트 명령, diff 중심 |
| Local LLM | 짧은 요약, 작업 의도 추출, target별 문장 다듬기 정도로 제한 |
| Junior Developer | 작은 단계, 완료 기준, 질문해야 할 내용 |
| Future Me | 이어서 볼 파일, 막힌 점, 다음 액션 |

이 전략의 목적은 낮은/중간급 모델을 고급 모델로 바꾼다고 주장하는 것이 아니라, **모델이 헷갈릴 여지를 줄여 같은 모델이 더 안정적으로 일하게 만드는 것**이다.
