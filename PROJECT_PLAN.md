# Context Capsule Project Plan

## Purpose

Context Capsule turns rough work requests, meeting notes, and tester feedback into local, reviewable work packets.

The project is not an auto-coding tool. The core idea is human-in-the-loop control: understand the request first, scan the repository locally, retrieve only relevant context, flag risky areas, and generate a brief that a person can approve before implementation starts.

## Problem

AI coding and team handoff often fail because the handoff is weak:

1. The model sees too much unrelated repository context.
2. Important files are missed.
3. Auth, DB, env, deployment, and API contract changes are handled too casually.
4. Forbidden rules fade during long conversations.
5. Completion criteria are unclear.
6. Meetings end without clear next actions.
7. Tester feedback disappears into chat instead of becoming the next patch queue.

The same issue appears in human teamwork. A teammate may not be blocked by skill, but by unclear scope, missing starting points, vague acceptance criteria, or missing ownership confirmation.

## Solution

Context Capsule combines:

- task request or meeting text
- repository scan
- request understanding
- relevant files
- risk findings
- forbidden rules
- token evidence estimate
- approval checklist
- acceptance criteria
- tester feedback

It generates:

- AI handoff prompt
- teammate brief
- junior guide
- future-me note
- risk checklist
- GitHub Issue draft
- scrum notes packet
- project kickoff packet
- project health check
- feedback review packet

## Current MVP Scope

Included:

- Python 3.11+ local app
- FastAPI Korean local UI
- local repository scanner
- Request Understanding Layer for colloquial task requests
- keyword/path task-aware retrieval
- optional hybrid retrieval
- persistent indexed retrieval
- Korean-to-English domain keyword hints
- context redaction for secrets and prompt-injection-like lines
- rule-based risk analyzer
- token evidence estimate
- target-specific handoff generation
- saved output packets
- GitHub Issue dry-run/apply adapter
- CLI generate, doctor, index, scrum, kickoff, health
- Beta Feedback Loop with `feedback-save` and `feedback-review`
- Windows launcher scripts
- validation and performance report scripts
- GitHub Release ZIP build script

Excluded:

- automatic code changes
- automatic merge/deploy
- automatic teammate scoring
- automatic role assignment
- required external LLM API calls
- credential collection
- Discord adapter
- external Token Analyzer adapter
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
-> token evidence
-> handoff generator
-> saved output packet
-> GitHub Issue dry-run
```

```text
Meeting notes / kickoff notes
-> rule-based meeting analyzer
-> decisions / blockers / actions / questions
-> issue drafts
-> health readiness signals
```

```text
Tester feedback
-> safe feedback save
-> feedback review
-> common issues
-> next patch priorities
-> regression test candidates
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
8. Feedback text is untrusted input and is redacted before saving.
9. Project Health and Feedback Review do not score teammates or assign owners.

## Validation Strategy

The MVP is validated with:

- unit tests
- scenario validation
- compile check
- FastAPI dashboard dry-run
- CLI generate -> create-issue dry-run
- CLI feedback-save -> feedback-review
- release ZIP verification
- user-speech retrieval QA

## Next Phases

1. v0.2.2 GitHub Release publication.
2. KDT tester feedback collection through the new feedback loop.
3. v0.2.3 repeated-feedback polish.
4. External Token Analyzer adapter.
5. Discord input adapter.
6. Retrieval evaluation metrics and optional stronger RAG backend.

