# Release Packaging

Context Capsule v0.2.10 is distributed as a GitHub Release ZIP.

The ZIP is a source-style local app package. It contains the FastAPI Korean local UI, CLI, launcher scripts, docs, tests, release notes, Beta Feedback Loop documentation, Workflow Graph Trace documentation, and tester UX polish docs. It does not contain `.venv`, generated `outputs`, cache folders, build artifacts, or local credentials.

## Build

From the repository root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_release.ps1 -Version 0.2.10
```

Output:

```text
dist/context-capsule-v0.2.10.zip
```

Dry-run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_release.ps1 -Version 0.2.10 -DryRun
```

The build script validates required release files, checks that generated/local folders are not tracked, creates the ZIP with `git archive`, and verifies required entries inside the archive.

## Publish

Suggested GitHub Release settings:

```text
Tag: v0.2.10
Title: Context Capsule v0.2.10
Asset: dist/context-capsule-v0.2.10.zip
Release notes: docs/releases/v0.2.10.md
```

Detailed publishing checklist:

- [GitHub Release Publish Checklist](./release_publish_checklist.md)

## User Install Flow

```text
Download context-capsule-v0.2.10.zip
Extract
Double-click run_context_capsule.bat
Open http://localhost:8501
```

First run creates `.venv` and installs `requirements.txt`.

## Release Checklist

- [ ] `pytest` passes.
- [ ] `scripts/validate_mvp.py --repeat 10` passes.
- [ ] `scripts/demo_scenario.py --json` prints a dry-run issue payload.
- [ ] `scripts/run_dashboard.ps1 -DryRun` prints the FastAPI/uvicorn command.
- [ ] `scripts/build_release.ps1 -Version 0.2.10` creates the ZIP.
- [ ] ZIP contains launcher scripts and docs.
- [ ] ZIP excludes `.venv`, `outputs`, `dist`, caches, and credentials.
- [ ] Release notes match the shipped version.

## Known Packaging Limits

- v0.2.10 is not a single executable.
- Python 3.11 or newer is required on the user's machine.
- Internet access is required for the first dependency install.
- GitHub Issue creation requires `GITHUB_TOKEN` or `GH_TOKEN` only when `--apply` is used.


