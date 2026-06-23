from __future__ import annotations

from datetime import datetime

from app.analyzers.risk_analyzer import analyze_risk, build_approval_checklist
from app.analyzers.token_analyzer import analyze_token_budget
from app.retrievers.hybrid_retriever import retrieve_hybrid_chunks
from app.retrievers.persistent_index import retrieve_indexed_chunks
from app.retrievers.simple_retriever import retrieve_relevant_chunks
from app.schemas.capsule_schema import (
    CapsuleInput,
    CapsuleOutput,
    HandoffSections,
    HandoffTarget,
    RepoChunk,
    RepoFile,
    RetrievalMode,
    RiskFinding,
    TokenBudget,
)


def generate_capsule(input_data: CapsuleInput, files: list[RepoFile]) -> CapsuleOutput:
    relevant_chunks = retrieve_chunks(
        files,
        input_data.task_request,
        input_data.top_k,
        input_data.repo_path,
        input_data.retriever_mode,
    )
    risk_findings = analyze_risk(input_data.task_request, relevant_chunks, input_data.forbidden_rules)
    approval_checklist = build_approval_checklist(risk_findings)
    project_summary = infer_project_summary(files)
    sections = build_handoff_sections(
        project_summary,
        input_data.task_request,
        relevant_chunks,
        risk_findings,
        approval_checklist,
    )
    handoff_prompt = select_handoff_prompt(sections, input_data.handoff_target)
    token_budget = analyze_token_budget(files, relevant_chunks, handoff_prompt)
    markdown = build_markdown(
        project_summary,
        input_data.task_request,
        relevant_chunks,
        risk_findings,
        approval_checklist,
        token_budget,
        sections,
        input_data.handoff_target,
        input_data.retriever_mode,
    )

    return CapsuleOutput(
        handoff_target=input_data.handoff_target,
        retriever_mode=input_data.retriever_mode,
        project_summary=project_summary,
        task_request=input_data.task_request,
        relevant_chunks=relevant_chunks,
        risk_findings=risk_findings,
        approval_checklist=approval_checklist,
        token_budget=token_budget,
        sections=sections,
        handoff_prompt=handoff_prompt,
        markdown=markdown,
    )


def retrieve_chunks(
    files: list[RepoFile],
    task_request: str,
    top_k: int,
    repo_path,
    retriever_mode: RetrievalMode,
) -> list[RepoChunk]:
    if retriever_mode == RetrievalMode.INDEXED:
        return retrieve_indexed_chunks(files, task_request, repo_path=repo_path, top_k=top_k)
    if retriever_mode == RetrievalMode.HYBRID:
        return retrieve_hybrid_chunks(files, task_request, top_k=top_k)
    return retrieve_relevant_chunks(files, task_request, top_k=top_k)


def infer_project_summary(files: list[RepoFile]) -> str:
    for file in files:
        if file.path.lower() == "readme.md":
            lines = [line.strip() for line in file.content.splitlines() if line.strip()]
            if len(lines) >= 2:
                return f"{lines[0].lstrip('# ').strip()} — {lines[1]}"
            if lines:
                return lines[0].lstrip("# ").strip()
    return "README를 찾지 못했습니다. 프로젝트 목적을 수동으로 확인해야 합니다."


def build_handoff_sections(
    project_summary: str,
    task_request: str,
    chunks: list[RepoChunk],
    risk_findings: list[RiskFinding],
    checklist: list[str],
) -> HandoffSections:
    return HandoffSections(
        overview=build_overview(project_summary, task_request, chunks),
        future_me_letter=build_self_handoff(task_request, chunks, risk_findings, checklist),
        teammate_brief=build_teammate_brief(task_request, chunks, risk_findings, checklist, junior=False),
        junior_guide=build_teammate_brief(task_request, chunks, risk_findings, checklist, junior=True),
        ai_handoff_prompt=build_ai_handoff_prompt(task_request, chunks, risk_findings, checklist),
        risk_checklist=build_risk_checklist(risk_findings, checklist),
    )


def select_handoff_prompt(sections: HandoffSections, handoff_target: HandoffTarget) -> str:
    if handoff_target == HandoffTarget.TEAMMATE:
        return sections.teammate_brief
    if handoff_target == HandoffTarget.JUNIOR_DEVELOPER:
        return sections.junior_guide
    if handoff_target == HandoffTarget.FUTURE_ME:
        return sections.future_me_letter
    return sections.ai_handoff_prompt


