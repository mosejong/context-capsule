# Scale and app/web Audit

This run-scoped audit measures the local scanner on generated repositories and verifies the FastAPI `app/web` handoff path. It is not a cross-machine benchmark.

## Scale Results

| Requested | Included | Truncated | Median Seconds | Peak Memory MB | Warnings |
| ---: | ---: | --- | ---: | ---: | --- |
| 1,000 | 1,000 | False | 0.1962 | 0.75 | none |
| 5,000 | 5,000 | False | 0.8740 | 3.10 | none |
| 10,000 | 5,000 | True | 0.8664 | 3.10 | max_files_reached |

The default scanner cap is 5,000 included files. A 10k fixture is expected to stop at that cap and emit `max_files_reached`; this is a measured safety boundary, not a 10k full-scan claim.

## app/web Contract

- `/api/health`: 200
- `/api/work-handoff`: 200
- `app/web/server.py` selected for an explicit app/web request: True
- API version: 0.5.0

## Reproduce

```powershell
.\.venv\Scripts\python.exe scripts\audit_scale_and_web.py
```
