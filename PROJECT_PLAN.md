# Context Capsule Project Plan

## Purpose

Context Capsule turns a vague work request into a small, reviewable handoff packet for AI coding tools, teammates, junior developers, and future-you.

The project is not an auto-coding tool. The core idea is human-in-the-loop control: scan the repository locally, retrieve only relevant context, flag risky areas, and generate a work brief that a person can approve before implementation starts.

## Problem

AI coding work often fails because the handoff is weak:

1. The model receives too much unrelated context.
2. Important files are missed.
3. Auth, DB, env, deployment, and API contract changes are handled too casually.
4. Forbidden rules fade during long conversations.
5. Completion criteria are unclear.
6. Teams spend time re-explaining repository context.

The same issue appears in human teamwork. A teammate may not be blocked by skill, but by unclear scope, missing starting points, and vague acceptance criteria.

## Solution

Context Capsule scans the local repository and combines:

- task request
- relevant files
- risk findings
- forbidden rules
- token budget estimate
- approval checklist
- acceptance criteria

It then generates target-specific outputs:

- `AI_HANDOFF_PROMPT.md`
- `TEAMMATE_BRIEF.md`
- `JUNIOR_GUIDE.md`
- `SELF_HANDOFF.md`
- `RISK_CHECKLIST.md`
- `GITHUB_ISSUE.md`
- `DECISION_RECORD.md`
- `metadata.json`

## MVP Scope

Included in the current local MVP:

- Python 3.13 local app
- Streamlit dashboard
- local repository scanner
- Request Understanding Layer for colloquial task requests
- keyword/path task-aware retrieval
- optional hybrid retrieval
- persistent indexed retrieval
- rule-based risk analyzer
- token budget estimate
- target-specific handoff generation
- saved output packets
- GitHub Issue dry-run/apply adapter
- CLI generate flow
- CLI Scrum Notes and Project Kickoff modes
- Windows launcher scripts
- fixed demo scenario
- validation and performance report scripts
- GitHub Release ZIP build script

Still excluded:

- automatic code changes
- automatic merge/deploy
- required external LLM API calls
- credential collection
- Discord adapter
- external Token-analyzer adapter
- Chroma/FAISS backend adapter
- local LLM summarization

## System Flow

```text
Repository path + task request
-> request understanding
-> repo scanner
-> file classifier
-> task-aware retriever
-> risk analyzer
-> token budget analyzer
-> handoff generator
-> saved output packet
-> GitHub Issue dry-run
```

## Handoff Targets

| Target | Purpose |
| --- | --- |
| `ai_tool` | Prompt Claude, Codex, or ChatGPT with scope, relevant files, risks, and verification steps. |
| `teammate` | Give a teammate a practical brief with first files, today-sized tasks, and completion criteria. |
| `junior_developer` | Break the task into smaller steps with checklist-style guidance. |
| `future_me` | Preserve current state, next action, and cautions for tomorrow. |

## Safety Principles

1. Dry-run first.
2. Human approval before high-risk work.
3. No external AI API required for MVP features.
4. GitHub writes require explicit `--apply`.
5. Tokens and credentials are read from environment variables only.
6. Generated packets stay under ignored `outputs/`.
7. Scanner excludes local/generated folders such as `.venv`, `outputs`, `dist`, and caches.

## Validation Strategy

The MVP is validated with:

- unit tests
- scenario validation
- compile check
- dashboard smoke check
- CLI generate -> create-issue dry-run
- release ZIP verification
- performance comparison report

The current baseline is:

```text
pytest: 73 passed
MVP scenarios: 5 scenarios x 10 runs passed
User-speech QA: 11 passed, 0 warn, 0 fail
```

## Next Phases

1. v0.1.2 GitHub Release publication and demo screenshots.
2. Discord input adapter.
3. External Token-analyzer adapter.
4. Chroma/FAISS backend adapter.
5. Closed-network install bundle.
6. Local LLM provider adapter.
