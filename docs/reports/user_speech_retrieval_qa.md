# User-Speech Retrieval QA

Generated at: 2026-06-28 18:27:00

Repository path: `.`

This report validates real Korean colloquial requests against indexed retrieval.

## Summary

- Cases: 8
- PASS: 8
- WARN: 0
- FAIL: 0
- Target cases: 6
- hit@1: 5/6
- hit@3: 6/6
- Average irrelevant top-path count: 2.00
- Protected false positives: 0
- Clarification accuracy: 2/2

## What Is Checked

- request understanding intent and confidence
- protected hints such as `auth` and `db`
- indexed retrieval usage and visible fallback
- target file hit@1 and hit@3
- irrelevant retrieved path count
- protected false positives
- clarification-only accuracy
- ambiguous requests stop with one clarification question
- token baseline scope is not whole-repo concat

## Results

| Case | Verdict | Intent | hit@1 | hit@3 | Irrelevant | Protected | Retrieval | Baseline | Top Paths | Notes |
| --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| readme_short | PASS | documentation_edit / high | yes | yes | 2 | None | indexed | retrieved_file_contents | README.md, tests/fixtures/external_repos/ecommerce/README.md, docs/reports/user_speech_retrieval_qa.md | OK |
| readme_portfolio | PASS | documentation_edit / high | yes | yes | 2 | None | indexed | retrieved_file_contents | README.md, tests/fixtures/external_repos/ecommerce/README.md, docs/reports/user_speech_retrieval_qa.md | OK |
| simple_retriever_colloquial | PASS | retrieval_change / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/retrievers/simple_retriever.py, scripts/validate_user_speech.py, tests/test_simple_retriever.py | OK |
| github_issue_bug | PASS | github_issue_bug_investigation / high | yes | yes | 3 | None | indexed | retrieved_file_contents | app/adapters/github_issue_adapter.py, app/cli.py, app/analyzers/request_understanding.py, scripts/validate_user_speech.py, docs/reports/user_speech_retrieval_qa.md | OK |
| local_launcher_bug | PASS | launcher_bug_investigation / high | yes | yes | 0 | None | indexed | retrieved_file_contents | scripts/install_windows.ps1, scripts/run_dashboard.ps1, run_context_capsule.bat, docs/local_app.md | OK |
| token_metric_suspicious | PASS | metric_validation / high | no | yes | 3 | None | indexed | retrieved_file_contents | docs/validation.md, docs/reports/performance_comparison.md, scripts/generate_performance_report.py, app/analyzers/token_analyzer.py, README.md | OK |
| ambiguous_this | PASS | bug_investigation / low | no | no | 0 | None | clarification_only | clarification_only | None | OK |
| ambiguous_previous | PASS | general / low | no | no | 0 | None | clarification_only | clarification_only | None | OK |

## How To Regenerate

```powershell
.\.venv\Scripts\python.exe scripts\validate_user_speech.py --repo-path .
```
