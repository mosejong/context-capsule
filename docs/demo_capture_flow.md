# Demo Capture Flow

Use this flow for portfolio screenshots, presentation slides, or a short demo video.

## Capture 1: README First Screen

Show:

- One-line product explanation
- Local app quick start
- 30-second demo command
- CLI generate -> create-issue dry-run flow

Purpose:

```text
"This is not an auto-coding bot. It turns vague work into a reviewable handoff packet."
```

## Capture 2: Local Dashboard Start

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

## Capture 3: CLI Generate

Command:

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "Create a login API fix handoff packet" --target all --save --json
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

## Capture 4: Saved Output Packet

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

## Capture 5: GitHub Issue Dry-Run

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

## Capture 6: Performance Report

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
Context Capsule scans the repo locally, retrieves only task-relevant context, flags risk, and generates handoff packets for AI tools, teammates, or future me.
The CLI can save the packet and preview a GitHub Issue as a dry-run.
High-risk work is blocked until a human approves the scope.
```
