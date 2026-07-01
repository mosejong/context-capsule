# Request Understanding Layer

Context Capsule v0.1.2 adds a local Request Understanding Layer before retrieval.

The goal is to handle real user phrasing before searching the repository:

```text
사용자 말투
-> intent normalization
-> target/protected hint extraction
-> clarification gate when confidence is low
-> retrieval query
-> risk analysis and handoff packet
```

## Why It Exists

Users rarely write perfect task requests.

Examples:

```text
리드미 손보자
심플 리트리버 왜 이럼
깃헙 이슈 생성 안됨
로컬 실행 안돼
토큰 계산 뻥튀기 같은데?
auth는 건드리지 말고 문서만 바꾸자
이거 왜그래?
```

If Context Capsule searches these phrases directly, it can miss target files, retrieve protected files, or waste tokens on unclear work.

## What It Extracts

- `intent`: documentation edit, bug investigation, metric validation, launcher bug, retrieval change, and similar task types
- `target_hints`: likely work areas
- `file_hints`: likely files to retrieve
- `protected_hints`: areas the user explicitly said not to touch
- `search_query`: retrieval query with protected areas removed
- `confidence`: high, medium, or low
- `clarification_question`: one question when the target is too unclear

## Safety Rule

If confidence is low, Context Capsule does not retrieve repository context.

Instead it returns a clarification-only packet:

```text
대상 파일, 기능명, 또는 오류 로그 중 하나를 알려주세요.
```

This is part of token control. Asking one question is cheaper and safer than searching the whole repository for "이거 왜그래?"

## Protected Area Example

Input:

```text
auth는 건드리지 말고 문서만 바꾸자
```

Interpretation:

```text
intent: documentation_edit
protected_hints: auth
file_hints: README.md, docs/*
search_query: documentation targets only
```

The protected area is passed into risk analysis as a forbidden rule, but it is not treated as a retrieval target.

## Validation Set

Current QA uses real Korean colloquial requests:

```text
리드미 손보자
README 포폴용으로 다듬자
심플 리트리버 왜 이럼
simple_retriever에 벡터 검색 추가
깃헙 이슈 생성 안됨
로컬 실행 안돼
토큰 계산 뻥튀기 같은데?
auth는 건드리지 말고 문서만 바꾸자
DB쪽은 냅두고 출력 문구만 바꾸자
이거 왜그래?
아까 그거 이어서 하자
```

PASS criteria:

- target file appears in top 1-3 for direct requests
- multi-file adapters appear in top 1-5
- protected domains are not retrieved as targets
- ambiguous requests ask one clarification question
- `baseline_context_scope` remains `retrieved_file_contents`
- indexed fallback is visible through `retrieval_report`
