from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FeedbackTemplate:
    project_name: str
    tester_name: str
    commands: list[str]
    markdown: str

    def to_dict(self) -> dict:
        return asdict(self)


DEFAULT_COMMANDS = [
    r".\context_capsule_cli.bat doctor --repo-path .",
    r".\.venv\Scripts\python.exe scripts\demo_user_speech.py",
    r".\context_capsule_cli.bat index --repo-path . --json",
    r'.\context_capsule_cli.bat generate --repo-path . --task "리드미 손보자" --retriever indexed --target all --save --json',
    r".\context_capsule_cli.bat create-issue outputs\YYYYMMDD_HHMMSS_slug --repo owner/name --json",
]


def build_feedback_template(project_name: str = "", tester_name: str = "") -> FeedbackTemplate:
    clean_project = project_name.strip() or "(project/repository name)"
    clean_tester = tester_name.strip() or "(tester name)"
    markdown = f"""# Context Capsule KDT Beta Feedback

## Tester

- Tester: {clean_tester}
- Project: {clean_project}
- Date:
- OS:
- Python version:
- Context Capsule version/release:

## Safety Notice

Do not paste secrets, `.env` values, API tokens, passwords, private keys, or private project code without permission.

## Setup Checklist

| Step | Command | Result | Notes |
| --- | --- | --- | --- |
| Doctor | `{DEFAULT_COMMANDS[0]}` | PASS / WARN / FAIL | |
| User-speech demo | `{DEFAULT_COMMANDS[1]}` | PASS / WARN / FAIL | |
| Build index | `{DEFAULT_COMMANDS[2]}` | PASS / WARN / FAIL | |
| Generate packet | `{DEFAULT_COMMANDS[3]}` | PASS / WARN / FAIL | |
| Issue dry-run | `{DEFAULT_COMMANDS[4]}` | PASS / WARN / FAIL | |

## Requests Tested

| Request Text | Expected Target File(s) | Actual Top File(s) | Verdict | Notes |
| --- | --- | --- | --- | --- |
| 리드미 손보자 | README.md | | PASS / WARN / FAIL | |
| 로컬 실행 안돼 | launcher/docs/scripts | | PASS / WARN / FAIL | |
| 깃헙 이슈 생성 안됨 | CLI/GitHub adapter | | PASS / WARN / FAIL | |
| auth는 건드리지 말고 문서만 바꾸자 | docs target, auth protected | | PASS / WARN / FAIL | |
| 이거 왜그래? | clarification-only | | PASS / WARN / FAIL | |
| (your own request) | | | PASS / WARN / FAIL | |

## Output Review

| Output File | Useful? | Notes |
| --- | --- | --- |
| `OVERVIEW.md` | Yes / No / Not checked | |
| `AI_HANDOFF_PROMPT.md` | Yes / No / Not checked | |
| `TEAMMATE_BRIEF.md` | Yes / No / Not checked | |
| `JUNIOR_GUIDE.md` | Yes / No / Not checked | |
| `SELF_HANDOFF.md` | Yes / No / Not checked | |
| `RISK_CHECKLIST.md` | Yes / No / Not checked | |
| `GITHUB_ISSUE.md` | Yes / No / Not checked | |

## Protected-Area Check

Did Context Capsule avoid protected areas such as auth, DB, env, secret, deploy, or private files?

```text
Answer:
Example:
```

## Result Reading Order

Was it clear which result tab to read first?

```text
Answer:
Example: I understood that I should check related files and risk first.
```

## Workflow Trace Check

Was the `작업 흐름` tab understandable?

```text
Answer:
Example: I understood why the request was blocked / I did not understand what "current step" meant.
```

## Confusing Moments

Where did the install, command, UI, or output become confusing?

```text
Answer:
```

## Missing User Phrases

Write any phrasing Context Capsule failed to understand.

```text
1.
2.
3.
```

## Bugs / Errors

Paste error messages only after removing secrets.

```text
Error:
What you expected:
What happened:
```

## Overall Feedback

```text
Most useful part:
Least useful part:
Would you use this before asking ChatGPT/Claude/Codex to work on your project? Why?
What should be improved first?
```
"""
    return FeedbackTemplate(
        project_name=clean_project,
        tester_name=clean_tester,
        commands=list(DEFAULT_COMMANDS),
        markdown=markdown,
    )
