# Korean RAG Quality Scan

Date: 2026-07-02

Purpose: decide how to improve Context Capsule retrieval quality for Korean user requests over mixed Korean/English repositories.

## Current Baseline

Context Capsule currently has three retrieval modes:

- `keyword`: deterministic keyword/path scoring with Korean-English domain synonyms.
- `hybrid`: keyword/path score plus a local vector similarity score.
- `indexed`: persistent local JSON index that falls back to hybrid when missing, stale, or provider-incompatible.

The default vector provider is `hash_local_v1`. It is useful for closed-network testing, but it is not a semantic embedding model.

## Findings

### 1. Multilingual embedding can help Korean query -> English code retrieval

The main quality gap is cross-lingual intent matching:

```text
결제 실패 고쳐줘 -> payment_service.py
로그인이 모바일에서만 안돼 -> backend/auth/login.py
```

Keyword synonym expansion helps, but it does not scale forever. A real multilingual embedding model should be evaluated behind the existing provider boundary.

Candidate models:

| Model | Why it matters | Caveat |
| --- | --- | --- |
| `intfloat/multilingual-e5-large` | Widely used multilingual retrieval model, supports Korean and sentence-transformers usage. | Needs `query:` / `passage:` prefixes and truncates long text at 512 tokens. |
| `BAAI/bge-m3` | Multilingual, multi-function, multi-granularity model; supports long inputs and dense/sparse/multi-vector concepts. | Heavier than hash baseline; sparse/multi-vector features are not wired yet. |
| `Qwen/Qwen3-Embedding-0.6B` | Recent multilingual embedding model with strong MTEB multilingual scores and query instruction support. | Query-side instruction must be handled correctly. |

Implementation decision:

- Keep `keyword` as the default no-dependency path.
- Keep `hash_local_v1` for CI and closed-network fallback.
- Add model-specific input formatting for known embedding families.
- Require benchmark proof before making a model the default.

### 2. Hybrid retrieval should stay

BGE-M3 and Qdrant docs both reinforce the same product direction: do not rely on dense vectors alone. Combine lexical/path signals with dense retrieval and evaluate fusion on real tasks.

For Context Capsule, lexical/path signals are not optional because:

- explicit files must stay mandatory
- folder scope such as `frontend-rn only` must beat semantic similarity
- protected areas such as `auth는 건드리지 마` are safety constraints, not semantic suggestions

Implementation decision:

- Dense embedding can reorder candidates.
- It must not override mandatory file/path/scope rules.
- Later vector DB adapters should support dense+sparse fusion, but only after local quality benchmarks exist.

### 3. Chunking should be document-aware, not one-size-fits-all

The old baseline used fixed 80-line chunks for every file.

Research and production docs agree that chunking affects RAG quality, but the right strategy depends on the document type and task. Recent code RAG research also warns that function-only chunking is not automatically best for code completion.

Implementation decision for v0.3 groundwork:

- Markdown docs: split by headings first, then line-window oversized sections.
- Code files: keep stable line-window chunks for now.
- Future eval: compare fixed line, Markdown heading, sliding window, and AST/code-aware chunking on external repos.

### 4. Reranking is promising, but not first

SentenceTransformers documents retrieve-and-rerank as a standard pattern, and BGE-M3 recommends hybrid retrieval plus reranking.

For Context Capsule, reranking should come after we have:

- hit@1 / hit@3 benchmark
- expected files per task
- scope escape checks
- token budget effect

Otherwise we will not know whether reranking helped or just made the system slower.

## Changes Applied Now

- Added Markdown heading-aware chunking for `.md` / `.markdown` docs.
- Added E5-style `query:` / `passage:` formatting.
- Added Qwen3 query instruction formatting.
- Kept BGE-M3 and unknown models as raw text input.
- Included the embedding input profile in the provider name so old indexes do not silently mix incompatible vectors.

## Next Evaluation Set

Add a Korean RAG quality benchmark with cases like:

```text
로그인이 모바일에서만 안돼 -> backend/auth/login.py
결제 실패 고쳐줘 -> payment_service.py
frontend-rn만 봐, frontend는 보지마 -> frontend-rn/* only
리드미를 포트폴리오용으로 다듬어줘 -> root README or scoped README
ML 정확도 몇 %야? -> qa/metric evidence docs
```

Metrics:

- hit@1
- hit@3
- scope escape count
- irrelevant README count
- risk false positive count
- retrieved context tokens
- runtime / index build time

## Sources

- SentenceTransformers pretrained/retrieve-and-rerank docs: https://www.sbert.net/docs/sentence_transformer/pretrained_models.html
- Multilingual E5 model card: https://huggingface.co/intfloat/multilingual-e5-large
- BGE-M3 model card: https://huggingface.co/BAAI/bge-m3
- BGE-M3 paper: https://arxiv.org/abs/2402.03216
- Qwen3 Embedding model card: https://huggingface.co/Qwen/Qwen3-Embedding-0.6B
- Qdrant hybrid queries docs: https://qdrant.tech/documentation/search/hybrid-queries/
- Code RAG chunking study: https://arxiv.org/abs/2605.04763
- Adaptive chunking study: https://arxiv.org/abs/2603.25333