def build_overview(project_summary: str, task_request: str, chunks: list[RepoChunk]) -> str:
    paths = "\n".join(f"- `{chunk.path}:{chunk.start_line}-{chunk.end_line}`" for chunk in chunks)
    return "\n".join(
        [
            "## 프로젝트",
            project_summary,
            "",
            "## 작업 요청",
            task_request,
            "",
            "## 먼저 볼 컨텍스트",
            paths if paths else "- 검색된 컨텍스트 없음",
        ]
    )


def build_ai_handoff_prompt(
    task_request: str,
    chunks: list[RepoChunk],
    risk_findings: list[RiskFinding],
    checklist: list[str],
) -> str:
    context_lines = []
    for index, chunk in enumerate(chunks, start=1):
        location = f"{chunk.path}:{chunk.start_line}-{chunk.end_line}"
        context_lines.append(f"[{index}] {location}\n{chunk.text[:1200]}")

    risk_lines = [
        f"- {item.kind.value} / {item.level.value}: {item.reason} ({item.path or item.evidence or 'task'})"
        for item in risk_findings
    ]
    checklist_lines = [f"- [ ] {item}" for item in checklist]

    return "\n".join(
        [
            "당신은 사용자의 승인 없이 코드를 직접 수정하지 않는 AI 코딩 어시스턴트입니다.",
            "아래 작업 범위 안에서만 분석하고, 변경 전 반드시 영향도와 수정 후보를 먼저 설명하세요.",
            "",
            "## 작업 요청",
            task_request,
            "",
            "## 관련 컨텍스트",
            "\n\n".join(context_lines) if context_lines else "관련 컨텍스트를 찾지 못했습니다.",
            "",
            "## 위험 신호",
            "\n".join(risk_lines) if risk_lines else "- 특별한 위험 신호 없음",
            "",
            "## 사람 승인 체크리스트",
            "\n".join(checklist_lines),
            "",
            "## 응답 규칙",
            "1. 수정 대상 파일을 먼저 나열하세요.",
            "2. 예상 영향도를 설명하세요.",
            "3. 위험도가 높은 변경은 대안을 먼저 제안하세요.",
            "4. 사용자가 YES라고 하기 전까지 직접 적용하지 마세요.",
        ]
    )


def build_teammate_brief(
    task_request: str,
    chunks: list[RepoChunk],
    risk_findings: list[RiskFinding],
    checklist: list[str],
    junior: bool,
) -> str:
    file_lines = [f"- `{chunk.path}`: {chunk.text[:180].replace(chr(10), ' ')}" for chunk in chunks]
    risk_lines = [
        f"- {item.kind.value} / {item.level.value}: {item.reason} ({item.path or item.evidence or 'task'})"
        for item in risk_findings
    ]
    checklist_lines = [f"- [ ] {item}" for item in checklist]
    tone = "주니어 개발자가 바로 시작할 수 있도록 작은 단계로 쪼개세요." if junior else "팀원이 오늘 바로 시작할 수 있는 단위로 정리하세요."

    return "\n".join(
        [
            tone,
            "압박하는 문장이 아니라, 시작점과 완료 기준을 명확히 전달하는 브리프를 작성하세요.",
            "",
            "## 작업 목표",
            task_request,
            "",
            "## 먼저 볼 파일",
            "\n".join(file_lines) if file_lines else "- 관련 파일을 찾지 못했습니다.",
            "",
            "## 오늘 할 일",
            "1. 먼저 볼 파일을 열고 현재 흐름을 확인합니다.",
            "2. 작업 요청과 직접 관련 있는 함수, 라우터, 설정만 표시합니다.",
            "3. 변경이 필요한 부분과 확인만 필요한 부분을 나눕니다.",
            "4. 코드 변경 전 모호한 부분을 질문합니다.",
            "",
            "## 완료 기준",
            "- 작업 요청과 직접 관련된 범위만 다룹니다.",
            "- 변경 파일과 확인 파일을 구분해서 보고합니다.",
            "- 실행 또는 테스트로 확인한 결과를 남깁니다.",
            "",
            "## 질문해야 할 것",
            "- DB/API/인증/배포 동작을 바꿔도 되는지 확인이 필요한가?",
            "- 완료 기준이 화면 변화인지, 테스트 통과인지, 문서 정리인지 명확한가?",
            "- 금지 파일이나 건드리면 안 되는 흐름이 있는가?",
            "",
            "## 위험 신호",
            "\n".join(risk_lines) if risk_lines else "- 특별한 위험 신호 없음",
            "",
            "## 확인 체크리스트",
            "\n".join(checklist_lines),
        ]
    )


