# Demo Capture Flow

Use this flow for portfolio screenshots, presentation slides, or a short demo video.

## Minimal v0.2.8 Story

Use this when the demo must be short:

```text
README first screen
-> target positioning for junior developers and interviewers
-> KDT tester start box
-> START_HERE_KO.md
-> dashboard loading status
-> Token Evidence in Overview
-> Scrum Notes Mode issue draft
-> Project Kickoff Mode role questions
-> user-speech indexed retrieval demo
-> GitHub Issue dry-run / saved packet
```

The message:

```text
Context Capsule helps junior developers prepare safer AI coding requests before any code changes begin.
```

## Capture 1: README First Screen

Show:

- One-line product explanation
- primary user / secondary reader positioning
- KDT tester start box
- Korean quickstart link
- first-run dashboard guide image
- Local app quick start
- Request Understanding examples
- indexed retrieval quick start
- release ZIP link

Purpose:

```text
"This is not an auto-coding bot. It helps a junior developer define scope, risk, and evidence before asking AI to work."
```

## Capture 2: User-Speech Indexed Retrieval

Command:

```powershell
.\.venv\Scripts\python.exe scripts\demo_user_speech.py
```

Capture:

- `리드미 손보자 -> README.md`
- `심플 리트리버 왜 이럼 -> app/retrievers/simple_retriever.py`
- `auth는 건드리지 말고 문서만 -> protected=auth`
- `이거 왜그래? -> clarification_only`

Purpose:

```text
"The tool handles real user phrasing instead of only polished prompts."
```

## Capture 3: CLI Generate With Saved Output

Command:

```powershell
.\context_capsule_cli.bat index --repo-path . --json
.\context_capsule_cli.bat generate --repo-path . --task "리드미 손보자" --retriever indexed --target all --save --json
```

Capture:

- `saved_output_dir`
- `token_budget`
- `risk_level`
- `auto_start_allowed`

Purpose:

```text
"The engine works without the dashboard."
```

## Capture 4: GitHub Issue Dry-Run

Command:

```powershell
.\context_capsule_cli.bat create-issue outputs\YYYYMMDD_HHMMSS_slug --repo mosejong/context-capsule --json
```

Capture:

- `"mode": "dry-run"`
- issue title
- labels
- acceptance criteria
- auto-start gate

Purpose:

```text
"No GitHub write happens until --apply is explicitly used."
```

## Optional Capture: Local Dashboard Start

Command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_dashboard.ps1
```

Capture:

- Terminal showing `http://localhost:8501`
- Browser showing the Context Capsule dashboard
- Result area showing generation status after `Generate Capsule`
- Overview tab showing Token Evidence and Estimated only status

## Optional Capture: Scrum/Kickoff Packets

Use the dashboard tabs or CLI:

```powershell
.\context_capsule_cli.bat scrum-notes --text-file .\tests\fixtures\scrum_runtime_issue_ko.txt --project-context "KDT beta project" --json
.\context_capsule_cli.bat kickoff --topic "Context Capsule v0.2" --notes-file .\tests\fixtures\project_kickoff_context_capsule_ko.txt --deadline "2 weeks" --json
```

Capture:

- decisions
- blockers
- next actions
- role-discussion questions
- issue drafts
- safety notes

Purpose:

```text
"v0.2 turns meeting text into reviewable execution packets without teammate scoring or automatic assignment."
```

Purpose:

```text
"A user can download the ZIP and run this locally."
```

## Optional Capture: Saved Output Packet

Open the generated output folder:

```text
outputs/YYYYMMDD_HHMMSS_slug/
```

Capture:

- `AI_HANDOFF_PROMPT.md`
- `TEAMMATE_BRIEF.md`
- `RISK_CHECKLIST.md`
- `GITHUB_ISSUE.md`
- `metadata.json`

Purpose:

```text
"One request becomes multiple target-specific work packets."
```

## Optional Capture: Performance Report

Open:

```text
docs/assets/performance_comparison.svg
docs/reports/performance_comparison.md
```

Capture:

- average token reduction
- relevant file hit rate
- scope escape count

Purpose:

```text
"The demo has measurable validation signals, not only a nice prompt."
```

## 30-Second Talk Track

```text
Developers usually tell AI, "fix this", then the model searches too broadly and may touch risky files.
Context Capsule first normalizes rough requests like "리드미 손보자" or "auth는 건드리지 말고 문서만", then scans the repo locally, retrieves only task-relevant context, flags risk, and generates handoff packets for AI tools, teammates, or future me.
The CLI can save the packet and preview a GitHub Issue as a dry-run.
High-risk work is blocked until a human approves the scope.
```

