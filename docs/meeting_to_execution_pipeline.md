# Meeting-to-Execution Pipeline

This document describes the expansion path from handoff packets to meeting-driven work preparation.

## Concept

Context Capsule can turn a fixed idea from a meeting into:

- decision record
- GitHub Issue draft
- AI handoff prompt
- teammate brief
- risk checklist
- token budget summary
- human approval gate

Short version:

```text
"Let's do this"
-> reviewable work packet
-> dry-run GitHub Issue
-> approval
-> execution starts
```

## Product Flow

```text
Discord idea meeting
-> idea fixed by command, reaction, or copied transcript
-> decision record generated
-> repository context retrieved
-> risk and token budget analyzed
-> GitHub Issue / teammate brief / AI handoff generated
-> human approval
-> Claude, Codex, or teammate starts work
```

## Automation Levels

| Level | Name | What Happens | Approval |
| --- | --- | --- | --- |
| 1 | Auto organize | Summarize decision and create a decision record. | Usually not required |
| 2 | Auto prepare | Retrieve files, analyze risk, create issue/brief. | Usually not required |
| 3 | Approved start | Send packet to AI tool or teammate. | Required |
| 4 | Manual merge | Review diff, tests, and merge decision. | Required |

The project should automate preparation, not merge risky changes without a person.

## Discord Bot Role

The Discord bot should act as a decision collector.

Possible commands:

```text
/idea      save an idea during discussion
/fix       convert a fixed idea into a work packet
/brief     generate AI/teammate/future-me brief
/risk      analyze risk before work starts
/start     prepare an approved handoff packet
```

Safety requirements:

- bot tokens are never written to generated packets
- repository tokens are read from environment variables only
- long repository scans should run asynchronously
- dry-run should be the default
- real GitHub writes require explicit approval

## GitHub Role

GitHub stores work as reviewable artifacts:

- Issue body
- labels
- recommended branch
- acceptance criteria
- auto-start gate
- decision record link or pasted content

Example labels:

```text
context-capsule
handoff:ai_tool
risk:high
auto-start:blocked
needs-human-approval
```

## AI Tool Role

Claude, Codex, or ChatGPT should receive the generated handoff prompt, not the entire repository.

The handoff should include:

- task request
- relevant files
- risk findings
- forbidden rules
- approval checklist
- verification commands

The AI should first return:

```text
files to inspect
suspected cause
change plan
risk/impact
test plan
```

Direct edits should happen only after human approval for risky work.

## MVP Boundary

v0.1.0 includes:

- saved packet generation
- GitHub Issue dry-run/apply adapter
- release ZIP packaging

v0.2 includes:

- text-based Scrum Notes Mode
- text-based Project Kickoff Mode
- issue drafts from meeting notes
- team-lead safety notes
- no teammate scoring or automatic assignment

Not included yet:

- live Discord bot
- automatic Claude/Codex execution
- automatic PR creation
- automatic merge/deploy

## Next Implementation Step

Add a Discord input adapter in dry-run mode:

```text
pasted meeting text
-> extracted decision/task
-> Context Capsule packet
-> GitHub Issue dry-run
```
