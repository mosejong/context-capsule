# Feedback Template

Use this template when KDT learners test Context Capsule on their own projects.

Generate a fresh template:

```powershell
.\context_capsule_cli.bat feedback-template --project-name "my-project" --tester-name "nickname" --save --json
```

Saved output:

```text
outputs/YYYYMMDD_HHMMSS_kdt-feedback-template/KDT_FEEDBACK_TEMPLATE.md
```

The template asks testers to record:

- setup and `doctor` result
- request text they tried
- expected target files
- actual top files
- protected-area behavior
- output usefulness
- confusing moments
- missing user phrasing
- sanitized errors

Do not collect secrets, `.env` values, API tokens, passwords, private keys, or private project code without permission.
