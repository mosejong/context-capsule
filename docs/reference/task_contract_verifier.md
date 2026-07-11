# Task Contract Verifier

Context Capsule v0.5.0 adds a lightweight harness around the existing Work Handoff flow.

## Boundary

The verifier is read-only. It does not inspect git automatically, edit files, execute tests, or grant approval. A caller supplies changed repository paths and check outcomes; Context Capsule compares that evidence with the saved contract.

## Contract

Every saved Work Handoff packet includes `TASK_CONTRACT.json` with:

- task
- allowed paths
- forbidden path patterns
- forbidden rules
- acceptance criteria
- required checks
- whether human approval is required

The initial allowed paths come from retrieved context. This is intentionally conservative: if an implementation needs another file, the person should expand the contract instead of silently allowing scope drift.

## Verdicts

| Verdict | Meaning |
| --- | --- |
| PASS | changed paths are in scope, approval is present when required, and all required checks passed |
| WARN | no boundary violation was reported, but one or more required checks were not run |
| BLOCKED | forbidden/out-of-scope path, missing approval, or failed check |

## CLI

```powershell
.\context_capsule_cli.bat verify `
  --contract outputs\...\TASK_CONTRACT.json `
  --changed-file app\auth.py `
  --check scope_review=passed `
  --check test_or_run_result=passed `
  --check acceptance_criteria_review=passed `
  --approval-granted `
  --json
```

The command exits `0` only for PASS, `1` for WARN/BLOCKED, and `2` for invalid input.

## FastAPI

`POST /api/verify-contract` accepts the contract, changed paths, check results, and the approval flag. It returns the same structured verdict as the CLI.

The Korean local UI exposes the same flow through `작업 결과 검증`: paste `TASK_CONTRACT.json`, list changed paths, record the three required checks, and confirm human approval when needed.

## Trust Note

The verifier checks reported evidence. It does not prove that the changed-path list or test result is truthful. Git adapter and subprocess execution are intentionally deferred so the public MVP remains local, predictable, and human-controlled.
