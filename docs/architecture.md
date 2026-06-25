# Architecture

Context Capsule is a local-first handoff packet generator.

It does not send the whole repository to an LLM. It normalizes the user request, scans local files, retrieves task-relevant context, analyzes risk, estimates token budget, and generates target-specific handoff outputs.

## High-Level Flow

```text
task request / chat log
-> request understanding
-> repository scan
-> file classification
-> task-aware retrieval
-> risk analysis
-> token budget analysis
-> target-specific handoff generation
-> saved output packet
-> GitHub Issue dry-run
```

## Components

### Repo Scanner

Reads local repository files that are useful for handoff generation:

- docs
- source code
- config files
- tests

It excludes local/generated folders:

- `.git`
- `.venv`, `venv`, `env`
- `outputs`
- `dist`, `build`
- cache folders
- `node_modules`

### File Classifier

Classifies files into:

| Kind | Examples |
| --- | --- |
| doc | `README.md`, `docs/*.md` |
| code | `*.py`, `*.js`, `*.ts`, `*.tsx` |
| config | `requirements.txt`, `pyproject.toml`, `.env.example` |
| test | `test_*.py`, `*.spec.ts` |

### Request Understanding Layer

Normalizes colloquial user requests before retrieval.

It extracts:

- intent
- target hints
- protected hints
- file hints
- retrieval search query
- clarification question when confidence is low

Low-confidence requests produce a clarification-only packet instead of retrieving repository context.

### Retriever

The baseline retriever is keyword/path based.

It favors:

- exact file path mentions
- task terms
- snake_case and space-separated matches
- README/docs/config context when relevant

v0.1.2 also supports persistent local indexed retrieval and optional hybrid retrieval.
Both keep the keyword/path retriever as fallback so No-AI Mode and closed-network use remain available.

### Risk Analyzer

Risk rules identify:

- secret/env/credential risk
- auth/JWT/login/password risk
- DB schema/migration/model risk
- deploy/nginx/docker/production risk
- API response/router/endpoint risk
- test/verification need

The analyzer separates:

- `mention_risk`: risky concept is mentioned
- `change_risk`: task likely intends to change the risky area

This avoids treating a README mention of "auth" or "secret" as the same thing as changing login or credential code.

### Token Budget Analyzer

The current local token provider uses `approx_local_v1`.

It estimates:

- candidate file context tokens
- retrieved context tokens
- final handoff prompt tokens
- estimated reduction percentage

The candidate file baseline uses the full contents of files selected by retrieval, not the whole repository concat. The value is a local estimate, not provider billing usage.

### Handoff Generator

Generates structured sections:

- overview
- AI handoff prompt
- teammate brief
- junior guide
- future-me handoff
- risk checklist
- GitHub issue packet

### Output Writer

Writes reusable packets under:

```text
outputs/YYYYMMDD_HHMMSS_slug/
```

`outputs/` is ignored by git and excluded from release ZIPs.

### CLI

Main commands:

```powershell
python -m app.cli generate --repo-path . --task "..." --target all --save --json
python -m app.cli create-issue outputs\YYYYMMDD_HHMMSS_slug --repo owner/name --json
```

The CLI shares the same `capsule_service.py` generation service as Streamlit.

### GitHub Issue Adapter

The adapter reads a saved packet and builds an issue payload.

Safety defaults:

- dry-run by default
- `--apply` required for real GitHub writes
- token read from `GITHUB_TOKEN` or `GH_TOKEN`
- token never written to packet files

## Service Boundary

```text
app/services/capsule_service.py
  -> FastAPI Korean local UI
  -> Legacy Streamlit prototype
  -> CLI generate
  -> future Discord adapter

saved output packet
  -> CLI create-issue
  -> future GitHub/Discord workflow
```

This keeps core generation reusable across UI, CLI, and future integrations.

## Technology Choices

| Layer | Current | Future |
| --- | --- | --- |
| UI | Streamlit | desktop shell or web app |
| CLI | argparse | packaged executable |
| Retrieval | keyword/path, optional hybrid, persistent indexed retrieval | Chroma/FAISS backend adapter |
| Vector DB | local JSON index, optional embedding provider | Chroma or FAISS |
| LLM | not required | local LLM or external provider adapter |
| Token usage | local estimate | provider usage adapter |
| Packaging | GitHub Release ZIP | PyInstaller or installer |

## Security Model

- No external AI API is required for MVP features.
- Repository context stays local unless the user copies/sends it.
- GitHub writes require explicit `--apply`.
- Generated packets are local artifacts under ignored `outputs`.
- Release ZIP excludes local state, caches, and credentials.
