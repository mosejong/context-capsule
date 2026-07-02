# Raw vs Context Capsule — 전체 비교

**날짜**: 2026-07-02  
**모델**: claude-haiku-4-5-20251001, claude-sonnet-4-6, claude-opus-4-8

## 인터뷰 최종 수치

- CC 전체 정답률: 76/90 (84.4%)
- Raw 전체 정답률: 20/39 (51.3%)
- 평균 토큰 절감: 71.8%
- 핵심 메시지: 비싼 모델도 Raw 컨텍스트에서는 추상적으로 답할 수 있으며, Context Capsule이 관련 근거를 좁혀줄 때 파일명/함수명/수치 정확도가 살아난다.

주의: 채점에는 알려진 오답 수치를 피한 것도 포함합니다. 예를 들어 근거 문서의 값이 `98.08`일 때 `98.6`을 말하지 않은 경우를 정답 보존으로 봅니다.

## Provider Cost Observation

This is a manual Anthropic console observation from the experiment run, not provider API usage stored by Context Capsule.

| Model | Observed cost |
|---|---:|
| Claude Sonnet 4.6 | $0.88 |
| Claude Opus 4.8 | $0.54 |
| Claude Haiku 4.5 | $0.41 |
| **Total** | **$1.83** |

Adding the Opus run increased spend by about $0.92; the $5 test budget had about $3.17 remaining. Because procurement/rainbow used small CC packets instead of raw 107K+ contexts, Opus could be tested without burning the full budget.

## Actual API Cost (computed from response `usage`)

Computed per call from `usage.input_tokens` / `output_tokens` / `cache_creation_input_tokens` / `cache_read_input_tokens` x the pricing table below (`$/1M tokens`), not the manual console observation above.

| Model | Input | Output | Cache write (5m) | Cache read |
|---|---:|---:|---:|---:|
| claude-haiku-4-5-20251001 | $1.00 | $5.00 | $1.25 | $0.10 |
| claude-sonnet-4-6 | $3.00 | $15.00 | $3.75 | $0.30 |
| claude-opus-4-8 | $5.00 | $25.00 | $6.25 | $0.50 |

| Model | Actual cost |
|---|---:|
| claude-haiku-4-5-20251001 | $0.0899 |
| claude-sonnet-4-6 | $0.2698 |
| claude-opus-4-8 | $0.5118 |
| **Total** | **$0.8716** |

## 레포/모델별 요약

### dummy-repo (소형, Raw vs CC 전 모델)

| 모델 | Raw | CC | 핵심 |
|---|---:|---:|---|
| Haiku | 9/9 | 9/9 | 기준선 |
| Sonnet | 6/9 | 8/9 | D-T3 Raw 0/3 |
| Opus | 5/9 | 9/9 | D-T2/D-T3 Raw 실패 -> CC 완벽 |

Opus Raw이 Haiku Raw보다 낮은 이유: Opus는 전체 컨텍스트를 추상화해서 답하는 경향이 있어 파일명/함수명을 생략했다. CC가 좁혀주면 9/9로 역전된다.

### procurement-logistics-ai (중형, 107K Raw)

| 모델 | Raw | CC |
|---|---:|---:|
| Haiku | 0/9 | 8/9 |
| Sonnet | - | 8/9 |
| Opus | - | 8/9 |

### rainbow-bridge (대형 451파일, CC only)

| 모델 | CC |
|---|---:|
| Haiku | 9/9 |
| Sonnet | 9/9 |
| Opus | 8/9 |

## 요약

