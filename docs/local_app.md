# Local App

Context Capsule is designed as a local-first program.

Users download the repository, run it on their own machine, and keep repository context and generated packets local by default.

## Windows Quick Start

Requirements:

- Windows 10/11
- Python 3.11 or newer
- Internet access only for first dependency install

Download:

```text
GitHub Releases -> context-capsule-v0.2.7.zip
```

Run:

```text
1. Extract the ZIP.
2. Double-click run_context_capsule.bat.
3. Open http://localhost:8501 if the browser does not open automatically.
```

The launcher creates `.venv`, installs `requirements.txt`, and starts the local FastAPI Korean web UI.

## Dashboard-First Test

For first-time testers, the terminal is optional.

```text
1. Open http://localhost:8501
2. Use `AI에게 작업 맡기기`
3. Keep 프로젝트 폴더 경로 as .
4. Type 리드미 손보자
5. Click 작업 정리본 만들기
6. Watch the result area for the generation status
7. Check 요약, 먼저 볼 파일, AI 지시문, and 위험/승인
```

Run CLI commands only when you want to diagnose setup, build an index manually, or create reproducible JSON output.

## Release ZIP

Build the release ZIP from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_release.ps1 -Version 0.2.7
```

Output:

```text
dist/context-capsule-v0.2.7.zip
```

The release package includes source code, launcher scripts, docs, tests, and release notes.
It excludes `.venv`, generated `outputs`, `dist`, caches, build artifacts, and credentials.

## PowerShell Install

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\install_windows.ps1
```

Start dashboard:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_dashboard.ps1
```

Use another port:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_dashboard.ps1 -Port 8502
```

## CLI Wrapper

Check local install:

```powershell
.\context_capsule_cli.bat doctor --repo-path .
```

Build a local retrieval index:

```powershell
.\context_capsule_cli.bat index --repo-path . --json
```

Generate a saved work summary:

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "리드미 손보자" --retriever indexed --target all --save --json
```

Protected-area example:

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "auth는 건드리지 말고 문서만 바꾸자" --retriever indexed --target all --save --json
```

Project Health Check:

```powershell
.\context_capsule_cli.bat health --text "v0.2 UI done. pytest passed. 주말 재테스트 전 README 정리." --my-scope "README, UI" --json
```

Preview GitHub Issue payload:

```powershell
.\context_capsule_cli.bat create-issue outputs\YYYYMMDD_HHMMSS_slug --repo mosejong/context-capsule --json
```

Create a real issue only after checking the dry-run payload:

```powershell
.\context_capsule_cli.bat create-issue outputs\YYYYMMDD_HHMMSS_slug --repo mosejong/context-capsule --apply
```

`GITHUB_TOKEN` or `GH_TOKEN` must be set in the shell environment for `--apply`.
The token is never written to generated packet files.

## Local Files

Generated packets are written under:

```text
outputs/YYYYMMDD_HHMMSS_slug/
```

Generated files include:

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

## Safety Model

- The app reads local repository files.
- External AI APIs are not required for MVP features.
- GitHub writes require explicit `--apply`.
- GitHub token is read from environment variables only.
- Secret/env/credential files are excluded or treated as high risk by the scanner/risk analyzer.

## Future Packaging

The current local program is a Python/FastAPI release ZIP.

v0.2.2 added Beta Feedback Loop. After a tester generates a result, the dashboard can save feedback under `outputs/feedback`, and Feedback Review can summarize repeated issues into next patch priorities.

v0.2.3 adds Workflow Graph Trace. The Work Handoff result includes a `작업 흐름` tab that shows scan, request understanding, retrieval, risk analysis, packet generation, and human review gate status.

v0.2.5 polished the first-tester flow. The dashboard explains which result tab to read first, uses easier labels such as `빠른 검색`, `균형 검색`, and `작업 정리본`, respects explicit file scope such as `.md files only`, and shows Workflow Graph Trace with Korean stage labels.

v0.2.6 clarifies the product target. The app is primarily for junior developers preparing AI coding requests, while the first screen and docs are written so interviewers, team leads, and AI beginners can understand the workflow without technical vocabulary first.

v0.2.7 adds Work Handoff Ownership Check. The Work Handoff form now has `내 담당 영역`, and the result shows `내 파트 확인` so users can see whether the request appears to match their own scope, another person's scope, or needs confirmation. This is only a confirmation aid; it does not evaluate teammates or assign work automatically.

Possible next packaging steps:

- PyInstaller executable
- Windows installer
- Local FastAPI + desktop shell

The current launcher is kept simple so the code remains inspectable and easy to run in closed or restricted environments.

