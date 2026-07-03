# GitHub Release Publish Checklist

Use this file when publishing `Context Capsule v0.3.1` on GitHub Releases.

## Release Settings

```text
Repository: mosejong/context-capsule
Tag: v0.3.1
Title: Context Capsule v0.3.1
Asset: dist/context-capsule-v0.3.1.zip
Release body: docs/releases/v0.3.1.md
```

## Before Upload

- [ ] Confirm `git status -sb` is clean.
- [ ] Confirm tag `v0.3.1` exists on GitHub.
- [ ] Confirm `dist/context-capsule-v0.3.1.zip` exists locally.
- [ ] Confirm ZIP was built with `scripts/build_release.ps1 -Version 0.3.1`.
- [ ] Confirm ZIP excludes `.venv`, `outputs`, `dist`, caches, and credentials.
- [ ] Copy the body from `docs/releases/v0.3.1.md`.

## Publish Steps

1. Open `https://github.com/mosejong/context-capsule/releases`.
2. Click `Draft a new release`.
3. Select tag `v0.3.1`.
4. Set release title to `Context Capsule v0.3.1`.
5. Paste `docs/releases/v0.3.1.md` into the release description.
6. Upload `dist/context-capsule-v0.3.1.zip`.
7. Check that the asset name is exactly `context-capsule-v0.3.1.zip`.
8. Publish release.

## After Publish

- [ ] Open the published release page.
- [ ] Download the ZIP once.
- [ ] Extract it into a temporary folder.
- [ ] Confirm `run_context_capsule.bat` exists.
- [ ] Confirm `README.md`, `START_HERE_KO.md`, `docs/reference/token_evidence.md`, `docs/reference/workflow_graph.md`, `docs/reference/work_handoff_ownership.md`, `docs/reference/nvidia_nim_provider.md`, `docs/releases/v0.3.1.md`, and `docs/local_app.md` exist.
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
v0.3.1 ships as a Windows ZIP with beginner-friendly Korean onboarding, first-run install/dashboard logs under `outputs/logs`, Korean failure guidance, target-positioning docs for interviewers/team leads, FastAPI local UI, CLI, GitHub Issue dry-run, Request Understanding, indexed retrieval, optional local embedding benchmark support, optional NVIDIA NIM provider lab, context redaction, Token Evidence guidance, Scrum/Kickoff/Health modes, Work Handoff Ownership Check, Beta Feedback Loop, Workflow Graph Trace, external repo evaluation, Python 3.11+ support, validation reports, and the Result Trust Flow UI.
```

## One-Line Positioning

```text
Turn "fix this" into a reviewable work card before AI or teammates start changing code.
```