| 레포 | ID | 태스크 | 모델 | Raw토큰 | CC토큰 | 절감 | Raw점수 | CC점수 | Raw비용 | CC비용 |
|---|---|---|---|---|---|---|---|---|---:|---:|
| dummy-repo | D-T1 | auth_service 500 에러  | haiku | ~4,468 | ~2,327 | 47.9% | 3/3 | 3/3 | $0.0087 | $0.0062 |
| dummy-repo | D-T1 | auth_service 500 에러  | sonnet | ~4,468 | ~2,327 | 47.9% | 3/3 | 3/3 | $0.0261 | $0.0187 |
| dummy-repo | D-T1 | auth_service 500 에러  | opus | ~4,468 | ~2,327 | 47.9% | 3/3 | 3/3 | $0.0521 | $0.0353 |
| dummy-repo | D-T2 | 결제 실패 고쳐줘 | haiku | ~4,468 | ~2,179 | 51.2% | 3/3 | 3/3 | $0.0087 | $0.0061 |
| dummy-repo | D-T2 | 결제 실패 고쳐줘 | sonnet | ~4,468 | ~2,179 | 51.2% | 3/3 | 3/3 | $0.0261 | $0.0183 |
| dummy-repo | D-T2 | 결제 실패 고쳐줘 | opus | ~4,468 | ~2,179 | 51.2% | 3/3 | 3/3 | $0.0520 | $0.0350 |
| dummy-repo | D-T3 | 로그인 안돼 | haiku | ~4,468 | ~2,732 | 38.9% | 3/3 | 3/3 | $0.0087 | $0.0066 |
| dummy-repo | D-T3 | 로그인 안돼 | sonnet | ~4,468 | ~2,732 | 38.9% | 3/3 | 3/3 | $0.0261 | $0.0198 |
| dummy-repo | D-T3 | 로그인 안돼 | opus | ~4,468 | ~2,732 | 38.9% | 3/3 | 3/3 | $0.0520 | $0.0378 |
| procurement-logistics-ai | P-T1 | ML 모델 정확도가 몇 %야? | haiku | ~107,524 | ~2,488 | 97.7% | 0/4 | 1/4 | $0.0000 | $0.0081 |
| procurement-logistics-ai | P-T1 | ML 모델 정확도가 몇 %야? | sonnet | ~107,524 | ~2,488 | 97.7% | CC only | 1/4 | - | $0.0243 |
| procurement-logistics-ai | P-T1 | ML 모델 정확도가 몇 %야? | opus | ~107,524 | ~2,488 | 97.7% | CC only | 1/4 | - | $0.0435 |
| procurement-logistics-ai | P-T2 | QA 리포트에 나온 성능 수치 알려줘 | haiku | ~107,524 | ~2,487 | 97.7% | 0/4 | 2/4 | $0.0000 | $0.0081 |
| procurement-logistics-ai | P-T2 | QA 리포트에 나온 성능 수치 알려줘 | sonnet | ~107,524 | ~2,487 | 97.7% | CC only | 2/4 | - | $0.0243 |
| procurement-logistics-ai | P-T2 | QA 리포트에 나온 성능 수치 알려줘 | opus | ~107,524 | ~2,487 | 97.7% | CC only | 2/4 | - | $0.0435 |
| procurement-logistics-ai | P-T3 | 프로젝트 모델 성능 요약해줘 | haiku | ~107,524 | ~2,424 | 97.7% | 0/4 | 2/4 | $0.0000 | $0.0079 |
| procurement-logistics-ai | P-T3 | 프로젝트 모델 성능 요약해줘 | sonnet | ~107,524 | ~2,424 | 97.7% | CC only | 2/4 | - | $0.0238 |
| procurement-logistics-ai | P-T3 | 프로젝트 모델 성능 요약해줘 | opus | ~107,524 | ~2,424 | 97.7% | CC only | 2/4 | - | $0.0426 |
| rainbow-bridge | R-T1 | auth 로그인 JWT 만료 처리 수 | haiku | - | ~2,166 | 0% | CC only | 3/3 | - | $0.0063 |
| rainbow-bridge | R-T1 | auth 로그인 JWT 만료 처리 수 | sonnet | - | ~2,166 | 0% | CC only | 3/3 | - | $0.0189 |
| rainbow-bridge | R-T1 | auth 로그인 JWT 만료 처리 수 | opus | - | ~2,166 | 0% | CC only | 3/3 | - | $0.0356 |
| rainbow-bridge | R-T2 | docker-compose.yml 배 | haiku | - | ~2,374 | 0% | CC only | 3/3 | - | $0.0070 |
| rainbow-bridge | R-T2 | docker-compose.yml 배 | sonnet | - | ~2,374 | 0% | CC only | 3/3 | - | $0.0210 |
| rainbow-bridge | R-T2 | docker-compose.yml 배 | opus | - | ~2,374 | 0% | CC only | 3/3 | - | $0.0399 |
| rainbow-bridge | R-T3 | users 테이블 마이그레이션 추가해 | haiku | - | ~2,596 | 0% | CC only | 3/3 | - | $0.0075 |
| rainbow-bridge | R-T3 | users 테이블 마이그레이션 추가해 | sonnet | - | ~2,596 | 0% | CC only | 3/3 | - | $0.0225 |
| rainbow-bridge | R-T3 | users 테이블 마이그레이션 추가해 | opus | - | ~2,596 | 0% | CC only | 3/3 | - | $0.0424 |

---
