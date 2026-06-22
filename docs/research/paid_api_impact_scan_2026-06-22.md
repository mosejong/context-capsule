# Paid API Impact Scan

Date: 2026-06-22

Purpose:

> Estimate where paid cloud LLM APIs can improve Context Capsule, what numbers are currently defensible, and what must be measured inside this project before making portfolio claims.

This document is not a promise that a paid API will make Context Capsule "N% better." It separates published evidence from project-specific hypotheses.

## 1. Short Answer

Paid APIs should be optional accelerators, not the core architecture.

For Context Capsule, a paid API can help most in these steps:

1. Chat-to-task extraction
2. Retrieved context summarization
3. Risk explanation wording
4. Target-specific prompt rewriting
5. LLM-as-judge evaluation for generated capsules

Paid APIs help least in these steps:

1. Repository scanning
2. File classification
3. Secret exclusion
4. Basic keyword retrieval
5. Rule-based risk detection

Those local steps should stay deterministic, testable, and closed-network safe.

## 2. Defensible Numbers From Current Research

### Prompt caching

A 2026 arXiv study on prompt caching across OpenAI, Anthropic, and Google agentic workloads reported:

- API cost reduction: 41-80%
- Time to first token improvement: 13-31%
- Test setup included multi-turn agent sessions and 10,000-token system prompts

How this applies to Context Capsule:

- Strong fit when the same repo rules, project overview, or coding standards are reused across many capsule generations.
- Weak fit when every run scans totally different repositories or when prompt blocks change constantly.
- Best design: place stable repo policy/context before dynamic task-specific chunks, so cacheable blocks remain stable.

### Model tier is not always linear

A 2026 automated code review evaluation compared Claude Sonnet 4.6, Claude Haiku 4.5, GPT-5.4 mini, Minimax M2.7, and GLM-5 Turbo across synthetic and real PR review samples. In that study, Haiku 4.5 beat Sonnet 4.6 on several code-review metrics:

- F1: 0.365 vs 0.343 (+6.4%)
- Recall: 0.293 vs 0.248 (+18.1%)
- Specificity score: +13.4%
- Suggestion score: +15.3%
- Cost per review: 3.2x lower

How this applies to Context Capsule:

- Do not assume "more expensive model = better capsule."
- Add model routing and evaluation instead of hard-coding a flagship API.
- Smaller paid models may be enough for brief generation if retrieval is already good.

### Real-world code tasks punish large context

The same code-review evaluation found a severe synthetic-to-real gap and showed that large diffs reduce model quality sharply. It reported F1 dropping from 0.657-0.800 on small diffs to 0.043-0.070 on larger diffs exceeding 50 lines.

How this applies to Context Capsule:

- The product thesis gets stronger: reduce the context before giving it to the model.
- Chunking, filtering, and focused handoff prompts may matter more than simply buying a stronger model.

### Token prices keep moving

A 2026 token pricing economics paper reports a roughly 600-fold decline in LLM inference token prices across 2020-2026, but also reports a large "reasoning premium" for flagship models.

How this applies to Context Capsule:

- Cost comparisons will go stale quickly.
- Store provider/model pricing as data, not as hard-coded text in docs.
- Evaluate "cheap model + good context" against "expensive model + raw context."

## 3. Provider Features Relevant To This Project

| Provider | Useful paid feature | Context Capsule usage |
| --- | --- | --- |
| OpenAI | Latency optimization guidance, streaming, prompt caching, priority processing, model tiers | Benchmark target for capsule quality and coding-handoff style |
| Anthropic | Prompt caching, fast mode, long context, model tier guidance, batch API | Claude/Codex-style handoff, repeated repo context reuse |
| Google Gemini | Context caching, Flash/Pro model tiers, paid cached-token pricing | Recurring code repository analysis and bug-fixing workflows |
| Mistral | Code and embed model family, enterprise/API options | Code-aware retrieval and alternative cloud benchmark |
| DeepSeek | Lower-cost external API candidate, OpenAI/Anthropic-compatible formats | Cheap experiment target, but not closed-network safe |

