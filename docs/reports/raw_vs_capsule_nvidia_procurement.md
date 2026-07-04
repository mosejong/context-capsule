# Raw vs Context Capsule — 전체 비교

**날짜**: 2026-07-04  
**Provider**: nvidia_nim  
**모델**: nvidia/nemotron-3-ultra-550b-a55b, deepseek-ai/deepseek-v4-flash

## 실험 요약 수치

- CC 전체 정답률: 16/24 (66.7%)
- Raw 전체 정답률: 12/24 (50.0%)
- 평균 토큰 절감: 97.7%
- 핵심 메시지: 비싼 모델도 Raw 컨텍스트에서는 추상적으로 답할 수 있으며, Context Capsule이 관련 근거를 좁혀줄 때 파일명/함수명/수치 정확도가 살아난다.

## Provider Cost Observation

NVIDIA NIM Build endpoints are treated as prototype/testing endpoints in this report. No product-operation cost guarantee is claimed, and API keys are read only from `NVIDIA_API_KEY` without being written to reports or metadata.

## Actual API Cost (computed from response `usage`)

No local price table is configured for this provider. Usage can be captured when the endpoint returns token usage, but this report does not convert it to billing cost.

## Run Scope

- Selected repos: procurement
- Task limit per repo: none
- The table below is generated only from this run's measured rows.
- If `--task-limit` is set, treat this as a smoke test, not a full benchmark.
- Provider calls retry transient 429/5xx/timeout errors up to 2 times before recording an error.

## Repo/Model Summary

| Repo | Model | Raw measured | Raw score | CC score | Avg token reduction |
|---|---|---:|---:|---:|---:|
| procurement-logistics-ai (중형 86파일) | deepseek-v4-flash | 3 | 5/12 | 8/12 | 97.7% |
| procurement-logistics-ai (중형 86파일) | nemotron-3-ultra-550b-a55b | 3 | 7/12 | 8/12 | 97.7% |

## 요약

| 레포 | ID | 태스크 | 모델 | Raw토큰 | CC토큰 | 절감 | Raw점수 | CC점수 | Raw비용 | CC비용 |
|---|---|---|---|---|---|---|---|---|---:|---:|
| procurement-logistics-ai | P-T1 | ML 모델 정확도가 몇 %야? | nemotron-3-ultra-550b-a55b | ~107,524 | ~2,459 | 97.7% | 1/4 | 2/4 | $0.0000 | $0.0000 |
| procurement-logistics-ai | P-T1 | ML 모델 정확도가 몇 %야? | deepseek-v4-flash | ~107,524 | ~2,459 | 97.7% | 1/4 | 2/4 | $0.0000 | $0.0000 |
| procurement-logistics-ai | P-T2 | QA 리포트에 나온 성능 수치 알려줘 | nemotron-3-ultra-550b-a55b | ~107,524 | ~2,459 | 97.7% | 3/4 | 3/4 | $0.0000 | $0.0000 |
| procurement-logistics-ai | P-T2 | QA 리포트에 나온 성능 수치 알려줘 | deepseek-v4-flash | ~107,524 | ~2,459 | 97.7% | 2/4 | 3/4 | $0.0000 | $0.0000 |
| procurement-logistics-ai | P-T3 | 프로젝트 모델 성능 요약해줘 | nemotron-3-ultra-550b-a55b | ~107,524 | ~2,425 | 97.7% | 3/4 | 3/4 | $0.0000 | $0.0000 |
| procurement-logistics-ai | P-T3 | 프로젝트 모델 성능 요약해줘 | deepseek-v4-flash | ~107,524 | ~2,425 | 97.7% | 2/4 | 3/4 | $0.0000 | $0.0000 |

---

## 상세 응답

### [P-T1] ML 모델 정확도가 몇 %야? — nemotron-3-ultra-550b-a55b

선택 파일: src/collect/build_map_summary.py, src/features/build_opportunity_matrix.py, src/modeling/demand_anomaly.py, docs/numbers_reference.md

