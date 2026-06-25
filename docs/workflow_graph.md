# Workflow Graph Trace

Context Capsule v0.2.3 added a local workflow graph trace for Work Handoff packets. v0.2.5 polishes the user-facing wording so first testers see Korean stage labels and simpler result guidance.

This is inspired by graph-style agent workflows such as LangGraph, but it is not an autonomous multi-agent system yet. It does not call external AI services, does not assign work automatically, and does not start code changes. It records the deterministic steps Context Capsule already performs so users can see why a work summary was generated, blocked, or stopped for clarification.

## Why It Exists

Beta testers asked whether Context Capsule really understands the request and why a result should be trusted.

The graph trace answers:

```text
What did it scan?
How did it understand my request?
Which retrieval mode was used?
Did it skip retrieval because the request was too vague?
Why was auto-start allowed or blocked?
Where should I look next?
```

## Current Nodes

```text
scan_repository
-> understand_request
-> retrieve_context
-> analyze_risk
-> generate_packet
-> review_gate
-> save_output
```

Each node records:

- status: `completed`, `skipped`, `blocked`, or `needs_input`
- human-readable summary
- short evidence
- next action

## Status Meaning

| Status | Meaning |
| --- | --- |
| `completed` | The step ran normally. |
| `skipped` | The step was intentionally skipped, usually because an earlier step needs input. |
| `blocked` | A safety rule or high-risk condition stopped automatic continuation. |
| `needs_input` | The user needs to clarify the request before the workflow can continue. |

## Example: Normal Request

```text
리드미 손보자
```

Expected graph:

```text
scan_repository: completed
understand_request: completed
retrieve_context: completed
analyze_risk: completed
generate_packet: completed
review_gate: completed
save_output: skipped or completed
```

## Example: Ambiguous Request

```text
이거 왜그래?
```

Expected graph:

```text
scan_repository: completed
understand_request: needs_input
retrieve_context: skipped
analyze_risk: skipped
generate_packet: completed
review_gate: needs_input
```

The important behavior is that Context Capsule asks one clarification question instead of guessing and wasting context.

## Example: Risky Request

```text
JWT secret/env 값을 수정해줘
```

Expected graph:

```text
scan_repository: completed
understand_request: completed
retrieve_context: completed
analyze_risk: blocked
generate_packet: completed
review_gate: blocked
```

The generated packet can still explain the risk, but auto-start remains blocked.

## Safety Boundary

The graph trace is an explanation layer, not an execution engine.

It must not:

- call Claude, GPT, Codex, or other external AI services
- edit files
- create GitHub Issues automatically
- create branches
- assign teammates
- score teammates

It can:

- show the internal decision path
- explain why a request needs clarification
- explain why a request was blocked
- expose fallback behavior
- make future Discord/LangGraph-style adapters safer to design

## Future Direction

If Context Capsule later adopts LangGraph or a similar orchestration framework, this trace can become the boundary contract:

```text
state
-> node result
-> evidence
-> safety gate
-> human approval
```

For now, the rule-based trace is intentionally simple. It improves trust without adding external model dependency or autonomous execution risk.
