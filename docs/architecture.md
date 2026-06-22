# Architecture

Context Capsule은 레포 전체를 LLM에 한 번에 던지는 방식이 아니라, 작업 요청에 필요한 컨텍스트만 검색해 AI 작업 브리프를 조립하는 구조를 지향한다.

## 1. High-level Flow

```text
User Task Request
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
Capsule Generation
        ↓
AI Coding Tool Handoff
```

## 2. Components

### Repo Scanner

로컬 레포에서 문서, 코드, 설정 파일을 수집한다.

- README/docs 문서
- Python/JS/TS 등 코드 파일
- requirements, package, docker-compose 등 설정 파일
- 테스트 파일

수집 제외 대상:

- `.git`
- `.venv`
- `node_modules`
- `dist`, `build`
- 대용량 파일

### File Classifier

파일 확장자와 파일명을 기준으로 유형을 나눈다.

| Kind | Example |
| --- | --- |
| doc | README.md, docs/*.md |
| code | *.py, *.js, *.tsx |
| config | Dockerfile, requirements.txt, package.json |
| test | test_*.py, *.spec.ts |

### Retriever

MVP에서는 키워드 기반 검색을 사용한다. Phase 2에서는 Chroma/FAISS 기반 vector search로 확장한다.

검색 기준:

- 작업 요청과 일치하는 단어
- 파일 경로 힌트(auth, router, schema, docker 등)
- README/CONTRIBUTION 같은 설명 문서 가중치

### Risk Analyzer

작업 요청과 검색된 chunk에서 위험 신호를 감지한다.

위험 영역:

- secret/env/credential
- auth/JWT/login/password
- DB schema/migration/model
- docker/nginx/deploy/SSL
- API response/router/endpoint

### Capsule Generator

최종 Markdown 패킷을 생성한다.

포함 내용:

- Project Summary
- Task Request
- Retrieved Context
- Risk Findings
- Human Approval Checklist
- AI Handoff Prompt

## 3. RAG 확장 설계

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

- sentence-transformers/all-MiniLM-L6-v2
- intfloat/multilingual-e5-small
- BAAI/bge-small-en-v1.5

한국어/영어 문서가 섞이는 레포를 고려하면 multilingual embedding 모델을 우선 검토한다.

## 4. Human-in-the-loop Policy

Context Capsule의 기본 정책은 다음과 같다.

1. AI는 직접 수정하지 않는다.
2. AI는 변경 파일과 영향도를 먼저 설명한다.
3. HIGH/BLOCKED 위험은 승인 전까지 보류한다.
4. secret과 production data는 수집·출력하지 않는다.
5. 작업 요청과 무관한 대규모 리팩터링은 금지한다.

## 5. 자체 위험도 모델 계획

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
