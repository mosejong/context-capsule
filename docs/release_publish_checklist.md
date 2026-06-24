# GitHub Release Publish Checklist

Use this file when publishing `Context Capsule v0.1.6` on GitHub Releases.

## Release Settings

```text
Repository: mosejong/context-capsule
Tag: v0.1.6
Title: Context Capsule v0.1.6
Asset: dist/context-capsule-v0.1.6.zip
Release body: docs/releases/v0.1.6.md
```

## Before Upload

- [ ] Confirm `git status -sb` is clean.
- [ ] Confirm tag `v0.1.6` exists on GitHub.
- [ ] Confirm `dist/context-capsule-v0.1.6.zip` exists locally.
- [ ] Confirm ZIP was built with `scripts/build_release.ps1 -Version 0.1.6`.
- [ ] Confirm ZIP excludes `.venv`, `outputs`, `dist`, caches, and credentials.
- [ ] Copy the body from `docs/releases/v0.1.6.md`.

## Publish Steps

1. Open `https://github.com/mosejong/context-capsule/releases`.
2. Click `Draft a new release`.
3. Select tag `v0.1.6`.
4. Set release title to `Context Capsule v0.1.6`.
5. Paste `docs/releases/v0.1.6.md` into the release description.
6. Upload `dist/context-capsule-v0.1.6.zip`.
7. Check that the asset name is exactly `context-capsule-v0.1.6.zip`.
8. Publish release.

## After Publish

- [ ] Open the published release page.
- [ ] Download the ZIP once.
- [ ] Extract it into a temporary folder.
- [ ] Confirm `run_context_capsule.bat` exists.
- [ ] Confirm `README.md`, `docs/releases/v0.1.6.md`, and `docs/local_app.md` exist.
- [ ] Run `run_context_capsule.bat` or `scripts\run_dashboard.ps1`.
- [ ] Confirm `http://localhost:8501` opens.

## Presentation Demo Order

Keep the live demo short:

1. Release page: show the ZIP asset.
2. Extracted folder: show `run_context_capsule.bat`.
3. Dashboard: show local app at `localhost:8501`.
4. CLI generate: show `saved_output_dir`, `token_budget`, and `risk_level`.
5. Saved packet: show `AI_HANDOFF_PROMPT.md`, `TEAMMATE_BRIEF.md`, and `GITHUB_ISSUE.md`.
6. GitHub Issue dry-run: show `"mode": "dry-run"` and auto-start gate.
7. Performance report: show estimated token reduction and relevant file hit rate.

## 30-Second Release Pitch

```text
Context Capsule is a local-first handoff tool for AI-assisted development.
Instead of telling an AI "fix this", it scans the repo locally, finds task-relevant context, flags risky files, and generates reviewable packets for AI tools, teammates, or future me.
v0.1.6 ships as a Windows ZIP with a dashboard, CLI, GitHub Issue dry-run, Request Understanding, indexed retrieval, Korean-to-English domain retrieval hints, context redaction, first-tester dashboard guidance, direct KDT beta links, Python 3.11+ support, and validation reports.
```

## One-Line Positioning

```text
Turn "fix this" into a reviewable work card before AI or teammates start changing code.
```
