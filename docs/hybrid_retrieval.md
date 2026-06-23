# Hybrid Retrieval

Context Capsule keeps keyword/path retrieval as the default because it is fast, deterministic, and works in closed-network environments.

Hybrid retrieval is optional:

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "Find the files for a login API fix" --retriever hybrid --json
```

## Modes

| Mode | Behavior | Network Requirement |
| --- | --- | --- |
| `keyword` | Keyword/path-aware ranking with mandatory include for mentioned files. | None |
| `hybrid` | Keyword/path ranking plus local vector similarity. Falls back to keyword if embedding fails. | None by default |

## Default Hybrid Provider

Without extra setup, hybrid mode uses `hash_local_v1`, a deterministic local hash embedding provider.

This is not a semantic foundation model. It exists so that:

- hybrid ranking can be tested without external APIs
- closed-network mode keeps working
- CI does not need to download models
- the project has a provider boundary for real local embedding models

## Optional Local Embedding Model

To use `sentence-transformers`, install the optional RAG dependencies and set a model path or model name:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-rag.txt
$env:CONTEXT_CAPSULE_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
.\context_capsule_cli.bat generate --repo-path . --task "Find related auth files" --retriever hybrid --json
```

For closed-network use, set `CONTEXT_CAPSULE_EMBEDDING_MODEL` to a locally available model path. If the model cannot load, Context Capsule falls back to the built-in hash provider or keyword retrieval instead of failing the packet generation flow.

## Safety Rules

- Explicitly mentioned files still win. `README`, `docs/local_app.md`, or `app/cli.py` remain mandatory top context when they exist.
- Keyword retrieval remains the fallback.
- No external AI API is called by retrieval.
- Generated packets should still be reviewed by a human before risky execution.

## Future Upgrade

The next retrieval upgrade is a persistent vector index:

- Chroma or FAISS index
- incremental re-indexing
- per-file-type chunking
- benchmark report: keyword vs hybrid vs indexed hybrid
