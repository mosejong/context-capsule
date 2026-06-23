# Context Capsule

Context Capsule turns a vague request like "fix this" into a local, reviewable work packet for AI coding tools, teammates, and your future self.

It scans a local repository, retrieves task-relevant context, flags risky change areas, estimates token reduction, writes target-specific handoff files, and can preview a GitHub Issue payload before anything is created.

```text
local repo + task request
-> relevant context retrieval
-> risk and approval checklist
-> AI / teammate / self handoff packet
-> saved outputs
-> GitHub Issue dry-run
```

## Why This Exists

AI coding tools often fail because the handoff is weak:

- The model sees too much unrelated repository context.
- Important files are missed.
- Risky areas such as auth, env, DB schema, or deployment are touched too casually.
- The user has to repeat project context every time.
- Work is started before a human can approve scope and risk.

Context Capsule is not an auto-coding tool. It is a human-in-the-loop handoff system that makes the work request narrower, safer, and easier to verify before code changes begin.

Current retrieval is a local keyword/path-aware baseline. It now forces explicitly mentioned files into the top context and deduplicates repeated file chunks; embedding-based hybrid retrieval is still a roadmap item.

## Local App Quick Start

Context Capsule can run as a local Windows program.

```text
Download context-capsule-v0.1.0.zip -> extract -> double-click run_context_capsule.bat
```

The launcher creates `.venv`, installs runtime dependencies, and starts the local dashboard:

```text
http://localhost:8501
```

CLI wrapper:

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "Create a login API fix handoff packet" --target all --save --json
.\context_capsule_cli.bat create-issue outputs\YYYYMMDD_HHMMSS_slug --repo mosejong/context-capsule --json
.\context_capsule_cli.bat scrum-notes --text "Coach: Reduce MVP scope. Team: Build release notes." --json
.\context_capsule_cli.bat kickoff --topic "Scrum-to-execution planning tool" --notes "Build Scrum Notes Mode first. Discord API later." --deadline "2 weeks" --json
```

See [Local App](./docs/local_app.md) for installation, CLI usage, and safety details.

## v0.1.0 Release ZIP

Build the GitHub Release asset:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_release.ps1 -Version 0.1.0
```

Output:

```text
dist/context-capsule-v0.1.0.zip
```

The release ZIP includes launcher scripts, docs, tests, and source code. It excludes `.venv`, `outputs`, `dist`, caches, and local credentials.

Release docs:

- [Release Packaging](./docs/release_packaging.md)
- [GitHub Release Publish Checklist](./docs/release_publish_checklist.md)
- [v0.1.0 Release Notes](./docs/releases/v0.1.0.md)
- [Demo Capture Flow](./docs/demo_capture_flow.md)

## 30-Second Demo

Run the fixed demo scenario:

```powershell
.\.venv\Scripts\python.exe scripts\demo_scenario.py --json
```

What it demonstrates:

```text
login API error request
-> capsule generation
-> saved output packet
-> GitHub Issue dry-run JSON
-> no GitHub write unless --apply is used
```

The demo writes a local packet under `outputs/demo/` and prints the dry-run issue payload.

## CLI Workflow

Generate a saved packet:

```powershell
.\.venv\Scripts\python.exe -m app.cli generate `
  --repo-path . `
  --task "Create a login API fix handoff packet" `
  --target all `
  --save `
  --json
```

Preview the GitHub Issue payload:

```powershell
.\.venv\Scripts\python.exe -m app.cli create-issue outputs\YYYYMMDD_HHMMSS_slug --repo mosejong/context-capsule --json
```

Create the issue only after checking the dry-run payload:

```powershell
.\.venv\Scripts\python.exe -m app.cli create-issue outputs\YYYYMMDD_HHMMSS_slug --repo mosejong/context-capsule --apply
```

Safety defaults:

- `create-issue` is dry-run by default.
- `--apply` is required for a GitHub write.
- `GITHUB_TOKEN` or `GH_TOKEN` is read from the shell environment only.
- Tokens are never written to generated packet files.
- Use `--skip-labels` if the target repository does not have matching labels.

## Generated Output Packet

Saved packets are written under:

```text
outputs/YYYYMMDD_HHMMSS_slug/
```

Generated files:

- `OVERVIEW.md`
- `AI_HANDOFF_PROMPT.md`
- `TEAMMATE_BRIEF.md`
- `JUNIOR_GUIDE.md`
- `SELF_HANDOFF.md`
- `RISK_CHECKLIST.md`
- `GITHUB_ISSUE.md`
- `DECISION_RECORD.md`
- `CONTEXT_CAPSULE.md`
- `metadata.json`

`outputs/` is ignored by git.

## Core Features

| Feature | Status | Purpose |
| --- | --- | --- |
| Repo scanner | MVP | Reads local repository files. |
| Task-aware retrieval | MVP | Selects context related to the user request. |
| Retrieval quality hotfix | MVP | Forces mentioned files into top context and deduplicates repeated file chunks. |
| Risk analyzer | MVP | Separates mention risk from change risk. |
| Token budget | MVP | Estimates raw context vs capsule token reduction. |
| Target handoff sections | MVP | Builds AI, teammate, junior, and future-self briefs. |
| Saved packet writer | MVP | Writes reusable Markdown and JSON artifacts. |
| GitHub Issue adapter | MVP | Supports dry-run and explicit `--apply`. |
| CLI generate | MVP | Runs the full packet flow without Streamlit. |
| Windows launcher | MVP | Lets users run the local dashboard from a batch file. |
| Scrum Notes Mode | v0.2 | Turns scrum text into decisions, blockers, next actions, and issue drafts. |
| Project Kickoff Mode | v0.2 | Turns project topics and idea notes into MVP scope and submission checklist. |

## Architecture

```text
app/services/capsule_service.py
  -> Streamlit dashboard
  -> CLI generate
  -> future Discord adapter

