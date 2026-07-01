# Context Capsule Docs

문서가 많아져서 목적별로 입구를 나눕니다.

`docs` 루트에는 자주 여는 문서만 남기고, 나머지는 하위 폴더로 정리했습니다.
처음 보는 사람은 이 파일에서 필요한 문서 하나만 골라 보면 됩니다.

## 1. 처음 실행하는 사람

| 목적 | 문서 |
| --- | --- |
| 한국어 첫 실행 안내 | [START_HERE_KO.md](../START_HERE_KO.md) |
| KDT 테스터용 상세 가이드 | [kdt_beta_quickstart.md](./kdt_beta_quickstart.md) |
| 테스터에게 보낼 초대문 | [operations/kdt_tester_invite.md](./operations/kdt_tester_invite.md) |
| 로컬 앱/ZIP/CLI 실행 | [local_app.md](./local_app.md) |

## 2. 면접/발표용

| 목적 | 문서 |
| --- | --- |
| 한 장 실험 요약 | [presentation/experiment_one_pager.md](./presentation/experiment_one_pager.md) |
| 왜 만들었는지 실험 근거 | [presentation/experiment_why_context_capsule.md](./presentation/experiment_why_context_capsule.md) |
| 타깃 포지셔닝 | [presentation/target_positioning.md](./presentation/target_positioning.md) |
| 30초 데모 흐름 | [presentation/demo_capture_flow.md](./presentation/demo_capture_flow.md) |

## 3. 기술 설명

| 목적 | 문서 |
| --- | --- |
| 면접용 기술 브리프 | [reference/tech_brief.md](./reference/tech_brief.md) |
| 아키텍처 | [reference/architecture.md](./reference/architecture.md) |
| Request Understanding | [reference/request_understanding.md](./reference/request_understanding.md) |
| Hybrid Retrieval | [reference/hybrid_retrieval.md](./reference/hybrid_retrieval.md) |
| Workflow Graph Trace | [reference/workflow_graph.md](./reference/workflow_graph.md) |
| Token Evidence | [reference/token_evidence.md](./reference/token_evidence.md) |

## 4. v0.2 협업 모드

| 목적 | 문서 |
| --- | --- |
| Scrum/Kickoff 모드 | [reference/v0.2_scrum_kickoff_modes.md](./reference/v0.2_scrum_kickoff_modes.md) |
| Project Health Check | [reference/project_health_check.md](./reference/project_health_check.md) |
| 내 파트 확인 | [reference/work_handoff_ownership.md](./reference/work_handoff_ownership.md) |
| Feedback Loop | [operations/beta_feedback_loop.md](./operations/beta_feedback_loop.md) |
| Meeting-to-Execution 방향 | [reference/meeting_to_execution_pipeline.md](./reference/meeting_to_execution_pipeline.md) |

## 5. 검증/실험 자료

| 목적 | 문서 |
| --- | --- |
| 검증 문서 인덱스 | [reports/README.md](./reports/README.md) |
| 전체 검증 현황 | [validation.md](./validation.md) |
| 외부 레포 평가 | [reports/external_repo_eval.md](./reports/external_repo_eval.md) |
| Raw vs Capsule 전체 결과 | [reports/raw_vs_capsule_full.md](./reports/raw_vs_capsule_full.md) |

## 6. 릴리즈/운영

| 목적 | 문서 |
| --- | --- |
| 릴리즈 노트 인덱스 | [releases/README.md](./releases/README.md) |
| 패키징 방법 | [operations/release_packaging.md](./operations/release_packaging.md) |
| 게시 체크리스트 | [operations/release_publish_checklist.md](./operations/release_publish_checklist.md) |
| KDT 테스트 계획 | [operations/kdt_beta_test_plan.md](./operations/kdt_beta_test_plan.md) |
| 테스터 초대 패킷 | [operations/kdt_tester_invite.md](./operations/kdt_tester_invite.md) |

## 7. 보관/전략 문서

아래 문서는 당장 실행에 필요하지 않은 기록/전략 문서입니다.

- [archive/vision.md](./archive/vision.md)
- [archive/future_direction.md](./archive/future_direction.md)
- [archive/v1_roadmap.md](./archive/v1_roadmap.md)
- [archive/commercialization_strategy.md](./archive/commercialization_strategy.md)
- [research/llm_tech_scan_2026-06-22.md](./research/llm_tech_scan_2026-06-22.md)
- [research/paid_api_impact_scan_2026-06-22.md](./research/paid_api_impact_scan_2026-06-22.md)

## 문서 운영 원칙

- README에는 최신 사용 흐름만 둡니다.
- 자세한 설명은 docs 아래에 둡니다.
- 실험 결과는 reports 아래에 둡니다.
- 버전별 기록은 releases 아래에 둡니다.
- 발표/기술/운영/보관 문서는 각각 presentation, reference, operations, archive 아래에 둡니다.
- 오래된 문서를 삭제하기보다 archive로 내려 우선순위를 낮춥니다.