**Raw 응답** (1/4)

ML 모델 정확도는 **98.6%** (홀드아웃 검증 기준)입니다.

## 관련 근거 파일 및 내용

### 1. `docs/check.md` (13차 검수 기록)
```
| 항목 | 값 |
|---|---|
| 훈련 데이터 | 86,991건 (전국 100,083건 중 키워드 규칙 매칭분) |
| 검증 정확도 | **98.58%** |
| confidence ≥ 0.55 비율 | 98.8% |
| 기타/미분류 재분류 가능 | 13,092건 중 3,857건 (29.5%) |
| 예상 최종 기타/미분류 비율 | 13.1% → **9.2%** (전국 raw 기준) |
```

### 2. `src/modeling/train_classifier.py` (훈련 스크

**CC 응답** (2/4)

제공된 컨텍스트에 따르면 **ML 품목 분류기 정확도는 98%**입니다.

**출처:**
- `docs/numbers_reference.md`: "98% | ML 품목 분류기 정확도 | 홀드아웃 테스트셋 

---

### [P-T1] ML 모델 정확도가 몇 %야? — deepseek-v4-flash

선택 파일: src/collect/build_map_summary.py, src/features/build_opportunity_matrix.py, src/modeling/demand_anomaly.py, docs/numbers_reference.md

**Raw 응답** (1/4)

우선 사용자가 "ML 모델 정확도가 몇 %야?"라고 물었습니다. 이 프로젝트에는 여러 ML 모델이 있을 수 있지만, 주로 공고명 분류를 위한 TF-IDF + LogisticRegression 모델이 있습니다. README나 check.md, train_classifier.py 등을 보면 정확도가 98.6% 또는 98.58% 등으로 언급됩니다. 구체적으로 어떤 모델을 말하는지 명확하지 않지만, 가장 대표적인 것은 item_category_detail 분류기입니다.

관련 파일:
- src/modeling/train_classifier.py: 훈련 스크립트, 검증 정확도 98.58% (홀드아웃 14,070건)
- src/modeling/item_classifier.py: 추론 모듈
- models/item_classifier.pkl: 저장된 모델
- check.md: 6차 검수 기록에 "검증 정확도 98.58%" 명시
- README.md: "정확도 98.6%" (ML 분류기 정확도)
- docs/numbers_reference.md: "98% — ML 품목

**CC 응답** (2/4)

우선 사용자의 질문은 "ML 모델 정확도가 몇 %야?"이다. 관련 컨텍스트를 보면 여러 문서에서 ML 분류기 정확도가 98%라고 명시되어 있다. 특히 docs/numbers_reference.md와 docs/slides_ppt_content.md에서 "98%", "ML 품목 분류기 정확도"라고 나와 있다. 또한 docs/data_dictionary.md에서도 "98% | ML 분류기 정확도 / 홀드아웃 14,070건 기준"이라고 확인된다.

사용자는 단순히 수치를 묻고 있다. 코드 수정이나 변경 요청이 아니라 정보 요청이다. 따라서 나는 직접 코드를 수정할 필요 없이, 관련 컨텍스트에서 찾은 정보를 바탕으로 답변하면 된다.

작업 요청은 "ML 모델 정확도가 몇 %야?"이므로, 나는 정확도를 알려주면 된다. 단, 나는 코드를 직접 수정하지 않는 AI 코딩 어시스턴트이므로, 정보 제공만 하면 된다.

답변은 간결하게 정확

---

### [P-T2] QA 리포트에 나온 성능 수치 알려줘 — nemotron-3-ultra-550b-a55b

선택 파일: src/collect/build_map_summary.py, docs/presentation_script.md, docs/numbers_reference.md, src/features/build_opportunity_matrix.py

**Raw 응답** (3/4)

# QA 리포트(check.md) 성능 수치 요약

`docs/check.md`(13차 검수 기록)에 명시된 주요 성능 수치는 다음과 같습니다.

