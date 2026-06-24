# Commercialization Strategy

This is a deferred future note.

Context Capsule is not currently focused on commercialization. The current focus is public beta development with KDT learner testing and feedback collection.

Active beta plan:

```text
docs/kdt_beta_test_plan.md
```

If commercialization becomes relevant later, this document can be used as a reference.

## Recommended Repository Split

```text
Public repository
  mosejong/context-capsule
  -> portfolio
  -> public local MVP
  -> release ZIP
  -> validation evidence
  -> learning and experimentation

Private repository
  context-capsule-pro / context-capsule-private / context-capsule-lab
  -> v0.2+ product experiments
  -> paid workflow features
  -> Discord/GitHub workflow integrations
  -> token measurement adapters
  -> pricing and license experiments
```

## Why Not Make Everything Private Now

The current public repository has portfolio value:

- README and product explanation
- GitHub Release ZIP
- local launcher flow
- tests and validation reports
- user-speech retrieval QA
- demo scripts and docs

Closing it would remove visible proof of execution.

Keeping every future feature public would expose product candidates too early.

The practical split is:

```text
v0.1.x public MVP stays public
v0.2+ product experiments move private when they become commercially sensitive
```

## Public MVP Positioning

Recommended README positioning:

```text
This repository is the public local MVP of Context Capsule.
Future workflow integrations and commercial product experiments may be developed separately.
```

Korean version:

```text
이 저장소는 Context Capsule의 공개 로컬 MVP입니다.
향후 Discord/GitHub workflow/Pro 기능은 별도 제품 실험으로 개발될 수 있습니다.
```

## License Strategy

Current public repository:

```text
MIT License
```

MIT is appropriate for a public portfolio MVP because it allows learning, experimentation, reuse, modification, distribution, and commercial use as long as the copyright and license notice are included.

Future private product repository:

```text
Proprietary / All rights reserved
```

Do not automatically copy the MIT license into a private commercial product repository unless that is an intentional business decision.

## Third-Party Dependency Check

Even if project code is original, runtime and dev dependencies are third-party open-source packages.

Current dependency groups:

| File | Purpose |
| --- | --- |
| `requirements.txt` | Streamlit, Pydantic, python-dotenv |
| `requirements-dev.txt` | pytest |
| `requirements-rag.txt` | optional Chroma, sentence-transformers, scikit-learn, numpy, pandas |
| `requirements-local-llm.txt` | optional local LLM adapters |

Before selling or bundling the product, confirm dependency licenses and redistribution rules.

## Public vs Private Feature Boundary

Keep public:

- v0.1.x local MVP
- README and demo explanation
- validation approach
- safe dry-run GitHub Issue adapter
- request-understanding examples
- local-first security model

Move private when commercially sensitive:

- Discord automation
- commercial workflow integrations
- Token-analyzer adapter if upstream licensing requires care
- paid templates/presets
- Claude/Codex execution adapters
- pricing/license logic
- product analytics

## Pricing Direction

Early pricing should match the product shape.

Possible path:

```text
Free public MVP
Personal local app: one-time purchase
Pro workflow integrations: subscription
Team workflow package: higher monthly plan
```

Why:

- A local app feels natural as a one-time purchase.
- Subscriptions become easier to justify when Discord, GitHub workflow, templates, updates, or team features are included.

## Deferred Checklist

- [x] Keep current public MVP repository open.
- [x] Confirm public repository has a LICENSE file.
- [x] Add public MVP/KDT beta positioning to README.
- [ ] Revisit private repository split only after beta feedback shows product value.
- [ ] Check dependency licenses before any commercial packaging.
- [ ] Define private repository license as proprietary/all-rights-reserved only if productized.

## One-Line Rule

```text
Public repo proves execution and gathers tester feedback. Commercialization waits.
```
