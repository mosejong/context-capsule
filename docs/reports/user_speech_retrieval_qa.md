# User-Speech Retrieval QA

Generated at: 2026-06-23 21:17:30

Repository path: `.`

This report validates real Korean colloquial requests against indexed retrieval.

## Summary

- Cases: 11
- PASS: 11
- WARN: 0
- FAIL: 0

## What Is Checked

- request understanding intent and confidence
- protected hints such as `auth` and `db`
- indexed retrieval usage and visible fallback
- target file appears in top 1-3 or top 1-5 depending on task
- ambiguous requests stop with one clarification question
- token baseline scope is not whole-repo concat

## Results

| Case | Verdict | Intent | Protected | Retrieval | Baseline | Top Paths | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| readme_short | PASS | documentation_edit / high | None | indexed | retrieved_file_contents | README.md, docs/reports/user_speech_retrieval_qa.md, tests/test_simple_retriever.py | OK |
| readme_portfolio | PASS | documentation_edit / high | None | indexed | retrieved_file_contents | README.md, docs/reports/user_speech_retrieval_qa.md, tests/test_simple_retriever.py | OK |
| simple_retriever_colloquial | PASS | retrieval_change / high | None | indexed | retrieved_file_contents | app/retrievers/simple_retriever.py, tests/test_simple_retriever.py, docs/reports/user_speech_retrieval_qa.md | OK |
| simple_retriever_vector | PASS | retrieval_change / high | None | indexed | retrieved_file_contents | app/retrievers/simple_retriever.py, tests/test_simple_retriever.py, docs/reports/user_speech_retrieval_qa.md | OK |
| github_issue_bug | PASS | github_issue_bug_investigation / high | None | indexed | retrieved_file_contents | app/adapters/github_issue_adapter.py, app/cli.py, tests/test_github_issue_adapter.py, app/analyzers/request_understanding.py, tests/test_simple_retriever.py | OK |
| local_launcher_bug | PASS | launcher_bug_investigation / high | None | indexed | retrieved_file_contents | docs/local_app.md, scripts/run_dashboard.ps1, run_context_capsule.bat, app/main.py, tests/test_local_launcher.py | OK |
| token_metric_suspicious | PASS | metric_validation / high | None | indexed | retrieved_file_contents | docs/validation.md, scripts/generate_performance_report.py, docs/reports/performance_comparison.md, app/analyzers/token_analyzer.py, app/analyzers/request_understanding.py | OK |
| protect_auth_docs_only | PASS | documentation_edit / high | auth | indexed | retrieved_file_contents | README.md, docs/release_publish_checklist.md, docs/reports/user_speech_retrieval_qa.md, docs/research/llm_tech_scan_2026-06-22.md, docs/research/paid_api_impact_scan_2026-06-22.md | OK |
| protect_db_output_copy | PASS | output_text_edit / high | db | indexed | retrieved_file_contents | app/generators/output_writer.py, app/main.py, app/generators/capsule_generator.py, tests/test_capsule_generator.py, tests/test_output_writer.py | OK |
| ambiguous_this | PASS | bug_investigation / low | None | clarification_only | clarification_only | None | OK |
| ambiguous_previous | PASS | general / low | None | clarification_only | clarification_only | None | OK |

## How To Regenerate

```powershell
.\.venv\Scripts\python.exe scripts\validate_user_speech.py --repo-path .
```
