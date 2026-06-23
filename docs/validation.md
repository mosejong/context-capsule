# Validation

Context Capsule은 기능을 추가할 때마다 같은 검증 루틴을 반복한다.

목표:

> 대시보드가 뜨는지뿐 아니라, 작업 요청이 올바른 파일을 찾고, 위험도를 과하게 잡지 않으며, 사용자용 출력에 개발자 내부 표현이 섞이지 않는지 확인한다.

## 1. Fast Check

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

현재 기준:

```text
32 passed
```

Current checked areas:

- capsule generation
- risk analyzer
- token usage provider boundary
- saved output packet
- GitHub issue adapter dry-run/apply payload
- fixed demo scenario

## 2. Compile Check

```powershell
.\.venv\Scripts\python.exe -m compileall app tests scripts
```

목적:

- import 오류
- 문법 오류
- 새 파일 누락

을 빠르게 확인한다.

## 3. Scenario Validation

```powershell
.\.venv\Scripts\python.exe scripts\validate_mvp.py --repeat 5
```

검증 시나리오:

1. README 문서 브리프
2. Chat/Error log -> Capsule
3. High-risk auth task blocks auto-start
4. Teammate brief
5. Future-me handoff

현재 기준 예시:

```text
validated 5 scenarios x 5 run(s)
```

확인하는 것:

- 관련 파일이 검색되는가
- HIGH/BLOCKED 위험 작업은 auto-start가 막히는가
- 안전한 작업은 auto-start가 허용되는가
- `RiskLevel.` 같은 개발자 enum 표현이 사용자 출력에 새지 않는가
- 토큰 절감률이 계산되는가
- GitHub Issue body와 recommended branch가 생성되는가

## 3.1 Performance Report

```powershell
.\.venv\Scripts\python.exe scripts\generate_performance_report.py
```

생성 결과:

- `docs/reports/performance_comparison.md`
- `docs/assets/performance_comparison.svg`

이 리포트는 시나리오별 토큰 절감률, retrieved chunk 수, risk 수, auto-start gate 결과를 표와 SVG 그림으로 보여준다.

## 4. Stress Repeat

반복 횟수를 올려 회귀 가능성을 더 세게 본다.

```powershell
.\.venv\Scripts\python.exe scripts\validate_mvp.py --repeat 50
```

주의:

- 기본은 유한 반복이다.
- 진짜 무한 루프는 개발 중 터미널을 점유하므로 사용하지 않는다.
- 실패하면 해당 scenario 이름과 원인을 먼저 본다.

## 5. Dashboard Smoke

```powershell
.\.venv\Scripts\python.exe -m streamlit run app\main.py
```

확인:

- `사용자 화면` 탭
- `개발자 분석` 탭
- Token Budget
- Meeting-to-Execution Packet
- Download 버튼

## 6. Known Validation Findings

## 7. Performance Report v2 Metrics

The generated performance report tracks more than token reduction:

- raw context tokens versus capsule tokens
- estimated token reduction
- relevant file hit rate
- unrelated retrieved file count
- success proxy
- scope escape proxy
- auto-start gate result

검증 중 발견해 수정한 것:

- `app/analyzers/risk_analyzer.py` 같은 명확한 경로가 있는 에러 로그에서 `app/auth.py`가 넓은 path token 때문에 같이 검색되던 문제
- `capsule generator` 요청이 `capsule_generator.py`를 못 찾던 snake_case 검색 문제
- `token budget`의 `token`을 secret token으로 오탐하던 문제
- 사용자 출력에 `RiskLevel.HIGH` 같은 내부 enum 표현이 보이던 문제
