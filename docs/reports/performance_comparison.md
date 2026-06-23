# Performance Comparison v2

Generated at: 2026-06-23 16:09:10

This report is generated from the MVP validation scenarios.

![Performance comparison](../assets/performance_comparison.svg)

## Summary

- Scenarios validated: 5
- Best token reduction: future_me_handoff (91.3%)
- Average token reduction: 68.7%
- Average relevant file hit rate: 100.0%
- Success proxy pass rate: 5/5
- Scope escape count: 0
- Auto-start blocked scenarios: high_risk_auth_blocks_auto_start

## What Is Compared

- Candidate context: sending the full contents of retrieved candidate files without compression.
- Capsule tokens: sending the generated handoff packet instead.
- Relevant file hit: whether expected files for the task were retrieved.
- Success proxy: validation assertions passed for the scenario.
- Scope escape: validation detected retrieval outside the expected task scope.

## Metrics

| Scenario | Auto Start | Candidate Tokens | Capsule Tokens | Reduction | Relevant File Hit | Unrelated Files | Success Proxy | Scope Escape |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |
| direct_readme_brief | allowed | 3,024 | 464 | 84.7% | 100.0% | 0 | pass | no |
| chat_error_to_capsule | allowed | 14 | 380 | 0.0% | 100.0% | 0 | pass | no |
| high_risk_auth_blocks_auto_start | blocked | 3,038 | 563 | 81.5% | 100.0% | 2 | pass | no |
| teammate_brief | allowed | 3,032 | 427 | 85.9% | 100.0% | 1 | pass | no |
| future_me_handoff | allowed | 3,052 | 265 | 91.3% | 100.0% | 0 | pass | no |

## How To Regenerate

```powershell
.\.venv\Scripts\python.exe scripts\generate_performance_report.py
```