outputs packet
  -> CLI create-issue
  -> future GitHub/Discord workflow

meeting text
  -> Scrum Notes Mode
  -> Project Kickoff Mode
  -> issue drafts and team-lead notes
```

The core generation flow is separated from the UI, so Streamlit, CLI, and future adapters reuse the same service.

## Token And Performance Metrics

Current token numbers are local estimates, not provider billing records.

Current provider boundary:

- `ApproxLocalTokenUsageProvider`: current local estimate, `approx_local_v1`
- `ExternalTokenAnalyzerProvider`: placeholder for an external Token-analyzer adapter
- future provider usage: actual Claude/OpenAI/Codex usage when measured from provider responses

Performance report:

- [Performance Comparison](./docs/reports/performance_comparison.md)
- [Performance SVG](./docs/assets/performance_comparison.svg)

Tracked metrics include:

- raw context tokens vs capsule tokens
- estimated token reduction
- relevant file hit rate
- unrelated retrieved file count
- success proxy
- scope escape proxy
- auto-start gate result

## Validation

Fast check:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Scenario validation:

```powershell
.\.venv\Scripts\python.exe scripts\validate_mvp.py --repeat 10
```

Performance report:

```powershell
.\.venv\Scripts\python.exe scripts\generate_performance_report.py
```

Current documented baseline:

```text
49 passed
5 MVP scenarios x 10 runs
```

More detail: [Validation](./docs/validation.md)

## Local-First Security Model

- MVP features do not require external AI APIs.
- Repository context stays local unless the user explicitly sends it elsewhere.
- GitHub writes require explicit `--apply`.
- Secret/env/credential files are excluded or treated as high risk by the scanner and risk analyzer.
- Closed or restricted environments can still use No-AI Mode for scan, retrieval, risk analysis, and Markdown packet generation.

## Roadmap

- [x] Local repository scanner
- [x] Task-aware retrieval
- [x] Mention risk / change risk split
- [x] Token budget estimate
- [x] AI / teammate / junior / future-self handoff sections
- [x] Saved output packet
- [x] CLI generate
- [x] GitHub Issue dry-run/apply adapter
- [x] Windows local app launcher
- [x] GitHub Release ZIP packaging
- [x] Fixed login error demo scenario
- [x] Performance comparison report v2
- [x] Text-based Scrum Notes Mode
- [x] Text-based Project Kickoff Mode
- [x] Retrieval quality hotfix for mentioned files and docs/code task intent
- [ ] Discord input adapter
- [ ] External Token-analyzer adapter
- [ ] Chroma / hybrid RAG retriever
- [ ] Local LLM provider adapter
- [ ] PyInstaller executable or Windows installer

## Docs

- [Project Plan](./PROJECT_PLAN.md)
- [Prototype Progress](./PROTOTYPE_PROGRESS.md)
- [Architecture](./docs/architecture.md)
- [Local App](./docs/local_app.md)
- [Release Packaging](./docs/release_packaging.md)
- [GitHub Release Publish Checklist](./docs/release_publish_checklist.md)
- [Demo Capture Flow](./docs/demo_capture_flow.md)
- [v0.1.0 Release Notes](./docs/releases/v0.1.0.md)
- [v0.2 Scrum and Kickoff Modes](./docs/v0.2_scrum_kickoff_modes.md)
- [Meeting-to-Execution Pipeline](./docs/meeting_to_execution_pipeline.md)
- [Future Direction](./docs/future_direction.md)
- [Validation](./docs/validation.md)
- [Performance Comparison](./docs/reports/performance_comparison.md)
- [LLM Tech Scan](./docs/research/llm_tech_scan_2026-06-22.md)
- [Paid API Impact Scan](./docs/research/paid_api_impact_scan_2026-06-22.md)
- [Rainbow Bridge sample capsule](./examples/rainbow_bridge_capsule.md)

## Positioning

Short version:

> Turn "fix this" into a reviewable work card.

Portfolio version:

> Context Capsule is a local-first handoff system that structures task scope, relevant files, risks, acceptance criteria, and verification steps before AI coding tools or teammates start work.
