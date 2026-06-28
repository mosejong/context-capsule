# Context Capsule — 기술 설계 브리프

> "바이브코딩 추세에서 AI 과금 부담과 토큰 낭비를 줄이기 위해 만든 로컬 우선 RAG 핸드오프 도구"

이 문서는 Context Capsule의 기술적 설계 결정을 설명한다.  
면접, 강사님 리뷰, 외부 발표 시 "이런 기술로 이렇게 만들어봤습니다" 형식의 설명 기반 자료다.

---

## 1. 왜 만들었는가

### 문제 인식

AI 코딩 도구(Claude, Codex, Gemini)를 쓰다 보면 두 가지 낭비가 반복된다.

1. **토큰 낭비**: 태스크와 무관한 파일까지 전부 붙여넣거나 전체 레포를 날린다.  
2. **정보 오염**: 레포 전체를 던지면 AI가 오래된 수치나 README 오류를 그대로 답변한다.

실험에서 확인된 수치 (procurement-logistics-ai, 86개 파일):

| 방식 | 입력 토큰 | 오류 |
|---|---|---|
| Raw (전체 레포 덤프) | ~188,000 토큰 | Haiku·Sonnet이 README 수치 98.6% 오답 반환 |
| Context Capsule | ~3,500 토큰 | Haiku·Sonnet·Opus 모두 정답 98.08% 반환 |

**→ 98% 토큰 절감, 정확도 오답 제거.**

### 해결 접근

"AI한테 다 넣지 말고, 태스크에 필요한 파일만 골라서 사람이 검토 후 넘기자."

---

## 2. 외부 LLM 미사용 — 폐쇄망·오프라인 호환

Context Capsule의 핵심 기능은 **외부 API 호출 없이 로컬에서 완결**된다.

### 이유

- 기업 내부 레포는 외부로 못 나가는 경우가 많다 (보안망, 내부망).
- AI API 키가 없어도 쓸 수 있어야 한다 (비용 장벽 제거).
- 로컬에서 돌아가면 응답 속도도 빠르고 과금 걱정도 없다.

### 실제 구현

`capsule_service.py` → `scan_repo()` → `generate_capsule()` → `build_execution_packet()` 전 파이프라인이 로컬 파일 읽기 + 규칙 기반 연산만 수행한다.

```python
# capsule_service.py — 외부 호출 없음
files = scan_repo(input_data.repo_path)   # 로컬 파일 읽기
capsule = generate_capsule(input_data, files)  # 규칙 기반 처리
```

`hybrid_retriever.py`의 주석:

```python
class HashEmbeddingProvider:
    """Dependency-free local embedding provider for closed-network mode.
    This is not a semantic model. It is a deterministic vector baseline
    that lets hybrid ranking run without downloading or calling external services.
    """
```

**→ 외부 LLM, 외부 API, 인터넷 연결 없이 동작.**  
선택적으로 `sentence-transformers` (로컬 모델)나 Ollama를 붙일 수 있지만 필수가 아니다.

---

## 3. RAG 설계 — 세 가지 검색 모드

RAG(Retrieval-Augmented Generation)에서 CC는 **검색(Retrieval)과 증강(Augmentation)만 로컬에서** 수행한다.  
생성(Generation)은 사람이 검토 후 AI 도구에 넘기는 방식으로 설계했다.

### 모드 1: Keyword (기본값, No-AI)

`simple_retriever.py` — 가장 가볍고 오프라인에서 100% 동작.

**작동 원리**:

```
query → tokenize() → Counter(term frequency)
      → MULTILINGUAL_DOMAIN_TERMS 확장 (한국어 → 영어 동의어)
      → 파일별 score 계산
      → intent 분류 (documentation / launcher / code / general)
      → top_k 파일 반환
```

**한국어 처리 예시**:

```python
MULTILINGUAL_DOMAIN_TERMS = {
    "결제": ("payment", "checkout", "billing"),
    "로그인": ("login", "auth", "jwt", "session"),
    "인증": ("auth", "login", "jwt", "permission"),
    "배포": ("deploy", "docker", "compose", "nginx", "production"),
    ...
}
```

"결제 fallback 구현해줘"라고 입력하면 `결제`가 `payment`, `checkout`으로 확장되어 `payment_service.py`가 상위에 랭크된다.

**파일명 직접 언급 시 강제 포함**:

```python
MANDATORY_SCORE = 1000.0
# 쿼리에 파일명이 있으면 점수 1000점 → 무조건 top_k 안에 들어감
```

**경로 가중치**:

```python
IMPORTANT_PATH_HINTS = {
    "auth": 1.5, "readme": 2.5, "cli": 2.0,
    "adapter": 2.0, "dashboard": 1.8, "launcher": 2.5, ...
}
```

