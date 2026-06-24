# KDT Beta Quickstart

This guide is for KDT learners who want to try Context Capsule on a local project and send useful feedback.

## What You Are Testing

Context Capsule turns rough requests into reviewable work packets.

Examples:

```text
리드미 손보자
로컬 실행 안돼
깃헙 이슈 생성 안됨
토큰 계산 뻥튀기 같은데?
auth는 건드리지 말고 문서만 바꾸자
이거 왜 안됨?
```

The tool should:

- understand the rough request
- find likely files
- separate protected areas such as auth, DB, deploy, and secrets
- stop and ask one clarification question when the request is too vague
- generate AI, teammate, future-me, risk, and GitHub Issue packets

## 1. Download And Open

Download:

```text
context-capsule-v0.1.4.zip
```

Extract the ZIP, then double-click:

```text
run_context_capsule.bat
```

The first run creates `.venv`, installs dependencies, and opens:

```text
http://localhost:8501
```

If the dashboard does not open, run the doctor command.

## 2. Run Doctor

```powershell
.\context_capsule_cli.bat doctor --repo-path .
```

Expected:

```text
Context Capsule doctor
```

Check whether the result says `PASS`, `WARN`, or `FAIL`.

## 3. Build The Local Index

```powershell
.\context_capsule_cli.bat index --repo-path . --json
```

This creates a local retrieval index under:

```text
.context-capsule-index/
```

The index is local and ignored by git.

This step is optional. Context Capsule still works without an index through keyword/path retrieval. Build the index when you want to test `--retriever indexed` or reuse the same repository across several requests.

## 4. Generate A Packet

Try this first:

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "리드미 손보자" --retriever indexed --target all --save --json
```

Then try one request from your own project:

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "로컬 실행 안돼" --retriever indexed --target all --save --json
```

The generated folder looks like:

```text
outputs/YYYYMMDD_HHMMSS_slug/
├── OVERVIEW.md
├── AI_HANDOFF_PROMPT.md
├── TEAMMATE_BRIEF.md
├── JUNIOR_GUIDE.md
├── SELF_HANDOFF.md
├── RISK_CHECKLIST.md
├── GITHUB_ISSUE.md
└── metadata.json
```

## 5. Preview A GitHub Issue

Dry-run only:

```powershell
.\context_capsule_cli.bat create-issue outputs\YYYYMMDD_HHMMSS_slug --repo owner/name --json
```

Do not use `--apply` during beta testing unless you intentionally want to create a real GitHub Issue.

## 6. Test Scrum Notes Mode

Use the dashboard tab or CLI with anonymized meeting notes.

Good beta test text:

```text
배경이미지가 생성됐다고 나오는데 저장이 안 되고 게임 화면에는 검은색으로 나와요.
로그에도 저장 위치가 안 찍혀요.
확인해보니 그래픽카드 사양 때문에 3분 timeout을 넘겨서 생성이 실패한 것 같습니다.
일단 timeout 시간을 늘려서 다시 테스트해볼게요.
```

Expected:

- blocker summary
- next actions
- issue drafts
- open questions
- safety notes

## 7. Send Feedback

Generate a feedback template:

```powershell
.\context_capsule_cli.bat feedback-template --project-name "my-project" --tester-name "nickname" --save --json
```

Then fill:

```text
outputs/YYYYMMDD_HHMMSS_kdt-feedback-template/KDT_FEEDBACK_TEMPLATE.md
```

Most useful feedback:

- the exact request you typed
- expected file
- actual top retrieved files
- whether protected areas were respected
- whether the tool should have asked a clarification question
- any install/run error

Do not paste secrets, `.env`, private API tokens, or proprietary code unless you intentionally want to share them.

## Current Validation Baseline

As of v0.1.4:

```text
User-speech QA: 73 PASS / 0 WARN / 0 FAIL
Clarification accuracy: 8/8
Protected false positives: 0
```

These are local validation results, not a guarantee for every project. Your failed cases are exactly what will make the next version better.
