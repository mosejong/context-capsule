# User-Speech Retrieval QA

Generated at: 2026-06-25 14:01:31

Repository path: `.`

This report validates real Korean colloquial requests against indexed retrieval.

## Summary

- Cases: 73
- PASS: 73
- WARN: 0
- FAIL: 0
- Target cases: 61
- hit@1: 54/61
- hit@3: 61/61
- Average irrelevant top-path count: 2.44
- Protected false positives: 0
- Clarification accuracy: 8/8

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
| readme_short | PASS | documentation_edit / high | yes | yes | 2 | None | indexed | retrieved_file_contents | README.md, docs/reports/user_speech_retrieval_qa.md, docs/request_understanding.md | OK |
| readme_portfolio | PASS | documentation_edit / high | yes | yes | 2 | None | indexed | retrieved_file_contents | README.md, docs/reports/user_speech_retrieval_qa.md, docs/request_understanding.md | OK |
| readme_cleanup | PASS | documentation_edit / high | yes | yes | 2 | None | indexed | retrieved_file_contents | README.md, docs/reports/user_speech_retrieval_qa.md, docs/request_understanding.md | OK |
| readme_ko_alias | PASS | documentation_edit / high | yes | yes | 2 | None | indexed | retrieved_file_contents | README.md, docs/reports/user_speech_retrieval_qa.md, docs/request_understanding.md | OK |
| docs_summary | PASS | documentation_edit / high | yes | yes | 4 | None | indexed | retrieved_file_contents | README.md, docs/release_publish_checklist.md, docs/releases/v0.1.3.md, docs/reports/user_speech_retrieval_qa.md, docs/v1_roadmap.md | OK |
| docs_portfolio | PASS | documentation_edit / high | yes | yes | 4 | None | indexed | retrieved_file_contents | README.md, docs/reports/user_speech_retrieval_qa.md, docs/request_understanding.md, docs/releases/v0.1.7.md, docs/commercialization_strategy.md | OK |
| simple_retriever_colloquial | PASS | retrieval_change / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/retrievers/simple_retriever.py, tests/test_simple_retriever.py, scripts/validate_user_speech.py | OK |
| simple_retriever_vector | PASS | retrieval_change / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/retrievers/simple_retriever.py, tests/test_simple_retriever.py, scripts/validate_user_speech.py | OK |
| retriever_ranking_bug | PASS | retrieval_change / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/retrievers/simple_retriever.py, tests/test_simple_retriever.py, scripts/validate_user_speech.py | OK |
| retriever_search_quality | PASS | retrieval_change / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/retrievers/simple_retriever.py, tests/test_simple_retriever.py, scripts/validate_user_speech.py | OK |
| retriever_score_suspicious | PASS | retrieval_change / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/retrievers/simple_retriever.py, tests/test_simple_retriever.py, scripts/validate_user_speech.py | OK |
| retriever_test_hint | PASS | retrieval_change / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/retrievers/simple_retriever.py, tests/test_simple_retriever.py, scripts/validate_user_speech.py | OK |
| github_issue_bug | PASS | github_issue_bug_investigation / high | yes | yes | 3 | None | indexed | retrieved_file_contents | app/adapters/github_issue_adapter.py, app/cli.py, app/analyzers/request_understanding.py, scripts/validate_user_speech.py, docs/reports/user_speech_retrieval_qa.md | OK |
| github_issue_dry_run | PASS | github_issue_bug_investigation / high | yes | yes | 3 | None | indexed | retrieved_file_contents | app/adapters/github_issue_adapter.py, app/cli.py, app/analyzers/request_understanding.py, scripts/validate_user_speech.py, docs/reports/user_speech_retrieval_qa.md | OK |
| github_issue_payload | PASS | github_issue_bug_investigation / high | yes | yes | 3 | None | indexed | retrieved_file_contents | app/adapters/github_issue_adapter.py, app/cli.py, app/analyzers/request_understanding.py, scripts/validate_user_speech.py, docs/reports/user_speech_retrieval_qa.md | OK |
| github_issue_adapter | PASS | github_issue_bug_investigation / high | yes | yes | 3 | None | indexed | retrieved_file_contents | app/adapters/github_issue_adapter.py, app/cli.py, app/analyzers/request_understanding.py, scripts/validate_user_speech.py, docs/reports/user_speech_retrieval_qa.md | OK |
| github_issue_skip_labels | PASS | github_issue_bug_investigation / high | yes | yes | 3 | None | indexed | retrieved_file_contents | app/adapters/github_issue_adapter.py, app/cli.py, app/analyzers/request_understanding.py, scripts/validate_user_speech.py, docs/reports/user_speech_retrieval_qa.md | OK |
| github_issue_command_error | PASS | github_issue_bug_investigation / high | yes | yes | 3 | None | indexed | retrieved_file_contents | app/adapters/github_issue_adapter.py, app/cli.py, app/analyzers/request_understanding.py, scripts/validate_user_speech.py, docs/reports/user_speech_retrieval_qa.md | OK |
| local_launcher_bug | PASS | launcher_bug_investigation / high | yes | yes | 1 | None | indexed | retrieved_file_contents | scripts/run_dashboard.ps1, scripts/install_windows.ps1, docs/local_app.md, run_context_capsule.bat | OK |
| local_dashboard_bug | PASS | launcher_bug_investigation / high | yes | yes | 1 | None | indexed | retrieved_file_contents | scripts/run_dashboard.ps1, scripts/install_windows.ps1, docs/local_app.md, run_context_capsule.bat | OK |
| local_run_dashboard_error | PASS | launcher_bug_investigation / high | yes | yes | 1 | None | indexed | retrieved_file_contents | scripts/run_dashboard.ps1, scripts/install_windows.ps1, docs/local_app.md, run_context_capsule.bat | OK |
| local_bat_bug | PASS | launcher_bug_investigation / high | yes | yes | 1 | None | indexed | retrieved_file_contents | scripts/run_dashboard.ps1, scripts/install_windows.ps1, docs/local_app.md, run_context_capsule.bat | OK |
| local_streamlit_bug | PASS | launcher_bug_investigation / high | yes | yes | 2 | None | indexed | retrieved_file_contents | scripts/run_dashboard.ps1, scripts/install_windows.ps1, docs/local_app.md, run_context_capsule.bat | OK |
| local_port_bug | PASS | launcher_bug_investigation / high | yes | yes | 1 | None | indexed | retrieved_file_contents | scripts/run_dashboard.ps1, scripts/install_windows.ps1, docs/local_app.md, run_context_capsule.bat | OK |
| token_metric_suspicious | PASS | metric_validation / high | no | yes | 3 | None | indexed | retrieved_file_contents | docs/validation.md, scripts/generate_performance_report.py, docs/reports/performance_comparison.md, app/analyzers/token_analyzer.py, README.md | OK |
| token_budget_bug | PASS | metric_validation / high | no | yes | 3 | None | indexed | retrieved_file_contents | docs/validation.md, scripts/generate_performance_report.py, docs/reports/performance_comparison.md, app/analyzers/token_analyzer.py, README.md | OK |
| token_reduction_suspicious | PASS | metric_validation / high | no | yes | 3 | None | indexed | retrieved_file_contents | docs/validation.md, scripts/generate_performance_report.py, docs/reports/performance_comparison.md, app/analyzers/token_analyzer.py, README.md | OK |
| token_usage_check | PASS | metric_validation / high | no | yes | 3 | None | indexed | retrieved_file_contents | docs/validation.md, scripts/generate_performance_report.py, docs/reports/performance_comparison.md, app/analyzers/token_analyzer.py, README.md | OK |
| performance_report_check | PASS | metric_validation / high | no | yes | 3 | None | indexed | retrieved_file_contents | docs/validation.md, scripts/generate_performance_report.py, docs/reports/performance_comparison.md, app/analyzers/token_analyzer.py, README.md | OK |
| token_analyzer_adapter_hint | PASS | metric_validation / high | no | yes | 3 | None | indexed | retrieved_file_contents | docs/validation.md, scripts/generate_performance_report.py, docs/reports/performance_comparison.md, app/analyzers/token_analyzer.py, README.md | OK |
| output_copy | PASS | output_text_edit / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/generators/capsule_generator.py, app/generators/output_writer.py, app/main.py, app/analyzers/request_understanding.py, scripts/validate_user_speech.py | OK |
| ai_handoff_copy | PASS | output_text_edit / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/generators/capsule_generator.py, app/generators/output_writer.py, app/main.py, app/analyzers/request_understanding.py, scripts/validate_user_speech.py | OK |
| github_issue_output_copy | PASS | output_text_edit / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/generators/capsule_generator.py, app/generators/output_writer.py, app/main.py, app/analyzers/request_understanding.py, scripts/validate_user_speech.py | OK |
| metadata_output | PASS | output_text_edit / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/generators/capsule_generator.py, app/generators/output_writer.py, app/main.py, app/analyzers/request_understanding.py, scripts/validate_user_speech.py | OK |
| teammate_brief_copy | PASS | output_text_edit / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/generators/capsule_generator.py, app/generators/output_writer.py, app/main.py, app/analyzers/request_understanding.py, scripts/validate_user_speech.py | OK |
| scrum_notes | PASS | scrum_notes / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, docs/v0.2_scrum_kickoff_modes.md | OK |
| meeting_next_actions | PASS | scrum_notes / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, docs/v0.2_scrum_kickoff_modes.md | OK |
| kickoff_scope | PASS | project_kickoff / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, scripts/validate_user_speech.py | OK |
| kickoff_mvp | PASS | project_kickoff / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, scripts/validate_user_speech.py | OK |
| kickoff_contest_checklist | PASS | project_kickoff / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, scripts/validate_user_speech.py | OK |
| ram_colab_issue | PASS | runtime_environment_issue / high | no | no | 0 | None | indexed | retrieved_file_contents | app/analyzers/request_understanding.py, scripts/validate_user_speech.py, tests/test_github_issue_adapter.py, docs/research/llm_tech_scan_2026-06-22.md, scripts/validate_mvp.py | OK |
| image_black_screen | PASS | media_render_bug / high | no | no | 0 | None | indexed | retrieved_file_contents | app/main.py, app/services/feedback_service.py, app/analyzers/request_understanding.py, app/services/doctor_service.py, scripts/validate_user_speech.py | OK |
| generated_but_not_saved | PASS | file_output_bug / high | yes | yes | 2 | None | indexed | retrieved_file_contents | docs/local_app.md, app/main.py, app/generators/output_writer.py, scripts/run_dashboard.ps1, scripts/install_windows.ps1 | OK |
| check_save_path | PASS | file_output_bug / high | yes | yes | 2 | None | indexed | retrieved_file_contents | docs/local_app.md, app/main.py, app/generators/output_writer.py, scripts/run_dashboard.ps1, scripts/install_windows.ps1 | OK |
| missing_log | PASS | logging_issue / high | yes | yes | 2 | None | indexed | retrieved_file_contents | app/cli.py, app/main.py, app/generators/output_writer.py, docs/reports/user_speech_retrieval_qa.md, app/analyzers/request_understanding.py | OK |
| timeout_generation | PASS | timeout_issue / high | no | no | 0 | None | indexed | retrieved_file_contents | app/analyzers/request_understanding.py, scripts/validate_user_speech.py, tests/test_meeting_analyzer.py, scripts/validate_mvp.py, tests/fixtures/scrum_runtime_issue_ko.txt | OK |
| increase_timeout | PASS | timeout_issue / high | no | no | 0 | None | indexed | retrieved_file_contents | app/analyzers/request_understanding.py, scripts/validate_user_speech.py, tests/test_meeting_analyzer.py, scripts/validate_mvp.py, tests/fixtures/scrum_runtime_issue_ko.txt | OK |
| script_review | PASS | presentation_review / high | yes | yes | 3 | None | indexed | retrieved_file_contents | docs/v0.2_scrum_kickoff_modes.md, app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, README.md, docs/v1_roadmap.md | OK |
| add_eval_report | PASS | presentation_review / high | yes | yes | 3 | None | indexed | retrieved_file_contents | docs/v0.2_scrum_kickoff_modes.md, app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, README.md, docs/v1_roadmap.md | OK |
| presentation_feedback | PASS | presentation_review / high | yes | yes | 3 | None | indexed | retrieved_file_contents | docs/v0.2_scrum_kickoff_modes.md, app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, README.md, docs/v1_roadmap.md | OK |
| demo_video_saved | PASS | file_output_bug / high | yes | yes | 2 | None | indexed | retrieved_file_contents | docs/local_app.md, app/main.py, docs/v0.2_scrum_kickoff_modes.md, app/generators/output_writer.py, app/analyzers/meeting_analyzer.py | OK |
| zoom_audio_low | PASS | presentation_environment_issue / high | yes | yes | 3 | None | indexed | retrieved_file_contents | docs/v0.2_scrum_kickoff_modes.md, app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, README.md, docs/v1_roadmap.md | OK |
| share_audio_missing | PASS | presentation_environment_issue / high | yes | yes | 3 | None | indexed | retrieved_file_contents | docs/v0.2_scrum_kickoff_modes.md, app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, README.md, docs/v1_roadmap.md | OK |
| ppt_script_mismatch | PASS | presentation_review / high | yes | yes | 3 | None | indexed | retrieved_file_contents | docs/v0.2_scrum_kickoff_modes.md, app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, README.md, docs/v1_roadmap.md | OK |
| slide_page_edit | PASS | media_render_bug / high | yes | yes | 3 | None | indexed | retrieved_file_contents | docs/v0.2_scrum_kickoff_modes.md, app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, README.md, docs/v1_roadmap.md | OK |
| presentation_polish | PASS | presentation_review / high | yes | yes | 3 | None | indexed | retrieved_file_contents | docs/v0.2_scrum_kickoff_modes.md, app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, README.md, docs/v1_roadmap.md | OK |
| vague_this_bug | PASS | bug_investigation / low | no | no | 0 | None | clarification_only | clarification_only | None | OK |
| continue_previous_chat | PASS | general / low | no | no | 0 | None | clarification_only | clarification_only | None | OK |
| task_offer | PASS | team_coordination / high | yes | yes | 3 | None | indexed | retrieved_file_contents | docs/v0.2_scrum_kickoff_modes.md, app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, README.md, docs/v1_roadmap.md | OK |
| rehearsal_schedule | PASS | presentation_review / high | yes | yes | 3 | None | indexed | retrieved_file_contents | docs/v0.2_scrum_kickoff_modes.md, app/analyzers/meeting_analyzer.py, docs/reports/user_speech_retrieval_qa.md, README.md, docs/v1_roadmap.md | OK |
| protect_auth_docs_only | PASS | documentation_edit / high | yes | yes | 4 | auth | indexed | retrieved_file_contents | README.md, docs/release_publish_checklist.md, docs/releases/v0.1.3.md, docs/reports/user_speech_retrieval_qa.md, docs/v1_roadmap.md | OK |
| protect_db_output_copy | PASS | output_text_edit / high | yes | yes | 2 | db | indexed | retrieved_file_contents | app/generators/capsule_generator.py, app/generators/output_writer.py, app/main.py, app/analyzers/request_understanding.py, scripts/validate_user_speech.py | OK |
| protect_jwt_readme | PASS | documentation_edit / high | yes | yes | 4 | auth | indexed | retrieved_file_contents | README.md, docs/reports/user_speech_retrieval_qa.md, docs/request_understanding.md, docs/releases/v0.1.7.md, docs/commercialization_strategy.md | OK |
| protect_secret_token_report | PASS | metric_validation / high | no | yes | 3 | secret | indexed | retrieved_file_contents | docs/validation.md, scripts/generate_performance_report.py, docs/reports/performance_comparison.md, app/analyzers/token_analyzer.py, README.md | OK |
| protect_env_local | PASS | launcher_bug_investigation / high | yes | yes | 1 | secret | indexed | retrieved_file_contents | scripts/run_dashboard.ps1, scripts/install_windows.ps1, docs/local_app.md, run_context_capsule.bat | OK |
| protect_deploy_docs | PASS | documentation_edit / high | yes | yes | 4 | deploy | indexed | retrieved_file_contents | README.md, docs/release_publish_checklist.md, docs/releases/v0.1.3.md, docs/reports/user_speech_retrieval_qa.md, docs/v1_roadmap.md | OK |
| protect_db_output | PASS | output_text_edit / high | yes | yes | 2 | db | indexed | retrieved_file_contents | app/generators/capsule_generator.py, app/generators/output_writer.py, app/main.py, app/analyzers/request_understanding.py, scripts/validate_user_speech.py | OK |
| ambiguous_this | PASS | bug_investigation / low | no | no | 0 | None | clarification_only | clarification_only | None | OK |
| ambiguous_previous | PASS | general / low | no | no | 0 | None | clarification_only | clarification_only | None | OK |
| ambiguous_that | PASS | bug_investigation / low | no | no | 0 | None | clarification_only | clarification_only | None | OK |
| ambiguous_do_that | PASS | general / low | no | no | 0 | None | clarification_only | clarification_only | None | OK |
| ambiguous_touch_this | PASS | documentation_edit / low | no | no | 0 | None | clarification_only | clarification_only | None | OK |
| ambiguous_continue | PASS | general / low | no | no | 0 | None | clarification_only | clarification_only | None | OK |

## How To Regenerate

```powershell
.\.venv\Scripts\python.exe scripts\validate_user_speech.py --repo-path .
```
