# Prototype Progress

This file tracks the product path from idea to v0.1.0 local release candidate.

## Current Status

Context Capsule is now a working local-first MVP:

```text
local repo + task request
-> relevant context retrieval
-> risk and approval checklist
-> target-specific handoff packet
-> saved outputs
-> GitHub Issue dry-run
-> release ZIP packaging
```

## Status Board

| Status | Item | Notes |
| --- | --- | --- |
| Done | Repository scaffold | README, plan, docs, app structure, license. |
| Done | Python 3.13 setup | Local `.venv` flow and dependency split. |
| Done | Streamlit dashboard | Local UI for task request, rules, tabs, and saved packets. |
| Done | Repo scanner | Reads docs, code, config, and tests while excluding local/generated folders. |
| Done | File classifier | Classifies docs, code, config, and tests. |
| Done | Task-aware retrieval | Keyword/path-aware retrieval for MVP. |
| Done | Retrieval quality hotfix | Mentioned files are mandatory top context and duplicate file chunks are deduplicated. |
| Done | Optional hybrid retrieval | `--retriever hybrid` adds local vector ranking with keyword fallback. |
| Done | Persistent retrieval index | `context_capsule_cli.bat index` builds a local JSON index for `--retriever indexed`. |
| Done | Risk analyzer | Detects auth, DB, secret, deploy, API, and test risk signals. |
| Done | Mention/change risk split | README/docs mentions are not treated the same as requested code changes. |
| Done | Token budget | Local `approx_local_v1` token estimate and reduction view. |
| Done | Target handoff modes | AI, teammate, junior, and future-self sections. |
| Done | Saved output packet | Writes Markdown/JSON artifacts under ignored `outputs/`. |
| Done | GitHub Issue adapter | Dry-run by default, explicit `--apply` for real writes. |
| Done | CLI generate | Runs the packet flow without Streamlit. |
| Done | Demo scenario | Fixed login API error scenario with dry-run issue payload. |
| Done | Performance report | Markdown + SVG report from MVP validation scenarios. |
| Done | Windows launcher | `run_context_capsule.bat` and PowerShell launchers. |
| Done | Release ZIP script | `scripts/build_release.ps1` creates `dist/context-capsule-v0.1.0.zip`. |
| Done | Scrum Notes Mode | Text input -> decisions, blockers, next actions, issue drafts. |
| Done | Project Kickoff Mode | Topic + idea notes -> MVP scope, workstreams, checklist. |
| Done | Publish v0.1.0 release | ZIP and release notes published to GitHub Releases. |
| Next | Demo screenshots | Capture README, dashboard, CLI, dry-run issue, and performance SVG. |
| Backlog | Discord adapter | Convert fixed meeting decisions into packets/issues. |
| Backlog | Token-analyzer adapter | Connect external analyzer behind provider boundary. |
| Backlog | Hybrid RAG backend | Add Chroma/FAISS backend adapter and incremental indexing. |

## Implemented Flow

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "Create a login API fix handoff packet" --target all --save --json
.\context_capsule_cli.bat create-issue outputs\YYYYMMDD_HHMMSS_slug --repo mosejong/context-capsule --json
```

## Validation Baseline

```text
pytest: 59 passed
MVP scenarios: 5 scenarios x 10 runs passed
Dashboard smoke: HTTP 200 on local Streamlit test port
CLI generate -> create-issue dry-run verified
Release ZIP verification passed
CLI scrum-notes/kickoff verified
README and simple_retriever retrieval hotfix smoke verified
Hybrid retriever CLI smoke verified
Indexed retriever CLI smoke verified
```

## v0.1.0 Release Candidate

Release package:

```text
dist/context-capsule-v0.1.0.zip
```

Included:

- source code
- launcher scripts
- runtime requirements
- docs
- release notes
- validation scripts
- tests

Excluded:

- `.venv`
- `outputs`
- `dist`
- caches
- local credentials

## Product Direction

Short version:

> Turn "fix this" into a reviewable work card.

Expanded version:

> Context Capsule is a local-first handoff system that structures task scope, relevant files, risks, acceptance criteria, and verification steps before AI coding tools or teammates start work.

## v0.2 Direction

v0.2 adds meeting and kickoff planning:

- Scrum Notes Mode
- Project Kickoff Mode
- issue drafts from meeting text
- team-lead notes
- explicit no-scoring/no-auto-assignment boundary

The product remains human-in-the-loop. Meeting text can suggest next actions, but final owner assignment stays with the human lead.

## v0.1.1 Hotfix Direction

The first real review found that retrieval quality matters more than adding new surfaces.

Fixed:

- explicit file/path mentions are mandatory top context
- README/docs tasks prefer documentation files
- code tasks can still pull code and adapter files
- duplicate chunks from the same file are removed by default
- negated risk instructions such as "do not touch auth" no longer become HIGH change risk

Still planned:

- Chroma/FAISS backend adapter
- better token baseline against actual provider usage
