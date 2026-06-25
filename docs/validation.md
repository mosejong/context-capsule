# Validation

Context Capsule is validated as a local-first handoff generator, not as an autonomous coding agent.

The validation goal is:

```text
Given a repository and task request, retrieve relevant files, generate a useful handoff packet, flag risky work, and keep writes behind explicit approval.
```

## Fast Check

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Current baseline:

```text
101 passed
```

Covered areas:

- capsule generation
- request understanding for colloquial Korean task requests
- Korean requests against English codebase file names
- context redaction for secret-like values and prompt-injection-like lines
- risk analyzer
- token usage provider boundary
- saved output writer
- GitHub Issue adapter dry-run/apply payload
- CLI generate/create-issue
- CLI scrum-notes/kickoff
- text-based Scrum Notes and Project Kickoff analyzers
- mentioned-file mandatory retrieval
- docs/code task intent ranking
- intent-aware retrieval filtering for documentation-only and launcher troubleshooting requests
- duplicate file chunk deduplication
- optional hybrid retrieval with embedding fallback
- persistent indexed retrieval with stale/provider fallback
- indexed retrieval QA for real user-speech requests
- indexed fallback visibility through `retrieval_report`
- clarification-only gate for ambiguous requests
- token baseline uses retrieved file contents instead of whole-repo concat
- negated risk instruction handling
- fixed demo scenario
- local launcher files and dry-run scripts
- scanner exclusion of generated `outputs`

## Compile Check

```powershell
.\.venv\Scripts\python.exe -m compileall app tests scripts
```

Purpose:

- catch import errors
- catch syntax errors
- verify script modules compile

## Scenario Validation

```powershell
.\.venv\Scripts\python.exe scripts\validate_mvp.py --repeat 10
```

Current baseline:

```text
validated 5 scenarios x 10 run(s)
```

Scenarios:

1. README documentation brief.
2. Chat/error log to capsule.
3. High-risk auth task blocks auto-start.
4. Teammate brief.
5. Future-me handoff.

Checks:

- expected files are retrieved
- request understanding intent and protected hints are recorded
- HIGH/BLOCKED change risk blocks auto-start
- safe work can remain allowed
- generated issue body has branch and acceptance criteria
- token reduction is calculated
- scope escape proxy remains false

## User-Speech Retrieval QA

```powershell
.\.venv\Scripts\python.exe scripts\validate_user_speech.py --repo-path .
```

Generated file:

- `docs/reports/user_speech_retrieval_qa.md`

Current baseline:

```text
73 cases
PASS: 73
WARN: 0
FAIL: 0
hit@1: 54/61 target cases
hit@3: 61/61 target cases
protected false positives: 0
clarification accuracy: 8/8
```

Checks:

- colloquial Korean requests map to expected target files
- Korean requests can retrieve common English codebase paths through local domain-term expansion
- protected domains such as `auth` and `db` are not treated as work targets
- ambiguous requests use clarification-only mode
- indexed retrieval fallback is visible
- token baseline scope remains `retrieved_file_contents` or `clarification_only`
- retrieval metrics include hit@1, hit@3, irrelevant count, protected false positives, and clarification accuracy

Short presentation demo:

```powershell
.\.venv\Scripts\python.exe scripts\demo_user_speech.py
```

## Performance Report

```powershell
.\.venv\Scripts\python.exe scripts\generate_performance_report.py
```

Generated files:

- `docs/reports/performance_comparison.md`
- `docs/assets/performance_comparison.svg`

Tracked metrics:

- candidate file context tokens versus capsule tokens
- estimated token reduction
- relevant file hit rate
- unrelated retrieved file count
- success proxy
- scope escape proxy
- auto-start gate result

Current report baseline:

```text
Average estimated token reduction: 67.5%
Average relevant file hit rate: 100.0%
Success proxy pass rate: 5/5
Scope escape count: 0
```

These are local estimates, not provider billing records.

## Dashboard Smoke

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\run_dashboard.ps1 -NoInstall -Port 8501
```

Expected:

```text
http://localhost:8501 returns HTTP 200
```

## CLI Smoke

Doctor:

```powershell
.\context_capsule_cli.bat doctor --repo-path . --json
```

Expected:

- status is `PASS` or `WARN`
- Python version is reported
- required files are checked
- repo scan count is reported
- dry-run safety is reported

Feedback template:

```powershell
.\context_capsule_cli.bat feedback-template --project-name "my-project" --tester-name "nickname" --save --json
```

Expected:

- `KDT_FEEDBACK_TEMPLATE.md` is saved
- setup checklist is included
- request/result table is included
- secret-sharing warning is included

Generate:

```powershell
.\context_capsule_cli.bat generate --repo-path . --task "Create a login API fix handoff packet" --target all --save --json
```

Dry-run issue:

```powershell
.\context_capsule_cli.bat create-issue outputs\YYYYMMDD_HHMMSS_slug --repo mosejong/context-capsule --json
```

Expected:

- `mode` is `dry-run`
- issue title exists
- labels exist
- token budget is included
- auto-start gate is included

## Release ZIP Check

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\build_release.ps1 -Version 0.2.1
```

Expected:

- `dist/context-capsule-v0.2.1.zip` exists
- launcher scripts are inside the ZIP
- `START_HERE_KO.md` is inside the ZIP
- release notes are inside the ZIP
- `.venv`, `outputs`, `dist`, caches, and credentials are excluded

## Stress Repeat

For extra confidence:

```powershell
.\.venv\Scripts\python.exe scripts\validate_mvp.py --repeat 50
```

Use this when changing retrieval, risk rules, token counting, or output generation.
