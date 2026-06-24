# Vision

Context Capsule is a local-first work handoff system.

It turns vague human requests into reviewable work packets for AI coding tools, teammates, junior developers, and future-me.

## Product Thesis

AI coding work fails less when the handoff is explicit.

The core problem is usually not only retrieval. Real users do not write perfect prompts:

```text
리드미 손보자
깃헙 이슈 생성 안됨
로컬 실행 안돼
토큰 계산 뻥튀기 같은데?
auth는 건드리지 말고 문서만 바꾸자
이거 왜그래?
```

Context Capsule should not rush from vague input into repository search. It should first understand the request, then retrieve only useful context.

## Current Architecture Direction

```text
user phrasing
-> Request Understanding Layer
-> intent / target / protected-area normalization
-> task-aware retrieval
-> risk analysis
-> token budget estimate
-> AI / teammate / self handoff packet
-> GitHub Issue dry-run
```

## Request Understanding Layer

The Request Understanding Layer is now a first-class product layer.

It handles:

- colloquial Korean request normalization
- target file and work-area hints
- protected-area separation
- low-confidence clarification
- retrieval query construction

Examples:

| User Request | Interpreted As |
| --- | --- |
| `리드미 손보자` | `documentation_edit`, target `README.md` |
| `깃헙 이슈 생성 안됨` | GitHub issue adapter / CLI investigation |
| `로컬 실행 안돼` | local launcher and dashboard run flow |
| `토큰 계산 뻥튀기 같은데?` | token metric validation |
| `auth는 건드리지 말고 문서만 바꾸자` | docs target, `auth` protected |
| `이거 왜그래?` | clarification-only, no retrieval |

## Human-In-The-Loop Rule

Context Capsule should help a human decide what to do next.

It should not hide uncertainty.

Rules:

- If confidence is high, retrieve relevant files.
- If confidence is medium, show candidates and reasoning.
- If confidence is low, ask one clarification question.
- If a domain is protected, do not retrieve it as a work target.
- If indexed retrieval falls back, expose that in `retrieval_report`.
- If token usage is estimated, label it as estimated.

## Validation Philosophy

Validation should use real user phrasing, not only polished prompts.

Current user-speech QA checks:

- target file appears in top 1-3 or top 1-5
- protected domains are not treated as targets
- ambiguous requests stop before retrieval
- indexed fallback is visible
- token baseline scope stays honest

The generated report is:

```text
docs/reports/user_speech_retrieval_qa.md
```

## Roadmap

Detailed market-readiness path:

```text
docs/v1_roadmap.md
```

Commercialization and repository split:

```text
docs/commercialization_strategy.md
```

### v0.1.x Reliability

- keep expanding real user-speech aliases
- improve protected-area scope detection
- expose retrieval and request-understanding reasoning in saved packets
- keep token claims local and estimated unless provider usage is measured

### v0.2.x Collaboration Modes

- Scrum Notes Mode
- Project Kickoff Mode
- meeting notes to issue drafts
- team-lead direction and blocker summaries

### v0.3.x External Integrations

- Discord text input adapter
- GitHub Issue apply flow hardening
- Token-analyzer provider adapter when upstream API stabilizes

### v0.4.x Retrieval Backends

- Chroma / FAISS backend adapter
- incremental index refresh
- file-type aware chunking
- measured retrieval benchmark set

### v0.5.x Meeting-To-Execution

- Discord meeting decision capture
- human-approved issue creation
- optional AI handoff adapter
- no automatic merge or deploy

## One-Line Positioning

Context Capsule turns a rough "이거 해줘" into a scoped, reviewable, human-approved work packet.
