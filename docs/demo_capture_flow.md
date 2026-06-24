# Demo Capture Flow

Use this flow for portfolio screenshots, presentation slides, or a short demo video.

## Minimal v0.1.6 Story

Use this when the demo must be short:

```text
README first screen
-> KDT tester start box
-> user-speech indexed retrieval demo
-> GitHub Issue dry-run / saved packet
```

The message:

```text
Context Capsule understands rough work requests before retrieval, selects a small set of target files, and keeps risky execution behind review.
```

## Capture 1: README First Screen

Show:

- One-line product explanation
- KDT tester start box
- first-run dashboard guide image
- Local app quick start
- Request Understanding examples
- indexed retrieval quick start
- release ZIP link

Purpose:

```text
"This is not an auto-coding bot. It turns vague work into a reviewable handoff packet."
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
