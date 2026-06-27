# GitHub Release Publish Checklist

Use this file when publishing `Context Capsule v0.2.8` on GitHub Releases.

## Release Settings

```text
Repository: mosejong/context-capsule
Tag: v0.2.8
Title: Context Capsule v0.2.8
Asset: dist/context-capsule-v0.2.8.zip
Release body: docs/releases/v0.2.8.md
```

## Before Upload

- [ ] Confirm `git status -sb` is clean.
- [ ] Confirm tag `v0.2.8` exists on GitHub.
- [ ] Confirm `dist/context-capsule-v0.2.8.zip` exists locally.
- [ ] Confirm ZIP was built with `scripts/build_release.ps1 -Version 0.2.8`.
- [ ] Confirm ZIP excludes `.venv`, `outputs`, `dist`, caches, and credentials.
- [ ] Copy the body from `docs/releases/v0.2.8.md`.

## Publish Steps

1. Open `https://github.com/mosejong/context-capsule/releases`.
2. Click `Draft a new release`.
3. Select tag `v0.2.8`.
4. Set release title to `Context Capsule v0.2.8`.
5. Paste `docs/releases/v0.2.8.md` into the release description.
6. Upload `dist/context-capsule-v0.2.8.zip`.
7. Check that the asset name is exactly `context-capsule-v0.2.8.zip`.
8. Publish release.

## After Publish

- [ ] Open the published release page.
- [ ] Download the ZIP once.
- [ ] Extract it into a temporary folder.
- [ ] Confirm `run_context_capsule.bat` exists.
- [ ] Confirm `README.md`, `START_HERE_KO.md`, `docs/token_evidence.md`, `docs/workflow_graph.md`, `docs/work_handoff_ownership.md`, `docs/releases/v0.2.8.md`, and `docs/local_app.md` exist.
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
Context Capsule helps junior developers prepare safer AI coding requests.
Instead of telling an AI "fix this", it first organizes what files to look at, what not to touch, what done means, and what instruction to copy into Claude, Codex, or ChatGPT.
v0.2.8 ships as a Windows ZIP with beginner-friendly Korean onboarding, target-positioning docs for interviewers/team leads, FastAPI local UI, CLI, GitHub Issue dry-run, Request Understanding, indexed retrieval, context redaction, Token Evidence guidance, Scrum/Kickoff/Health modes, Work Handoff Ownership Check, Beta Feedback Loop, Workflow Graph Trace, Python 3.11+ support, and validation reports.
```

## One-Line Positioning

```text
Turn "fix this" into a reviewable work card before AI or teammates start changing code.
```

