# Reports Index

## Latest NVIDIA Reports

| Report | Purpose |
| --- | --- |
| [raw_vs_capsule_nvidia_procurement.md](./raw_vs_capsule_nvidia_procurement.md) | NVIDIA NIM procurement medium-repo Raw vs Capsule comparison |
| [raw_vs_capsule_nvidia_rainbow-bridge.md](./raw_vs_capsule_nvidia_rainbow-bridge.md) | NVIDIA NIM rainbow-bridge large-repo CC-only run |

검증/실험 리포트가 많아져서 우선순위를 나눕니다.

## 먼저 볼 것

| 문서 | 용도 |
| --- | --- |
| [../presentation/experiment_one_pager.md](../presentation/experiment_one_pager.md) | 발표/면접용 한 장 요약 |
| [raw_vs_capsule_full.md](./raw_vs_capsule_full.md) | Raw vs Context Capsule 전체 실험 결과 |
| [raw_vs_capsule_summary.md](./raw_vs_capsule_summary.md) | Raw vs Context Capsule 핵심 요약 |
| [retrieval_mode_benchmark.md](./retrieval_mode_benchmark.md) | keyword/hybrid/indexed 검색 모드 비교 |
| [retrieval_mode_benchmark_ko_sroberta.md](./retrieval_mode_benchmark_ko_sroberta.md) | ko-sroberta 실제 로컬 임베딩 후보 측정 |
| [external_repo_eval.md](./external_repo_eval.md) | 외부 레포 평가 결과 |
| [user_speech_retrieval_qa.md](./user_speech_retrieval_qa.md) | 한국어 구어체 요청 QA |

## 보조 리포트

| 문서 | 용도 |
| --- | --- |
| [agent_readme_comparison.md](./agent_readme_comparison.md) | README 생성 에이전트 비교 |
| [dummy_repo_10task_report.md](./dummy_repo_10task_report.md) | 더미 레포 10개 태스크 평가 |
| [edge_case_test_report.md](./edge_case_test_report.md) | 모호한 요청/대형 레포 엣지케이스 |
| [performance_comparison.md](./performance_comparison.md) | 초기 성능 비교 리포트 |
| [raw_vs_capsule_dummy.md](./raw_vs_capsule_dummy.md) | Raw vs Capsule 더미 레포 상세 로그 |

## 현재 대표 수치

```text
Context Capsule answer accuracy: 76/90 (84.4%)
Raw answer accuracy:             20/39 (51.3%)
Average estimated token reduction: 71.8%
Actual API cost from usage:       $0.8716 total
Observed provider spend:          $1.83 total (manual console observation)
```

주의:

```text
토큰 감소율은 local estimate입니다.
실제 provider billing 보장은 아닙니다.
```
