# KDT Beta Test Plan

Context Capsule is currently a learning-first public beta.

The goal is not immediate commercialization. The goal is to make a usable local workflow tool, give it to KDT learners, collect real feedback, and improve reliability.

## Beta Positioning

```text
Public repository = portfolio + KDT tester beta + feedback evidence
Private repository = optional future product experiments
```

Current focus:

- build as much of the workflow as possible in public
- keep safety defaults visible
- let KDT learners try it on their own projects
- collect failure cases and confusing moments
- expand QA from real user phrasing

Not the current focus:

- payment
- licensing experiments
- closed-source Pro features
- autonomous coding
- teammate scoring or automatic assignment

## Tester Profile

Primary testers:

- KDT learners
- beginner developers
- teammates who use ChatGPT, Claude, Codex, or similar tools
- people who struggle to explain project context repeatedly

Useful tester projects:

- class team projects
- personal portfolio projects
- FastAPI/Streamlit/React projects
- projects with README, docs, and simple backend/frontend folders

## Test Flow

Ask testers to run this flow:

```powershell
.\context_capsule_cli.bat doctor --repo-path .
```

```powershell
.\.venv\Scripts\python.exe scripts\demo_user_speech.py
```

```powershell
.\context_capsule_cli.bat index --repo-path . --json
```

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "리드미 손보자" --retriever indexed --target all --save --json
```

```powershell
.\context_capsule_cli.bat create-issue outputs\YYYYMMDD_HHMMSS_slug --repo owner/name --json
```

Generate a feedback form:

```powershell
.\context_capsule_cli.bat feedback-template --project-name "my-project" --tester-name "nickname" --save --json
```

For their own projects, ask them to try requests like:

```text
리드미 손보자
로컬 실행 안돼
깃헙 이슈 생성 안됨
토큰 계산 뻥튀기 같은데?
auth는 건드리지 말고 문서만 바꾸자
이거 왜그래?
```

## Feedback Questions

Use `docs/feedback_template.md` or the generated `KDT_FEEDBACK_TEMPLATE.md` after testing.

Core questions:

1. Did `doctor` make the local setup status clear?
2. Did install/run fail anywhere?
3. What task request did you try first?
4. Did Context Capsule find the files you expected?
5. Did it retrieve irrelevant files?
6. Did it correctly avoid protected areas such as auth, DB, env, or secrets?
7. Was the generated `AI_HANDOFF_PROMPT.md` useful?
8. Was the `TEAMMATE_BRIEF.md` understandable for a beginner?
9. Did the GitHub Issue dry-run feel safe?
10. What wording did you use that the tool failed to understand?

## Success Metrics

For the KDT beta, success means:

- new users can run `doctor`
- new users can run the demo
- at least 3-5 testers try it on real projects
- at least 20 new user phrases are collected
- user-speech QA grows toward 50 cases
- confusing install steps are documented or fixed
- no token/secret is accidentally written to outputs

## What To Collect

Collect:

- task request text
- expected target file
- actual retrieved files
- whether protected areas were respected
- whether clarification should have happened
- tester comments
- install/run errors

Do not collect:

- secrets
- `.env`
- private API tokens
- proprietary project code unless the tester explicitly agrees

## Next Build Priorities

After the first KDT beta:

1. Expand user-speech QA to 50 cases.
2. Add retrieval evaluation metrics: hit@1, hit@3, irrelevant count.
3. Improve unclear install/run errors.
4. Add a feedback template file.
5. Improve Streamlit onboarding for first-time users.

## One-Line Rule

```text
Build in public, learn from KDT testers, delay commercialization.
```