def build_self_handoff(
    task_request: str,
    chunks: list[RepoChunk],
    risk_findings: list[RiskFinding],
    checklist: list[str],
) -> str:
    file_lines = [f"- `{chunk.path}:{chunk.start_line}-{chunk.end_line}`" for chunk in chunks]
    risk_lines = [
        f"- {item.kind.value} / {item.level.value}: {item.reason} ({item.path or item.evidence or 'task'})"
        for item in risk_findings
    ]
    checklist_lines = [f"- [ ] {item}" for item in checklist]

    return "\n".join(
        [
            "내일 이어서 작업할 수 있도록 현재 맥락을 짧고 구체적으로 남깁니다.",
            "",
            "## 현재 작업",
            task_request,
            "",
            "## 이어서 볼 파일",
            "\n".join(file_lines) if file_lines else "- 관련 파일을 찾지 못했습니다.",
            "",
            "## 현재까지 파악한 점",
            "- 검색된 파일과 위험 신호를 기준으로 작업 범위를 좁혀야 합니다.",
            "- 추정과 확인된 사실을 구분해서 다음 작업 전에 다시 확인합니다.",
            "",
            "## 다음 작업",
            "1. 이어서 볼 파일을 먼저 엽니다.",
            "2. 위험 신호가 있는 변경은 적용 전에 영향도를 정리합니다.",
            "3. 변경 후 실행 명령이나 테스트 결과를 기록합니다.",
            "",
            "## 주의사항",
            "\n".join(risk_lines) if risk_lines else "- 특별한 위험 신호 없음",
            "",
            "## 내일 확인 체크리스트",
            "\n".join(checklist_lines),
        ]
    )


def target_label(handoff_target: HandoffTarget) -> str:
    labels = {
        HandoffTarget.AI_TOOL: "AI Handoff Prompt",
        HandoffTarget.TEAMMATE: "Teammate Brief",
        HandoffTarget.JUNIOR_DEVELOPER: "Junior Developer Brief",
        HandoffTarget.FUTURE_ME: "Self Handoff",
    }
    return labels[handoff_target]


def build_risk_checklist(risk_findings: list[RiskFinding], checklist: list[str]) -> str:
    risk_lines = [
        f"- **{item.kind.value} / {item.level.value}** — {item.reason} / `{item.path or item.evidence or 'task'}`"
        for item in risk_findings
    ]
    checklist_lines = [f"- [ ] {item}" for item in checklist]
    return "\n".join(
        [
            "## Risk Findings",
            "\n".join(risk_lines) if risk_lines else "- 특별한 위험 신호 없음",
            "",
            "## Human Approval Checklist",
            "\n".join(checklist_lines),
        ]
    )


def build_markdown(
    project_summary,
    task_request,
    chunks,
    risk_findings,
    checklist,
    token_budget: TokenBudget,
    sections: HandoffSections,
    handoff_target: HandoffTarget,
    retriever_mode: RetrievalMode,
) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chunk_lines = []
    for chunk in chunks:
        location = f"{chunk.path}:{chunk.start_line}-{chunk.end_line}"
        chunk_lines.append(f"- `{location}` — score {chunk.score:.2f}")

    risk_lines = [
        f"- **{item.kind.value} / {item.level.value}** — {item.reason} / `{item.path or item.evidence or 'task'}`"
        for item in risk_findings
    ]
    checklist_lines = [f"- [ ] {item}" for item in checklist]
    handoff_prompt = select_handoff_prompt(sections, handoff_target)

    return f"""# Context Capsule

Generated at: {generated_at}

## Project Summary

{project_summary}

## Task Request

{task_request}

## Handoff Target

{handoff_target.value}

## Retriever Mode

{retriever_mode.value}

## Retrieved Context

{chr(10).join(chunk_lines) if chunk_lines else '- 관련 컨텍스트 없음'}

## Token Budget

- Candidate file context estimate: {token_budget.raw_context_tokens:,} tokens
- Retrieved context estimate: {token_budget.retrieved_context_tokens:,} tokens
- Handoff prompt estimate: {token_budget.handoff_prompt_tokens:,} tokens
- Estimated reduction: {token_budget.estimated_reduction_percent:.1f}%
- Method: {token_budget.method}
- Baseline scope: {token_budget.baseline_context_scope}
- Verification status: {token_budget.verification_status}
- Actual provider usage: {token_budget.actual_provider_usage}

## Risk Findings

{chr(10).join(risk_lines) if risk_lines else '- 특별한 위험 신호 없음'}

## Human Approval Checklist

{chr(10).join(checklist_lines)}

## {target_label(handoff_target)}

```text
{handoff_prompt}
```

## Structured Outputs

### Overview

{sections.overview}

### Future Me

{sections.future_me_letter}

### Teammate Brief

{sections.teammate_brief}

### Junior Guide

{sections.junior_guide}

### AI Handoff Prompt

```text
{sections.ai_handoff_prompt}
```
"""
