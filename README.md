# Context Capsule

AI에게 일을 맡기기 전에, **무엇을 봐야 하는지, 무엇을 건드리면 안 되는지, 어떤 결과가 나와야 하는지** 정리해주는 로컬 작업 인수인계 도구입니다.

```text
대충 말한 작업 요청
-> 관련 파일과 금지 범위 정리
-> 충돌/위험 확인
-> Claude, Codex, ChatGPT에 복붙할 프롬프트 생성
```

현재 공개 버전은 KDT 수강생/신입 개발자/면접 포트폴리오 검증용 public MVP입니다. 상업화보다 실제 테스터 피드백과 제품 안정화를 우선합니다.

## 빠른 시작

```text
1. 최신 ZIP 다운로드
   https://github.com/mosejong/context-capsule/releases/latest

2. 압축 해제

3. run_context_capsule.bat 더블클릭

4. 브라우저에서 열기
   http://localhost:8501

5. AI에게 작업 맡기기에서 평소 말투로 입력
   리드미 손보자
   로그인 안돼
   로컬 실행 안돼
   auth는 건드리지 말고 문서만 바꾸자
```

처음이면 [START_HERE_KO.md](./START_HERE_KO.md)만 먼저 보세요.

## 화면 예시

<img src="./docs/assets/screenshots/01_dashboard_first_screen.png" alt="Context Capsule FastAPI local dashboard first screen" width="900">

<details>
<summary>작업 결과와 수치 충돌 예시 보기</summary>

### 작업 결과 요약

<img src="./docs/assets/screenshots/02_work_handoff_summary.png" alt="Context Capsule work handoff summary screen" width="900">

### 수치 충돌/위험 카드

<img src="./docs/assets/screenshots/03_metric_conflict_risk.png" alt="Context Capsule metric conflict risk card screen" width="900">

</details>

## Who It Is For

### Primary User: Junior Developers

- AI에게 어떤 파일을 보여줘야 할지 막막한 사람
- 작업 범위와 금지사항을 먼저 좁히고 싶은 사람
- 팀 프로젝트에서 README, 이슈, 회의록, 작업 브리프를 자주 만드는 사람
- AI가 엉뚱한 파일을 수정하지 않도록 사람이 통제하고 싶은 사람

### Secondary Reader: Team Leads, Interviewers, AI Beginners

- 신입 개발자가 AI를 안전하게 쓰는 방식을 보고 싶은 사람
- 결과물보다 문제 정의, 위험 통제, 검증 습관을 보고 싶은 사람
- AI/RAG/토큰 용어를 몰라도 사용 흐름을 이해해야 하는 사람

## 결과는 이 순서로 봅니다

```text
요약
-> 추천 첫 행동
-> 근거 파일
-> 충돌/위험
-> 복붙 프롬프트
```

- `요약`: Context Capsule이 요청을 어떻게 이해했는지 확인
- `추천 첫 행동`: 지금 바로 무엇부터 보면 되는지 확인
- `근거 파일`: AI나 팀원이 먼저 봐야 할 파일 후보
- `충돌/위험`: 수치 충돌, secret/env, auth/db/deploy 위험 확인
- `복붙 프롬프트`: Claude, Codex, ChatGPT에 넘길 작업 지시문

## 핵심 기능

| 기능 | 설명 |
| --- | --- |
| Request Understanding | `리드미 손보자`, `깃헙 이슈 안됨`, `이거 왜그래?` 같은 실제 말투를 의도/대상/보호영역으로 정규화 |
| Retrieval | 작업과 관련 있는 파일 후보만 선별 |
| Risk & Conflict Check | auth, DB, deploy, secret, 수치 충돌을 사람이 보기 좋게 표시 |
| Work Handoff | AI/팀원/내일의 나/GitHub Issue용 작업 정리본 생성 |
| Scrum/Kickoff/Health | 회의록, 프로젝트 시작 메모, MVP/프로토타입 준비도 점검 |
| Feedback Loop | 테스터 피드백을 저장하고 다음 패치 후보로 정리 |

## 실험 결과

Raw repository prompt와 Context Capsule prompt를 Haiku/Sonnet/Opus로 비교했습니다.

```text
Raw answer accuracy:             20/39 (51.3%)
Context Capsule answer accuracy: 76/90 (84.4%)
Average estimated token reduction: 71.8%
Observed provider spend:          $1.83 total
```

핵심은 “Haiku가 제일 좋다”가 아니라, **컨텍스트가 정리되면 모델 간 성능 차이가 줄어든다**는 점입니다.

자세한 요약: [Experiment One Pager](./docs/presentation/experiment_one_pager.md)

## 문서 찾기

문서가 많아져서 아래 인덱스에서 고르면 됩니다.

| 목적 | 볼 문서 |
| --- | --- |
| 처음 실행 | [START_HERE_KO.md](./START_HERE_KO.md) |
| 전체 문서 지도 | [docs/README.md](./docs/README.md) |
| 로컬 실행/ZIP | [docs/local_app.md](./docs/local_app.md) |
| 기술 구조 | [docs/reference/tech_brief.md](./docs/reference/tech_brief.md) |
| 실험/검증 | [docs/reports/README.md](./docs/reports/README.md) |
| 릴리즈 기록 | [docs/releases/README.md](./docs/releases/README.md) |

## 개발자용 명령

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest -q
```

로컬 UI:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_dashboard.ps1
```

CLI 예시:

```powershell
.\context_capsule_cli.bat doctor --repo-path .
.\context_capsule_cli.bat generate --repo-path . --task "리드미 손보자" --target all --save --json
```

릴리즈 ZIP:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_release.ps1 -Version 0.2.14
```

## 안전 원칙

- 외부 LLM/API 없이 기본 기능이 동작합니다.
- secret/env/credential 값은 출력하지 않도록 마스킹합니다.
- GitHub Issue 생성은 dry-run이 기본이고, 실제 생성은 `--apply`가 필요합니다.
- 자동 수정, 자동 역할 배정, 자동 팀원 평가는 하지 않습니다.
- 토큰 수치는 실제 provider billing이 아니라 local estimate입니다.

## 현재 버전

최신 릴리즈: [v0.2.14](./docs/releases/v0.2.14.md)

GitHub Release: https://github.com/mosejong/context-capsule/releases/latest
