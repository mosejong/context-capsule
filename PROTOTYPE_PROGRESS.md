# Prototype Progress

Context Capsule은 한 번에 크게 만들지 않고, 실행 가능한 작은 프로토타입을 단계별로 구체화한다.

현재 기준 목표:

> 레포와 작업 요청을 받아 AI/팀원/미래의 나에게 줄 최소 컨텍스트 기반 작업 브리프를 생성하고, 토큰 사용량과 위험 영역을 함께 보여준다.

## Status Board

| Status | Item | Notes |
| --- | --- | --- |
| Done | GitHub repo scaffold | README, plan, docs, app structure 생성 |
| Done | Python 3.13 local setup | Python 3.13.14 + `.venv` 확인 |
| Done | Streamlit MVP boot | `streamlit run app/main.py` 실행 확인 |
| Done | Basic repo scanner | 로컬 파일 스캔 |
| Done | Basic retriever | 키워드 기반 관련 chunk 검색 |
| Done | Basic risk analyzer | 규칙 기반 위험 신호 감지 |
| Done | Markdown capsule generator | AI handoff markdown 생성 |
| Done | Concept documentation | AI/Human/Self handoff, token analyzer, closed network 방향 반영 |
| Done | Stabilize tests | risk analyzer 테스트 실패 수정, `pytest` 통과 |
| Done | Prototype step plan | 아래 순서대로 하나씩 구현 |
| Done | Split requirements | MVP/RAG/로컬 LLM 의존성 분리 |
| Done | Handoff target modes | AI/팀원/미래의 나 템플릿 분리, 테스트 추가 |
| Done | Architecture model notes | 모델/기술 설명을 architecture에 추가 |
| Done | LLM tech scan | 최신 LLM/런타임/RAG 스택 공식 문서 기반 조사 |
| Done | Paid API impact scan | 유료 API 적용 시 성능/속도/토큰 비용을 어떻게 검증할지 조사 |
| Done | Token analyzer integration | 로컬 추정 기반 토큰 분석기 연결, UI/Markdown 출력 |
| Done | Chat-to-Capsule mode | GPT/Discord 대화에서 작업 요청, 파일, 결정 신호 추출 |
| Done | Meeting-to-Execution packet | Issue body, Decision Record, approval gate 생성 |
| Done | Split result views | 사용자 화면과 개발자 분석 화면 분리 |
| Done | MVP scenario validation | `scripts/validate_mvp.py` 반복 검증 루틴 추가 |
| Next | Discord/GitHub adapter | Discord API 입력과 GitHub Issue 생성 연동 |
| Backlog | Local RAG | Chroma/FAISS + local embedding |
| Backlog | Closed network bundle | 폐쇄망 설치/실행 패키지 |

## Current Known Issue

### Risk analyzer test failure

Resolved.

기존 `pytest` 기준 실패:

```text
tests/test_risk_analyzer.py::test_detects_auth_and_env_risk
```

원인:

- `risk_analyzer.py`가 chunk 하나에서 첫 번째 위험 규칙만 감지한다.
- `jwt token login password`에서 `token`이 먼저 BLOCKED로 잡히고, auth/login/password 기반 HIGH가 누락된다.

수정 방향:

- chunk 하나에서 여러 위험 규칙을 감지하도록 변경한다.
- secret/env BLOCKED와 auth HIGH를 동시에 보여준다.
- `deduplicate_findings`는 유지하되 중복 기준이 너무 공격적이지 않은지 확인한다.

완료 기준:

```text
python -m pytest -q
```

결과:

```text
2 passed in 0.11s
```

## Prototype Roadmap

## Step 1. Stabilize MVP

Status: Done

목표:

- 현재 MVP가 깨끗하게 실행되고 테스트가 통과하는 상태를 만든다.

작업:

1. risk analyzer 복수 위험 감지 수정
2. 테스트 통과 확인
3. `requirements.txt` 무게 점검
4. README 실행 방법 최신화 확인

완료 기준:

- `python -m pytest -q` 통과
- `streamlit run app/main.py` 실행 가능
- capsule markdown 생성 가능

검증 기록:

- Python 3.13.14 `.venv` 생성 완료
- `streamlit run app/main.py` 부팅 확인
- `python -m pytest -q` 결과: `2 passed`

## Step 2. Split Requirements

Status: Done

목표:

- MVP 실행용 의존성과 RAG/로컬 LLM 확장 의존성을 분리한다.

작업:

```text
requirements.txt
requirements-dev.txt
requirements-rag.txt
requirements-local-llm.txt
```

완료 기준:

- MVP 실행은 가볍게 설치된다.
- RAG 확장은 별도 설치로 가능하다.
- README에 설치 옵션이 분리되어 있다.

검증 기록:

- MVP runtime: `streamlit`, `pydantic`, `python-dotenv`
- Dev: `pytest`
- RAG: `chromadb`, `sentence-transformers`, `scikit-learn`, `numpy`, `pandas`
- Local LLM: provider-neutral adapter, optional `llama.cpp`/`Ollama`
- `pip install -e ".[dev]"` 성공
- `python -m pytest -q` 결과: `2 passed`

## Step 3. Add Handoff Target

Status: Done

목표:

- 하나의 capsule generator가 대상별 브리프를 생성하게 만든다.

대상:

```text
ai_tool
teammate
junior_developer
future_me
```

작업:

1. `CapsuleInput`에 `handoff_target` 추가
2. Streamlit UI에 target 선택 추가
3. generator 템플릿 분리
4. 테스트 추가