---

## 1. ML 품목 분류기 (`src/modeling/train_classifier.py`)

| 지표 | 수치 | 비고 |
|------|------|------|
| **검증 정확도** | **98.58%** | 홀드아웃 테스트셋 14,070건 기준 |
| **confidence ≥ 0.55 비율** | 98.8% | 이 비율만 실제 예측에 활용 |
| **기타/미분류 재분류** | 13,092건 중 3,857건 (29.5%) | ML fallback으로 편입 |
| **예상 최종 기타/미분류 비율** | 13.1% → **9.2%** |

**CC 응답** (3/4)

The user is asking for the performance metrics from the QA report. Let me look through the provided context to find any QA report or performance metrics.

Looking at the context files:
1. `src/collect/build_map_summary.py` - shows code for building map summary with adjusted_score calculation
2. `docs/presentation_script.md` - presentation script with architecture description
3. `docs/numbers_reference.md` - core metrics definitions with various numbers
4. `src/features/build_opportunity_matrix.py` - opportunity matrix building code
5. `src/modeling/demand_anomaly.py` - blue ocean detection with Isolation Forest
6. `docs/slides_ppt_content.md` - slide content with data collection numbers
7. `src/recommendation/gemini_client.py` - Gemini client for recommendations
8. `docs/data_dictionary.md` - data dictionary with aggregation definitions

I don't see a specific "QA report" in the provided context. The `docs/numbers_reference.md` has some metrics like "98% ML 품목 분류기 정확도" (98% ML classifier accuracy), but that's not a QA report per se.

Let me check if there's any mention of Q

---

### [P-T2] QA 리포트에 나온 성능 수치 알려줘 — deepseek-v4-flash

선택 파일: src/collect/build_map_summary.py, docs/presentation_script.md, docs/numbers_reference.md, src/features/build_opportunity_matrix.py

**Raw 응답** (2/4)

We need to parse the user's request: "QA 리포트에 나온 성능 수치 알려줘". The user is asking for the performance metrics mentioned in the QA report. Looking at the context, there is a file `check.md` which contains QA records (13차). The user likely wants the performance numbers from that QA report, such as classification accuracy, coverage, etc.

From `check.md`, we can extract key performance metrics:

- Classification accuracy: ML 분류기 정확도 98.58% (from 6차), but later in 6차 it says "검증 정확도: 98.58%" and "기타/미분류 13.1% → 9.2%". Also in 11차: "ML 분류기 정확도 98.6%".
- Coverage: 전국 17개 시/도, 220개 지역, 100,083건.
- Competition matrix: 253개 지역, 10개 업종.
- Consumer fit: 242개 지역.
- Blue ocean: 50개 블루오션.
- Demand forecast: 587행, 6개월 예측.
- Opportunity matrix: 2,446

**CC 응답** (3/4)

我们는 사용자의 승인 없이 코드를 직접 수정하지 않는 AI 코딩 어시스턴트입니다. 사용자의 요청은 "QA 리포트에 나온 성능 수치 알려줘"입니다. 관련 컨텍스트에는 QA 리포트가 직접 포함되어 있지 않지만, 여러 문서에서 성능 수치를 찾을 수 있습니다. 사용자는 QA 리포트에 나온 성능 수치를 요청했으므로, 관련 컨텍스트에서 성능 관련 수치를 추출하여 알려주어야 합니다.

컨텍스트에서 성능 수치를 찾아보면:

- [3] docs/numbers_reference.md: "98% | ML 품목 분류기 정확도 | 홀드아웃 테스트셋 14,070건 기준" 
- [8] docs/data_dictionary.md: "98% | ML 분류기 정확도 / 홀드아웃 14,070건 기준 | 사무용품 Recall 0.57 약점 포함"

또한 [1] src/collect/build_map_summary.py에서 adjusted_score 계산 로직이 있지만 성능 수치는

---

### [P-T3] 프로젝트 모델 성능 요약해줘 — nemotron-3-ultra-550b-a55b

