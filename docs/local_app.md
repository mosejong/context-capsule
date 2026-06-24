# Local App

Context Capsule is designed as a local-first program.

Users download the repository, run it on their own machine, and keep repository context and generated packets local by default.

## Windows Quick Start

Requirements:

- Windows 10/11
- Python 3.13
- Internet access only for first dependency install

Download:

```text
GitHub Releases -> context-capsule-v0.1.2.zip
```

Run:

```text
1. Extract the ZIP.
2. Double-click run_context_capsule.bat.
3. Open http://localhost:8501 if the browser does not open automatically.
```

The launcher creates `.venv`, installs `requirements.txt`, and starts the local Streamlit dashboard.

## Release ZIP

Build the release ZIP from the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_release.ps1 -Version 0.1.2
```

Output:

```text
dist/context-capsule-v0.1.2.zip
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

Generate a saved packet:

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "리드미 손보자" --retriever indexed --target all --save --json
```

Protected-area example:

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "auth는 건드리지 말고 문서만 바꾸자" --retriever indexed --target all --save --json
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

The current local program is a Python/Streamlit release ZIP.

Possible next packaging steps:

- PyInstaller executable
- Windows installer
- Local FastAPI + desktop shell

The current launcher is kept simple so the code remains inspectable and easy to run in closed or restricted environments.
