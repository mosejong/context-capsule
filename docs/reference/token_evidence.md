# Token Evidence Guide

This guide explains what the Token Evidence numbers mean and what they do not mean.

## Short Answer

Context Capsule does not magically reduce provider billing by itself.

It reduces the amount of context you are expected to paste into an AI coding tool by turning candidate files into a smaller handoff prompt.

```text
before:
candidate files + rough instruction

after:
small handoff prompt with target files, risks, and approval rules
```

## What Is Compared

The current dashboard compares two local estimates.

```text
Candidate files
The full contents of files selected by retrieval.

Handoff prompt
The generated AI Handoff / target-specific packet.
```

The reduction is:

```text
1 - handoff_prompt_tokens / candidate_file_tokens
```

Example:

```text
Candidate files: 3,000 tokens
Handoff prompt: 600 tokens
Estimated reduction: 80%
```

This means: if you would otherwise paste those candidate files into Claude/Codex/GPT, the generated prompt is much smaller.

## What This Does Not Claim

Context Capsule does not currently claim:

```text
actual Claude billing reduction
actual OpenAI billing reduction
actual Codex usage reduction
model quality improvement percentage
guaranteed task success
```

The dashboard labels this honestly:

```text
Method: approx_local_v1
Verification status: Estimated only
Actual provider usage: Not measured yet
```

## Why This Still Matters

Even before provider usage is connected, the metric is useful because it shows whether Context Capsule is doing its main job:

```text
1. Find the likely files.
2. Avoid unrelated repository context.
3. Convert the useful parts into a smaller work brief.
4. Keep risky areas and approval rules visible.
```

If the handoff prompt is not smaller, that is also useful feedback. It means the retrieved context was already tiny, or the generated brief is too verbose.

## How To Validate Locally

Run the performance report:

```powershell
.\.venv\Scripts\python.exe scripts\generate_performance_report.py
```

Open:

```text
docs/reports/performance_comparison.md
docs/assets/performance_comparison.svg
```

The report tracks:

```text
candidate file context tokens
handoff prompt tokens
estimated reduction
relevant file hit rate
unrelated file count
scope escape
auto-start gate
```

## Future Token Analyzer Adapter

When the external Token Analyzer API or provider usage data is available, Context Capsule should compare:

```text
local estimate
actual provider input tokens
actual provider output tokens
actual total usage
```

Until then, Token Evidence is a local, honest estimate for prompt-size comparison.