선택 파일: src/collect/build_map_summary.py, src/features/build_opportunity_matrix.py, src/modeling/demand_anomaly.py, docs/presentation_script.md

**Raw 응답** (3/4)

프로젝트의 모델 성능을 요약해 드리겠습니다. 관련 파일과 수치를 근거로 정리합니다.

---

## 📊 모델 성능 요약

### 1. **품목 분류 ML 모델 (TF-IDF + Logistic Regression)**

| 지표 | 수치 | 비고 |
|------|------|------|
| **검증 정확도** | **98.58%** | 홀드아웃 테스트셋 14,070건 기준 |
| **훈련

**CC 응답** (3/4)

The user is asking for a summary of the project model performance. Let me analyze the provided context to extract relevant information about model performance metrics.

From the context, I can see several relevant pieces of information:

1. From `docs/numbers_reference.md`:
   - **98%** - ML 품목 분류기 정확도 (홀드아웃 테스트셋 14,070건 기준) - from `src/modeling/train_classifier.py`

2. From `src/modeling/demand_anomaly.py`:
   - Uses Isolation Forest for anomaly detection (blue ocean detection)
   - Parameters: contamination=0.1, random_state=42
   - Features: opportunity_score, competition_score
   - Returns top_n=50 blue ocean candidates

3. From `src/collect/build_map_summary.py`:
   - adjusted_score calculation: opportunity_score × (survival_5y/100) × (1 - dissolution_rate)
   - Min-max normalization to 0-100 scale for adjusted_score_100

4. From `src/features/build_opportunity_matrix.py`:
   - opportunity_score = count_score(40%) + amount_score(

---

### [P-T3] 프로젝트 모델 성능 요약해줘 — deepseek-v4-flash

선택 파일: src/collect/build_map_summary.py, src/features/build_opportunity_matrix.py, src/modeling/demand_anomaly.py, docs/presentation_script.md

**Raw 응답** (2/4)

우선 사용자가 "프로젝트 모델 성능 요약해줘"라고 요청했습니다. 제공된 전체 레포지토리 정보를 바탕으로, 프로젝트에서 사용된 모델들의 성능을 요약해야 합니다.

프로젝트는 조달청 공모전 출품작으로, 공공조달 데이터를 분석하여 창업 입지·물류 거점을 추천하는 서비스입니다. 주요 모델은 크게 두 가지로 보입니다:

1. **ML 분류기 (item_classifier)**: 공고명을 19개 품목군으로 분류하는 TF-IDF + LogisticRegression 모델.
2. **수요 예측 모델 (demand_forecast)**: 선형 회귀 + 계절 성분을 이용한 월별 발주 건수 예측.
3. **이상 탐지 모델 (demand_anomaly)**: IsolationForest를 이용한 블루오션(수요공백) 탐지.

또한, AI 해석을 위해 Gemini API를 사용하지만 이는 분류/예측 모델이라기보다는 자연어 생성 모듈입니다

**CC 응답** (3/4)

우선 사용자의 요청은 "프로젝트 모델 성능 요약해줘"입니다. 관련 컨텍스트에는 여러 파일들이 주어져 있습니다. 이 중에서 모델 성능과 관련된 내용을 찾아야 합니다.

컨텍스트를 살펴보면:

- [3] src/modeling/demand_anomaly.py:22-67: 블루오션 탐지 모델 (Isolation Forest) 관련. 성능 지표는 없음.
- [5] docs/numbers_reference.md:8-37: "98% ML 품목 분류기 정확도" 언급. (홀드아웃 테스트셋 14,070건 기준)
- [7] src/recommendation/gemini_client.py:58-113: Gemini API 사용, 프롬프트 설계 관련. 성능 지표 없음.
- [1], [2], [4], [6], [8]는 주로 데이터 수집, 점수 산정, 아키텍처 설명 등.

따라서 모델 성능에 대한 직접적인 요약은 [5]의 "98

---

