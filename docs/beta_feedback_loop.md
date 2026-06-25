# Beta Feedback Loop

Beta Feedback Loop is a v0.2.2 feature for turning tester comments into the next patch plan.

It is not a user rating system. It is not teammate evaluation. It is a structured way to preserve what testers tried, what they expected, what Context Capsule returned, and what confused them.

## Problem

KDT testers give useful feedback in chat:

```text
어디 입력해야 하는지 헷갈려요.
결과 탭이 너무 많아요.
토큰이 왜 줄어드는지 설명이 필요해요.
기대한 파일이 안 나왔어요.
```

If this stays only in Discord, the next patch depends on memory.

Beta Feedback Loop saves each feedback item and then reviews the whole folder to find repeated issues.

## Saved Feedback

Dashboard feedback and CLI feedback-save both write the same files:

```text
outputs/feedback/YYYYMMDD_HHMMSS_slug/
├── FEEDBACK.md
└── feedback.json
```

The saved record includes:

- version
- mode
- project name
- repo path/type
- request text
- expected files
- actual top files
- risk result
- token evidence
- confusing UI/UX
- reuse willingness
- notes

## Review Output

Feedback Review reads saved `feedback.json` files and creates:

- common issues
- missed file cases
- UI confusion points
- token explanation questions
- risk explanation questions
- next patch priorities
- regression test candidates

This turns tester reactions into implementation work.

## Dashboard Usage

1. Generate a Work Handoff, Scrum Notes, Kickoff, or Health Check result.
2. Scroll to `이 결과가 이상했나요?`.
3. Enter expected files, confusing part, reuse willingness, and notes.
4. Click `피드백 저장`.
5. Open `피드백 리뷰`.
6. Click `피드백 리뷰 생성`.

## CLI Usage

Save one feedback item:

```powershell
.\context_capsule_cli.bat feedback-save `
  --mode work `
  --project-name "shop-app" `
  --request "로그인이 모바일에서만 안돼" `
  --expected-file backend/auth/login.py `
  --actual-file README.md `
  --confusing-part "결과 탭에서 어디를 봐야 하는지 헷갈렸어요." `
  --output-dir outputs\feedback `
  --json
```

Review saved feedback:

```powershell
.\context_capsule_cli.bat feedback-review `
  --feedback-root outputs\feedback `
  --save `
  --json
```

## Safety Boundaries

- Feedback text is untrusted input.
- Secret-looking values are redacted before saving.
- Prompt-injection-like lines are redacted before saving.
- Feedback Review does not create branches, issues, assignments, or code changes.
- A human decides what to fix next.

## Patch Planning Rule

Use Feedback Review as a triage helper:

```text
Repeated file mismatch -> retrieval/ranking test
Repeated UI confusion -> wording/layout patch
Repeated token question -> Token Evidence explanation patch
Repeated risk question -> Risk & Approval explanation patch
```