## 4. Expected Impact On Context Capsule

These are implementation hypotheses, not measured results yet.

| Area | Local MVP baseline | Paid API likely effect | Claim status |
| --- | --- | --- | --- |
| Relevant file discovery | Keyword/rule retrieval | Little direct improvement unless used as query rewriter | Must measure |
| Capsule wording quality | Template-based markdown | Better summaries and target-specific instructions | Must measure |
| Risk explanation | Rule labels | Better explanation of why risk matters | Must measure |
| Token cost | Local estimate only | Prompt caching can reduce repeated API cost if stable blocks are reused | Supported by external caching study |
| Perceived speed | Local deterministic generation is fast | Streaming improves perceived wait; cloud may beat CPU local LLM for generation | Provider/hardware dependent |
| Closed-network use | Works locally | Paid API cannot be used | Architectural constraint |

## 5. What We Should Measure

Use three modes:

```text
Mode A: No LLM
Mode B: Local LLM
Mode C: Paid API
```

Run the same task set against each mode:

```text
1. Login API bug brief
2. DB schema change brief
3. Docker/nginx deployment issue brief
4. README/docs cleanup brief
5. Frontend-only UI task brief
6. Security/env secret handling brief
```

Metrics:

```text
quality.related_file_hit_rate
quality.risk_recall
quality.forbidden_rule_retention
quality.completion_criteria_quality
quality.user_acceptance_score

tokens.raw_context_tokens
tokens.retrieved_context_tokens
tokens.final_capsule_tokens
tokens.api_input_tokens
tokens.api_output_tokens
tokens.cached_input_tokens

speed.scan_seconds
speed.retrieval_seconds
speed.llm_seconds
speed.total_seconds
speed.time_to_first_token_seconds

cost.estimated_usd
cost.cost_per_capsule
```

Project-specific claim format:

```text
On the six-task prototype set, Context Capsule reduced prompt input from X tokens to Y tokens
(-Z%) while preserving A% of required risk rules and B% of relevant files.
```

For paid API mode:

```text
Using provider prompt caching on repeated repository context reduced API input cost by X%
and time to first token by Y% on repeated capsule generation.
```

## 6. Recommended Architecture Decision

Keep this boundary:

```text
Core pipeline:
  scan -> classify -> chunk -> retrieve -> risk -> token budget -> template capsule

Optional model layer:
  task rewrite -> summarize retrieved context -> polish target prompt -> judge capsule
```

Reason:

- Context Capsule must still work in closed networks.
- Paid API calls can leak source context if not explicitly controlled.
- The portfolio claim is stronger if the local deterministic MVP already reduces context.
- Paid APIs then become measurable enhancement plugins, not a dependency.

## 7. Implementation Priority

1. Build token analyzer first.
2. Add benchmark fixture tasks.
3. Add a `ModelProvider` interface.
4. Add `NoLLMProvider` baseline.
5. Add `PaidAPIProvider` later with explicit redaction and opt-in.
6. Track speed, token, and quality metrics in output JSON.

## 8. Product Wording

Good wording:

> Context Capsule measures how much repository context is reduced before handoff, then optionally compares local and paid model modes for brief quality, latency, and cost.

Avoid:

> Paid API makes this N% smarter.

Better:

> Paid APIs are evaluated as optional quality and latency boosters after retrieval has already narrowed the work context.

## 9. Sources

- Prompt caching evaluation: https://arxiv.org/abs/2601.06007
- Code review model comparison: https://arxiv.org/abs/2606.15689
- Token pricing economics: https://arxiv.org/abs/2603.28576
- OpenAI API pricing: https://platform.openai.com/docs/pricing
- OpenAI latency optimization: https://developers.openai.com/api/docs/guides/latency-optimization
- Anthropic pricing and prompt caching: https://docs.anthropic.com/en/docs/about-claude/pricing
- Google Gemini API pricing: https://ai.google.dev/gemini-api/docs/pricing
- Google Gemini context caching: https://ai.google.dev/gemini-api/docs/caching
