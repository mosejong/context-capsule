# NVIDIA NIM Provider Lab

Context Capsule remains local-first by default. NVIDIA NIM support is an optional external-provider experiment for comparing Raw vs Capsule quality with OpenAI-compatible cloud endpoints.

## Position

Use this mode for:

- model quality experiments
- Raw vs Capsule comparison
- prototype demos
- checking whether cheaper/free prototype endpoints can validate the handoff-packet idea

Do not describe this as:

- closed-network mode
- unlimited free production inference
- a required dependency
- a default Context Capsule runtime

NVIDIA Build lists free inference endpoints and model pages show OpenAI-compatible examples using:

```text
base_url = "https://integrate.api.nvidia.com/v1"
```

Official pages:

- NVIDIA Build: https://build.nvidia.com/
- Models: https://build.nvidia.com/models
- Nemotron 3 Ultra: https://build.nvidia.com/nvidia/nemotron-3-ultra-550b-a55b
- DeepSeek V4 Flash: https://build.nvidia.com/deepseek-ai/deepseek-v4-flash
- NVIDIA API Docs: https://docs.api.nvidia.com/

## Environment

Only environment variables are used. The provider also loads a local `.env` file from the repository root when present. `.env` is ignored by git.

Recommended:

```env
NVIDIA_API_KEY=...
```

PowerShell session-only alternative:

```powershell
$env:NVIDIA_API_KEY = "..."
```

Optional:

```powershell
$env:NVIDIA_NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
```

Never place keys in:

- command examples
- markdown reports
- metadata files
- committed scripts
- screenshots

## Compare Script

Run a NVIDIA NIM comparison:

```powershell
.\.venv\Scripts\python.exe scripts\compare_raw_vs_capsule.py `
  --provider nvidia `
  --models nvidia/nemotron-3-ultra-550b-a55b deepseek-ai/deepseek-v4-flash `
  --repos dummy `
  --task-limit 1 `
  --output docs\reports\raw_vs_capsule_nvidia.md
```

The script writes provider/model names and scores, but does not write `NVIDIA_API_KEY`.

For the first smoke test, keep `--repos dummy --task-limit 1`. Remove those limits only after the provider works, because the full experiment can call multiple repositories and many model requests.

Reports generated with `--task-limit` are smoke-test reports. They must not be described as full benchmark results. The repo/model summary table is generated only from rows measured in the current run.

Anthropic and NVIDIA provider calls use the same sampling defaults for comparison runs:

```text
temperature = 0.2
top_p = 0.95
```

## Current Safety Rules

- The app still works without NVIDIA credentials.
- API calls happen only when the comparison script is explicitly run with `--provider nvidia`.
- The default report path for NVIDIA is separate: `docs/reports/raw_vs_capsule_nvidia.md`.
- No local price table is configured for NVIDIA. Usage can be captured if the endpoint returns usage, but the report does not convert it to billing cost.
- NVIDIA endpoint availability is treated as prototype/testing availability, not a product SLA.

## Claude Review Prompt

After generating a NVIDIA report, ask an external reviewer to check:

```text
Context Capsule v0.4.0 includes optional NVIDIA NIM provider support and run-scoped smoke, medium, and large-repo reports.

Please review:
1. whether the design still matches local-first / human-in-the-loop principles
2. whether free endpoint wording is overclaimed
3. whether NVIDIA_API_KEY can leak into logs, metadata, reports, or prompts
4. whether Raw vs Capsule comparison is fair
5. whether the smoke report only includes rows measured in the current run
6. whether NVIDIA/Claude/OpenAI comparisons are described honestly

Do not edit code. Review only.
```