완료 기준:

- AI용 출력은 수정 범위/금지사항/검증 명령 중심
- 팀원용 출력은 오늘 할 일/완료 기준/질문 목록 중심
- 미래의 나용 출력은 현재 상태/막힌 점/다음 작업 중심

검증 기록:

- `CapsuleInput.handoff_target` 추가
- Streamlit `Handoff target` selectbox 추가
- AI/Teammate/Junior/Self 템플릿 분리
- `tests/test_capsule_generator.py` 추가
- `python -m pytest -q` 결과: `4 passed`

## Step 4. Token Analyzer Integration

Status: Done

목표:

- Context Capsule의 토큰 절약 효과를 숫자로 보여준다.

작업:

1. 토큰 계산 인터페이스 정의
2. 원본 컨텍스트 토큰 수 계산
3. 최종 capsule 토큰 수 계산
4. 절약률 표시
5. Streamlit UI에 Token Budget 섹션 추가

출력 예시:

```text
Original context estimate: 18,420 tokens
Capsule prompt estimate: 3,180 tokens
Estimated reduction: 82.7%
```

완료 기준:

- 같은 작업 요청에서 원본 대비 capsule 토큰 수를 비교할 수 있다.
- 포트폴리오에서 수치 기반으로 설명할 수 있다.

검증 기록:

- `app/analyzers/token_analyzer.py` 추가
- `CapsuleOutput.token_budget` 추가
- Streamlit `Token Budget` metric 표시 추가
- Markdown `Token Budget` 섹션 추가
- `tests/test_token_analyzer.py` 추가
- `python -m pytest -q` 결과: `7 passed`

## Step 5. Chat-to-Capsule Mode

Status: Done

목표:

- GPT/Discord/회의 대화를 붙여넣으면 작업 요청을 정리한다.

작업:

1. chat log 입력창 추가
2. 작업 의도 추출 규칙 작성
3. 에러 로그/파일명/path 힌트 추출
4. 추출된 task request로 기존 retrieval 실행

완료 기준:

- "에러났는데 뭐야?" 같은 대화를 구체적인 작업 브리프로 변환한다.
- 관련 파일, 원인 후보, 수정 방향, 검증 명령을 출력한다.

검증 기록:

- `app/analyzers/chat_analyzer.py` 추가
- Streamlit `Chat / error log` 입력 모드 추가
- 파일 경로, 에러 힌트, 결정 힌트 추출
- `tests/test_chat_analyzer.py` 추가
- `python -m pytest -q` 결과: `9 passed`

## Step 6. Local RAG

목표:

- 키워드 검색에서 벡터 검색으로 확장한다.

작업:

1. chunk metadata 저장 구조 설계
2. local embedding model 선택
3. Chroma 또는 FAISS index 생성
4. top-k 검색 결과 비교
5. keyword + vector hybrid retrieval 검토

완료 기준:

- 작업 요청별 관련 파일 top-k 품질을 평가할 수 있다.
- 한국어/영어 혼합 문서에서 검색이 동작한다.

## Step 7. Closed Network Mode

목표:

- 외부 API 없이 폐쇄망에서 사용할 수 있는 실행 경로를 만든다.

작업:

1. offline wheel bundle 구조 작성
2. local model folder 규칙 작성
3. 외부 API 호출 차단 옵션
4. secret redaction 강화
5. `README_OFFLINE.md` 작성

완료 기준:

- 인터넷 없이 사전 반입한 패키지/모델로 실행 가능하다.
- 레포 내용이 외부 API로 나가지 않는다.

## Step 8. Meeting-to-Execution Pipeline

Status: MVP Done

목표:

- Discord 회의에서 확정된 아이디어를 GitHub Issue, 작업 브리프, AI handoff prompt로 변환한다.
- 자동 작업 착수는 사람 승인 뒤에만 진행한다.

작업:

1. Discord 대화/명령어 입력 schema 설계
2. decision record 생성 템플릿 작성
3. GitHub Issue body generator 추가
4. approval gate 규칙 정의
5. Claude/Codex adapter는 처음에는 prompt export만 지원

완료 기준:

- 회의 결정 텍스트 하나로 Issue 본문, risk checklist, AI handoff prompt가 생성된다.
- HIGH/BLOCKED risk는 자동 착수 대상에서 제외된다.
- 자동 merge/deploy/credential 변경은 지원하지 않는다.

검증 기록:

- `app/generators/execution_packet_generator.py` 추가
- Streamlit `Meeting-to-Execution Packet` 출력 추가
- GitHub Issue title/body, Decision Record, recommended branch 생성
- HIGH/BLOCKED risk 기반 auto-start gate 차단
- `tests/test_execution_packet_generator.py` 추가
- `python -m pytest -q` 결과: `11 passed`

남은 작업:

- 실제 Discord slash command 입력
- GitHub Issue 생성 API adapter
- Claude/Codex adapter 연결

## Working Rule

앞으로는 이 순서로 진행한다.

1. 한 번에 하나의 Step만 진행한다.
2. 각 Step은 구현 전 영향 파일과 수정 계획을 먼저 확인한다.
3. 구현 후 테스트/실행 결과를 기록한다.
4. 완료된 항목은 이 문서에서 `Done`으로 이동한다.
5. 프로젝트 중심 문장은 유지한다.

프로젝트 중심 문장:

> 작업을 잘 넘기기 위한 컨텍스트 압축기.
