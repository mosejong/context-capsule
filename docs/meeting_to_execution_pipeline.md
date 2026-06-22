# Meeting-to-Execution Pipeline

이 문서는 Context Capsule의 확장 비전인 `회의 결정 -> 작업 착수` 흐름을 정리한다.

핵심 문장:

> 회의에서 나온 "이걸로 가자"를 GitHub Issue, 작업 브리프, AI handoff prompt, 위험 체크리스트로 바꿔 바로 실행 가능한 작업 패킷을 만든다.

## 1. Why This Matters

아이디어 회의는 자주 열리지만, 결정이 실제 작업으로 바뀌는 과정에서 맥락이 사라진다.

반복되는 문제:

- 아이디어는 나왔지만 담당자가 뭘 해야 할지 모른다.
- 결정은 됐지만 GitHub Issue나 작업 카드가 없다.
- AI에게 시키려 해도 레포 맥락과 금지사항 설명이 다시 필요하다.
- 팀장이 매번 작업을 쪼개고 완료 기준을 써줘야 한다.
- 회의 대화가 Discord에 남아도 실행 가능한 작업 단위로 정리되지 않는다.

Context Capsule은 이 문제를 `회의 결정의 실행 패킷화` 문제로 본다.

## 2. Product Flow

```text
Discord idea meeting
        ↓
Idea fixed by command or reaction
        ↓
Decision record generated
        ↓
Repo context retrieval
        ↓
Risk and token budget analysis
        ↓
GitHub Issue / teammate brief / AI handoff prompt
        ↓
Human approval
        ↓
Claude / Codex / teammate starts work
```

The important rule:

> 자동 착수는 가능하지만 자동 merge는 하지 않는다.

## 3. Automation Levels

| Level | Name | What happens | Approval |
| --- | --- | --- | --- |
| 1 | Auto organize | 회의 결정 요약, Decision Record 생성 | 필요 없음 |
| 2 | Auto prepare | 관련 파일 검색, 위험도 분석, Issue/brief 생성 | 필요 없음 |
| 3 | Approved start | Claude/Codex/팀원에게 작업 패킷 전달 | 필요 |
| 4 | Manual merge | diff 확인, 테스트 결과 확인, merge 결정 | 반드시 필요 |

이 구조를 쓰면 프로젝트의 human-in-the-loop 원칙을 유지하면서도 회의 후 작업 착수 속도를 올릴 수 있다.

## 4. Discord Bot Role

Discord bot은 단순 알림봇이 아니라 회의 결정 수집기가 된다.

초기 명령어 후보:

```text
/idea      회의 중 나온 아이디어를 임시 저장
/fix       확정된 아이디어를 작업 단위로 변환
/brief     AI/팀원/미래의 나용 브리프 생성
/risk      위험도 분석
/start     승인된 작업을 GitHub Issue 또는 AI adapter로 전달
```

MVP에서는 slash command와 message command를 우선 검토한다.

주의:

- Discord interaction은 빠르게 응답해야 하므로 긴 repo scan은 비동기로 처리한다.
- bot token, webhook secret, repository token은 절대 capsule 본문에 출력하지 않는다.
- Discord 원문 전체를 외부 LLM API로 보내지 않고 먼저 로컬에서 task 후보만 추출한다.

## 5. GitHub Role

GitHub에는 휘발되지 않는 작업 기록을 남긴다.

생성 후보:

```text
GitHub Issue
Decision Record markdown
AI handoff prompt
Teammate brief
Risk checklist
Token budget report
```

Issue body 예시:

```md
# Add teammate brief mode

## Decision
회의에서 teammate brief mode를 Phase 2 핵심 기능으로 확정했다.

## Work Scope
- handoff_target schema 확장
- teammate template 추가
- Streamlit target selector 추가
- 테스트 케이스 추가

## Risk
MEDIUM

## Approval Rule
코드 수정 전 변경 파일과 예상 영향도를 먼저 보고한다.
```

## 6. Claude / Codex Connection

처음부터 Claude/Codex를 직접 조종하지 않는다.

안전한 순서:

1. Discord decision을 정리한다.
2. GitHub Issue를 만든다.
3. Context Capsule brief를 Issue에 첨부한다.
4. 사용자가 승인한다.
5. 승인 후 Claude/Codex adapter가 작업을 시작한다.

Adapter 후보:

```text
Claude Code adapter
Codex adapter
GitHub Issue adapter
Local CLI adapter
```

초기 MVP에서는 `실행 가능한 패킷 생성`까지가 목표다. 실제 AI 실행은 후속 단계에서 붙인다.

## 7. Safety Rules

자동 작업 착수 전에 반드시 지킬 규칙:

1. secret/env/credential은 redaction 후 처리한다.
2. HIGH/BLOCKED risk는 자동 착수하지 않는다.
3. DB schema, auth, deploy 변경은 approval_required로 표시한다.
4. AI adapter는 새 branch, patch, draft PR까지만 허용한다.
5. merge, production deploy, credential 변경은 사람이 직접 한다.
6. 모든 자동 실행에는 원본 Discord message ID와 GitHub Issue 링크를 남긴다.

## 8. Prototype Scope

Phase 1:

- Discord 대화 붙여넣기 기반 `Chat-to-Capsule`
- `/fix` 명령어 없이 수동 입력으로 decision text 테스트
- GitHub Issue body markdown 생성
- Status: implemented in MVP

Phase 2:

- Discord bot slash command prototype
- idea/fix/brief command
- 비동기 job queue 또는 local background task

Phase 3:

- GitHub Issue 생성 adapter
- Claude/Codex handoff prompt attachment
- approval gate

Phase 4:

- Claude/Codex adapter 실험
- branch/draft PR 생성 흐름 검토
- execution metrics 저장

## 9. Success Metrics

```text
meeting_to_issue_time_seconds
decision_to_brief_time_seconds
related_file_hit_rate
risk_recall
forbidden_rule_retention
token_reduction_percent
human_approval_required_count
auto_start_blocked_by_risk_count
```

좋은 포트폴리오 문장:

> Discord 회의에서 확정된 아이디어를 평균 X초 안에 GitHub Issue와 AI handoff prompt로 변환하고, 위험 변경은 자동 착수 전에 차단했다.

## 10. Sources

- Discord application commands: https://discord.com/developers/docs/interactions/application-commands
- Discord receiving/responding to interactions: https://discord.com/developers/docs/interactions/receiving-and-responding
- Discord webhooks: https://discord.com/developers/docs/resources/webhook
- Anthropic Claude Code SDK: https://docs.anthropic.com/en/docs/claude-code/sdk
- Anthropic Claude Code GitHub Actions: https://docs.anthropic.com/en/docs/claude-code/github-actions
- OpenAI Codex docs: https://developers.openai.com/codex
- OpenAI Codex GitHub Action docs: https://developers.openai.com/codex/github-action