ML 모델 없이 규칙만으로 파일 우선순위를 조정한다.

---

### 모드 2: Hybrid (선택적 로컬 벡터 순위 보정)

`hybrid_retriever.py` — keyword 점수 58% + 해시 벡터 유사도 42%로 재랭킹.

**HashEmbeddingProvider**: SHA-256 해시 기반 384차원 벡터.  
외부 모델 없이 결정론적(deterministic)으로 생성된다. 같은 텍스트 → 항상 같은 벡터.

```python
DEFAULT_KEYWORD_WEIGHT = 0.58
DEFAULT_SEMANTIC_WEIGHT = 0.42
```

`CONTEXT_CAPSULE_EMBEDDING_PROVIDER=sentence-transformers` 환경변수를 설정하면 로컬 임베딩 모델로 교체 가능 (설치 필요).

---

### 모드 3: Indexed (영속 인덱스, 대형 레포용)

`persistent_index.py` — 레포 청크를 미리 인덱싱해서 반복 쿼리를 빠르게 처리.  
`.context-capsule-index/` 폴더에 로컬 저장. 서버 불필요.

---

### 검색 모드 비교

| 모드 | 외부 의존성 | 속도 | 정확도 | 적합 레포 크기 |
|---|---|---|---|---|
| `keyword` | 없음 | 빠름 | 높음 (hit@1 9/10) | ~소형·중형 |
| `hybrid` | 없음 (hash) / 선택적 (sentence-transformers) | 보통 | 향상됨 | 중형 이상 |
| `indexed` | 없음 | 쿼리 빠름, 인덱스 구축 필요 | 동일 | 대형 |

---

## 4. 모델 없음 — 규칙 기반 경량화

Context Capsule에는 **ML 모델이 없다. GPU도 필요 없다.**

### 파일 선별 — 규칙 기반 점수화

모든 판단이 Python 코드 규칙으로 이루어진다:

- **토크나이징**: `re.compile(r"[A-Za-z0-9_]+|[가-힣]+")`로 한국어+영어 추출
- **TF 점수**: `Counter(tokenize(query))` — 쿼리 단어 빈도 × 파일 내 등장 횟수
- **의도 분류**: `classify_task_intent()` — `DOCUMENTATION_HINTS`, `CODE_HINTS`, `LAUNCHER_HINTS` 집합 교집합
- **경로 가중치**: `IMPORTANT_PATH_HINTS` 딕셔너리 — `auth: 1.5`, `readme: 2.5`

### 위험도 분석 — 규칙 기반 패턴 매칭

`risk_analyzer.py` — LLM 판단 없이 키워드 패턴으로 위험도를 결정한다.

```python
RISK_RULES = [
    (RiskLevel.BLOCKED, "secret/env/credential 변경", ["secret", ".env", "api_key", ...]),
    (RiskLevel.HIGH,    "인증/권한 로직 영향",         ["auth", "jwt", "login", "password", ...]),
    (RiskLevel.HIGH,    "DB schema/migration 영향",   ["schema", "migration", "table", "column"]),
    (RiskLevel.MEDIUM,  "API 응답 형식 변경",           ["response", "router", "endpoint"]),
]
```

**변경 의도 감지**: `has_change_intent()` — "수정", "고쳐", "fix", "implement" 등 30개 키워드.  
**부정 문맥 감지**: "건드리지 마", "do not", "avoid" 등 → 같은 키워드여도 CHANGE가 아닌 MENTION으로 분류.  
**수치 충돌 감지**: 여러 문서에서 같은 맥락의 % 수치가 다를 때 MEDIUM 플래그.

→ 인터넷 없이, 모델 없이, Python 표준 라이브러리만으로 위험도를 판단한다.

---

## 5. Human-in-the-Loop — 설계 철학

Context Capsule은 **AI가 직접 코드를 바꾸지 않는다.**

```
사용자 태스크 입력
    ↓
[CC] 파일 선별 + 위험도 분석 + 토큰 추정
    ↓
[패킷 생성] AI 핸드오프 프롬프트 + 리스크 체크리스트
    ↓
[사람 검토] 파일 범위 확인, 위험도 승인
    ↓
[AI 도구에 전달] Claude / Codex / Gemini 등
```

이유:
- 위험도 HIGH/BLOCKED 작업(인증, DB 마이그레이션, 배포)은 사람이 먼저 봐야 한다.
- AI가 컨텍스트를 잘못 읽고 엉뚱한 파일을 건드리는 것을 방지한다.
- 리뷰 게이트를 도구가 강제해줌으로써 신입도 안전하게 작업 범위를 잡을 수 있다.

---

