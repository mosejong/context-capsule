# Project Health Check

Project Health Check is a v0.2.1+ collaboration mode.

It reads project status text, scrum notes, or kickoff notes and estimates whether the project is ready enough to continue as an MVP or prototype.

This mode does not call an external LLM. It uses rule-based signals so it can run in local-first and closed-network settings.

## What It Answers

- MVP readiness percentage
- Prototype readiness percentage
- stability label
- missing meeting items
- next meeting questions
- ownership check: is this likely my part, another person's part, or unclear?
- evidence behind each score

## What It Does Not Do

- It does not evaluate teammates.
- It does not assign owners automatically.
- It does not create branches.
- It does not create GitHub Issues automatically.
- It does not decide final priority.

The output is a planning aid for the next meeting.

## MVP Readiness Signals

| Signal | Weight |
| --- | ---: |
| Decisions exist | 20 |
| Next actions exist | 20 |
| Acceptance criteria exist | 15 |
| Tests or validation exist | 15 |
| Owner/scope hints exist | 10 |
| Risks or blockers exist | 10 |
| Deadline or schedule exists | 10 |

## Prototype Readiness Signals

| Signal | Weight |
| --- | ---: |
| Runnable demo or visible UI exists | 25 |
| Core flow or MVP scope exists | 20 |
| Tester feedback exists | 15 |
| Iteration/release history exists | 15 |
| Docs/install guide exists | 10 |
| Validation command or test result exists | 10 |
| Remaining risk is written down | 5 |

## Ownership Check

The user can enter a self-declared scope such as:

```text
README, local run guide, FastAPI UI
```

Context Capsule compares that scope with the meeting text and returns:

- `likely_my_part`
- `possibly_other_part`
- `needs_confirmation`

This is only a hint. The team must still confirm ownership through Issue/PR or meeting discussion.

## CLI

```powershell
.\context_capsule_cli.bat health `
  --text-file .\tests\fixtures\project_health_status_ko.txt `
  --project-context "Context Capsule v0.2" `
  --deadline "주말 재테스트 전" `
  --my-scope "README, UI" `
  --json
```

## Dashboard

Open the local app:

```text
http://localhost:8501
```

Then select:

```text
준비도 점검
```

The result tabs show:

- 점수판
- 부족한 회의
- 내 파트 확인
- 근거
- Markdown
