# Prototype Progress

This file tracks the product path from idea to the current local beta.

## Current Status

Context Capsule is a working local-first public beta.

```text
local repo / meeting text / tester feedback
-> request or meeting understanding
-> relevant context retrieval
-> risk and approval checklist
-> handoff or collaboration packet
-> workflow graph trace
-> optional GitHub Issue dry-run
-> beta feedback save/review loop
```

## Status Board

| Status | Item | Notes |
| --- | --- | --- |
| Done | Request Understanding Layer | Normalizes rough Korean/English requests before retrieval. |
| Done | Repo scanner and classifier | Reads docs, code, config, and tests while excluding generated/local folders. |
| Done | Keyword/path retrieval | Default No-AI fallback. |
| Done | Optional hybrid/indexed retrieval | Local hash embedding fallback and persistent JSON index. |
| Done | Risk analyzer | Splits mention risk and change risk; blocks secret/prompt-injection contexts. |
| Done | Token Evidence | Local estimate only; not provider billing usage. |
| Done | Handoff packets | AI, teammate, junior, future-me, risk, GitHub Issue sections. |
| Done | GitHub Issue adapter | Dry-run by default; `--apply` required for real issue creation. |
| Done | FastAPI Korean UI | Replaces the confusing Streamlit sidebar flow with large workflow cards. |
| Done | Scrum Notes Mode | Meeting text -> decisions, blockers, next actions, issue drafts. |
| Done | Project Kickoff Mode | Idea notes -> MVP scope, workstreams, risks, checklist. |
| Done | Project Health Check | Meeting/status text -> MVP/prototype readiness and missing meeting questions. |
| Done | Ownership Check | Compares meeting text with self-declared scope to ask if this is really my part. |
| Done | Beta Feedback Loop | Saves tester feedback and reviews repeated issues into next patch priorities. |
| Current | Workflow Graph Trace | Shows the Work Handoff node path and explains completed, skipped, blocked, or needs-input steps. |
| Next | v0.2.x beta polish | Apply repeated tester feedback from Feedback Review. |
| Backlog | Token Analyzer adapter | Compare local estimate with actual provider/tool usage when available. |
| Backlog | Discord adapter | Meeting input channel after text-based workflow is stable. |
| Backlog | Chroma/FAISS backend | Optional stronger retrieval backend after evaluation metrics are stable. |

## Implemented CLI Flow

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "로그인 안돼" --target all --save --json
.\context_capsule_cli.bat create-issue outputs\YYYYMMDD_HHMMSS_slug --repo owner/name --json
.\context_capsule_cli.bat feedback-save --mode work --request "로그인 안돼" --expected-file backend/auth/login.py --actual-file README.md --output-dir outputs\feedback --json
.\context_capsule_cli.bat feedback-review --feedback-root outputs\feedback --save --json
```

## Validation Baseline

The exact number changes as tests are added. Run the current baseline with:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m compileall app tests scripts
.\.venv\Scripts\python.exe scripts\validate_mvp.py --repeat 10
.\.venv\Scripts\python.exe scripts\validate_user_speech.py --repo-path .
```

## Product Direction

Short version:

> Turn "이거 해줘" into a scoped, reviewable work card.

Expanded version:

> Context Capsule is a local-first handoff system that structures task scope, relevant files, risks, acceptance criteria, meeting decisions, readiness gaps, and tester feedback before AI coding tools or teammates start work.

## v0.2.x Direction

```text
v0.2.0 = meeting notes and kickoff packets
v0.2.1 = FastAPI Korean UI + Project Health Check
v0.2.2 = Beta Feedback Loop
v0.2.3 = workflow graph trace for handoff trust
```

The product remains human-in-the-loop. It can suggest next actions and questions, but final owner assignment, code changes, issue creation, and release decisions stay with people.