## 6. 전체 파이프라인 흐름

```
사용자 요청 (task_request)
    │
    ▼
scan_repo()                    ← 로컬 파일 수집, .git / venv / node_modules 제외
    │
    ▼
classify_file()                ← doc / code / config / test 분류
    │
    ▼
retrieve_relevant_chunks()     ← 키워드 스코어링 + 의도 분류 + mandatory 파일 포함
    │
    ▼
analyze_risk()                 ← RISK_RULES 매칭, 변경 의도 감지, 수치 충돌 감지
    │
    ▼
token_analyzer()               ← 로컬 char 추정 (approx_local_v1), 감소율 계산
    │
    ▼
generate_capsule()             ← 핸드오프 프롬프트 생성
    │
    ▼
build_work_handoff_trace()     ← 워크플로우 그래프 trace (결정 경로 기록)
    │
    ▼
save_output_packet()           ← outputs/YYYYMMDD_slug/ 저장
```

**외부 API 호출: 없음.**

---

## 7. 기술 스택 요약

| 계층 | 선택 | 이유 |
|---|---|---|
| 언어 | Python 3.11 | 생태계, 팀 친숙도, 3.13 setuptools 버그 우회 |
| 검색 | 자체 구현 (규칙 기반) | 외부 의존성 제거, 오프라인 동작 |
| 벡터 | SHA-256 해시 384차원 (기본값) | 설치·모델 없이 hybrid 모드 가능 |
| 위험도 분석 | 규칙 기반 패턴 매칭 | ML 불필요, 결과가 예측 가능하고 수정 쉬움 |
| 토큰 추정 | `len(text) / 4` 로컬 추산 | 외부 tokenizer API 없이 동작 |
| 패키징 | `pip install -e .` | Python 3.11 표준, 진입점 `context-capsule` CLI |
| 테스트 | pytest, 138 tests | 회귀 방지, 자동 hit@1 평가 harness |

---

## 8. 면접/데모 시 설명 포인트

**Q. 외부 AI API를 안 쓰면 어떻게 동작하나요?**

> "파일 선별, 위험도 판단, 토큰 추정 모두 로컬 Python 규칙으로 처리합니다. 외부 LLM은 최종적으로 사람이 검토한 컨텍스트 패킷을 전달받는 AI 도구일 뿐이고, CC 자체에는 API 호출이 없습니다. 그래서 보안망 환경이나 오프라인 환경에서도 동작합니다."

**Q. RAG라고 하는데 벡터 DB 없이 어떻게 검색하나요?**

> "기본 모드는 TF 기반 키워드 스코어링입니다. 쿼리를 tokenize해서 파일별로 단어 빈도 점수를 내고, 경로 가중치와 의도 분류를 추가합니다. 한국어 도메인 용어는 영어 동의어로 확장해서 '결제'라고 써도 payment_service.py가 상위에 오게 했습니다. hybrid 모드는 SHA-256 해시 벡터로 재랭킹을 추가하는데, 이것도 외부 모델 없이 로컬에서 결정론적으로 생성됩니다."

**Q. 모델 경량화는 어떻게 했나요?**

> "저는 ML 모델을 안 씁니다. 오히려 그게 설계 결정이었는데, '규칙 기반으로도 충분한가'를 먼저 검증했습니다. 86개 파일 레포에서 keyword 모드만으로 hit@1 9/10, 위험도 탐지 10/10이 나왔습니다. GPU, 모델 파일, 다운로드 없이 Python 표준 라이브러리만으로 이 정확도가 나오면, 굳이 무거운 모델을 붙일 이유가 없었습니다."

**Q. 신입 개발자가 왜 이걸 만들었나요?**

> "저도 AI 코딩 도구를 쓰면서 과금 걱정을 했고, 전체 레포를 넣었다가 AI가 엉뚱한 파일을 건드리는 경험을 했습니다. 개발자들의 공통 문제라고 판단해서, 태스크에 필요한 컨텍스트만 골라주고 위험도도 먼저 알려주는 도구를 만들어봤습니다."

---

## 9. 검증 결과 (v0.2.12 기준)

| 지표 | 결과 |
|---|---|
| 단위 테스트 | 138 PASS |
| hit@1 (외부 레포 10 태스크) | 9/10 (90%) |
| hit@3 (외부 레포 10 태스크) | 10/10 (100%) |
| 위험도 탐지 정확도 | 10/10 (100%) |
| user-speech 쿼리 hit@1 | 55/61 (90%) |
| 토큰 절감 (86파일 레포) | ~98% vs 전체 레포 덤프 |
| 외부 API 호출 | 0 |

---

*Context Capsule v0.2.12 · 작성일 2026-06-28*
