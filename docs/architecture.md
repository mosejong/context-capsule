# Architecture

Context Capsule is a local-first handoff packet generator.

It does not send the whole repository to an LLM. It scans local files, retrieves task-relevant context, analyzes risk, estimates token budget, and generates target-specific handoff outputs.

## High-Level Flow

```text
task request / chat log
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

### Retriever

The v0.1.0 retriever is keyword/path based.

It favors:

- exact file path mentions
- task terms
- snake_case and space-separated matches
- README/docs/config context when relevant

Future versions can add Chroma/FAISS and local embedding models behind the same service boundary.

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

v0.1.0 uses `approx_local_v1`.

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
  -> Streamlit dashboard
  -> CLI generate
  -> future Discord adapter

saved output packet
  -> CLI create-issue
  -> future GitHub/Discord workflow
```

This keeps core generation reusable across UI, CLI, and future integrations.

## Technology Choices

| Layer | v0.1.0 | Future |
| --- | --- | --- |
| UI | Streamlit | desktop shell or web app |
| CLI | argparse | packaged executable |
| Retrieval | keyword/path scoring | hybrid keyword + vector search |
| Vector DB | none | Chroma or FAISS |
| LLM | not required | local LLM or external provider adapter |
| Token usage | local estimate | provider usage adapter |
| Packaging | GitHub Release ZIP | PyInstaller or installer |

## Security Model

- No external AI API is required for MVP features.
- Repository context stays local unless the user copies/sends it.
- GitHub writes require explicit `--apply`.
- Generated packets are local artifacts under ignored `outputs`.
- Release ZIP excludes local state, caches, and credentials.
