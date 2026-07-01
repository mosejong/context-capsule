# Target Positioning

Context Capsule is not a general prompt generator and not an autonomous coding agent.

It is a local work-preparation tool for junior developers who want to use AI coding tools with clearer scope, safer boundaries, and better evidence.

## Core Position

```text
AI에게 일을 맡기기 전에
무엇을 봐야 하는지,
무엇을 건드리면 안 되는지,
어떤 결과가 나오면 끝난 건지
정리해주는 도구
```

Short version:

```text
AI가 아무 파일이나 보고 아무렇게나 고치지 않게,
사람이 먼저 작업 범위를 정리해주는 도구
```

## Primary User

### Junior Developers

Context Capsule is mainly for new developers who:

- are unsure which files to show Claude, Codex, or ChatGPT
- need help turning rough requests into concrete work scope
- want to avoid accidentally touching auth, DB, env, deployment, or secrets
- need README, issue draft, meeting notes, or handoff summaries for team projects
- want an AI prompt that includes relevant files, forbidden areas, and verification steps

## Secondary Reader

### Team Leads, Interviewers, and AI Beginners

The explanation must also make sense to people who:

- do not use AI coding tools deeply
- need to evaluate whether a junior developer can define work clearly
- care more about risk control and verification than about AI buzzwords
- want to see a portfolio project with user feedback, tests, release notes, and safety boundaries

This is why the user-facing UI prefers:

| Technical phrase | User-facing phrase |
| --- | --- |
| LLM | AI |
| prompt | 지시문 |
| context | 참고할 내용 |
| token | 사용량 / 예상 사용량 |
| handoff prompt | AI에게 넘길 지시문 |
| packet | 작업 정리본 |
| repository | 프로젝트 폴더 |

Technical terms can still appear in developer architecture docs, but they should not dominate the first screen or first README section.

## What It Should Not Become Yet

These ideas are useful but out of scope for the current product line:

- image generation prompt hub
- all-purpose prompt generator
- realtime meeting recording
- realtime STT
- Discord/Zoom automation
- automatic teammate scoring
- automatic role assignment
- automatic code modification

## Roadmap Boundary

### v0.2.x

- text-based work request summaries
- README / docs / meeting text summary generation
- explicit file-scope constraints
- beginner-friendly UI wording
- beta feedback loop

### v0.3.x

- stronger meeting text paste workflow
- audio file upload -> STT -> meeting summary experiment
- stronger extraction of deadlines, follow-up messages, and role-discussion questions

### v0.4.x

- Discord / Zoom / collaboration log integration review
- team project history to work brief generation

### v0.5.x

- realtime recording/STT review only after privacy, consent, storage, cost, and performance are designed

### Later

- image-generation prompt helpers
- presentation prompt helpers
- AI work-instruction template hub

These later ideas should not weaken the current core message: Context Capsule prepares safer AI coding handoffs.
