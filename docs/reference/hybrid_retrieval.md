# Hybrid Retrieval

Context Capsule keeps keyword/path retrieval as the default because it is fast, deterministic, and works in closed-network environments.

Hybrid retrieval is optional:

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "Find the files for a login API fix" --retriever hybrid --json
```

Build and reuse a persistent local retrieval index:

```powershell
.\context_capsule_cli.bat index --repo-path . --json
.\context_capsule_cli.bat generate --repo-path . --task "Find the files for a login API fix" --retriever indexed --json
```

## Modes

| Mode | Behavior | Network Requirement |
| --- | --- | --- |
| `keyword` | Keyword/path-aware ranking with mandatory include for mentioned files. | None |
| `hybrid` | Keyword/path ranking plus local vector similarity. Falls back to keyword if embedding fails. | None by default |
| `indexed` | Reads `.context-capsule-index/retrieval_index.json`, then falls back to hybrid if the index is missing, stale, or built with a different provider. | None by default |

`indexed` fallback is visible in generated output through `retrieval_report`:

```json
{
  "requested_mode": "indexed",
  "used_mode": "hybrid_fallback",
  "fallback_reason": "retrieval index is stale"
}
```

## Default Hybrid Provider

Without extra setup, hybrid and indexed modes use `hash_local_v1`, a deterministic local hash embedding provider.

This is not a semantic foundation model. It exists so that:

- hybrid ranking can be tested without external APIs
- closed-network mode keeps working
- CI does not need to download models
- the project has a provider boundary for real local embedding models

## Optional Local Embedding Model

To use `sentence-transformers`, install the optional RAG dependencies and set a model path or model name:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-rag.txt
$env:CONTEXT_CAPSULE_EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
.\context_capsule_cli.bat generate --repo-path . --task "Find related auth files" --retriever hybrid --json
```

For closed-network use, set `CONTEXT_CAPSULE_EMBEDDING_MODEL` to a locally available model path. If the model cannot load, Context Capsule falls back to the built-in hash provider or keyword retrieval instead of failing the packet generation flow.

### Korean / Multilingual Profiles

Context Capsule formats embedding inputs for known multilingual retrieval models:

| Model family | Query formatting | Passage formatting | Why |
| --- | --- | --- | --- |
| `multilingual-e5-*` | `query: ...` | `passage: ...` | E5 model cards require query/passage prefixes for retrieval tasks. |
| `Qwen3-Embedding-*` | `Instruct: ...\nQuery: ...` | raw text | Qwen3 recommends task instructions on the query side and no instruction for documents. |
| `BAAI/bge-m3` | raw text | raw text | BGE-M3 model card says query instructions are no longer required. |
| other models | raw text | raw text | Keep unknown providers conservative. |

The input profile is included in the provider name. If an existing local index was built with a different profile, `indexed` mode falls back instead of silently mixing incompatible vectors.

Recommended local candidates to evaluate:

- `intfloat/multilingual-e5-large`: strong multilingual baseline, but truncates long texts at 512 tokens.
- `BAAI/bge-m3`: multilingual, supports dense/sparse/multi-vector concepts, and accepts longer inputs.
- `Qwen/Qwen3-Embedding-0.6B`: strong multilingual embedding model with explicit query instruction support.

## Safety Rules

- Explicitly mentioned files still win. `README`, `docs/local_app.md`, or `app/cli.py` remain mandatory top context when they exist.
- Keyword retrieval remains the fallback.
- No external AI API is called by retrieval.
- Generated packets should still be reviewed by a human before risky execution.

## Future Upgrade

The next retrieval upgrade is an evaluated Korean RAG quality track:

- benchmark: keyword vs hash hybrid vs multilingual embedding
- hit@1/hit@3 on Korean user-speech tasks over English/Korean repos
- section-aware Markdown chunking and code-aware chunking comparison
- optional reranker after top-k retrieval
- Chroma, FAISS, or Qdrant backend adapter
- incremental re-indexing
- benchmark report: keyword vs hybrid vs indexed multilingual retrieval
