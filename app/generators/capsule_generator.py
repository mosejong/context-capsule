from __future__ import annotations

from datetime import datetime

from app.analyzers.risk_analyzer import analyze_risk, build_approval_checklist
from app.retrievers.simple_retriever import retrieve_relevant_chunks
from app.schemas.capsule_schema import CapsuleInput, CapsuleOutput, RepoFile


def generate_capsule(input_data: CapsuleInput, files: list[RepoFile]) -> CapsuleOutput:
    relevant_chunks = retrieve_relevant_chunks(files, input_data.task_request, top_k=input_data.top_k)
    risk_findings = analyze_risk(input_data.task_request, relevant_chunks, input_data.forbidden_rules)
    approval_checklist = build_approval_checklist(risk_findings)
    project_summary = infer_project_summary(files)
    handoff_prompt = build_handoff_prompt(input_data.task_request, relevant_chunks, risk_findings, approval_checklist)
    markdown = build_markdown(project_summary, input_data.task_request, relevant_chunks, risk_findings, approval_checklist, handoff_prompt)

    return CapsuleOutput(
        project_summary=project_summary,
        task_request=input_data.task_request,
        relevant_chunks=relevant_chunks,
        risk_findings=risk_findings,
        approval_checklist=approval_checklist,
        handoff_prompt=handoff_prompt,
        markdown=markdown,
    )


def infer_project_summary(files: list[RepoFile]) -> str:
    for file in files:
        if file.path.lower() == "readme.md":
            lines = [line.strip() for line in file.content.splitlines() if line.strip()]
            if len(lines) >= 2:
                return f"{lines[0].lstrip('# ').strip()} — {lines[1]}"
            if lines:
                return lines[0].lstrip("# ").strip()
    return "README를 찾지 못했습니다. 프로젝트 목적을 수동으로 확인해야 합니다."


def build_handoff_prompt(task_request, chunks, risk_findings, checklist) -> str:
    context_lines = []
    for index, chunk in enumerate(chunks, start=1):
        location = f"{chunk.path}:{chunk.start_line}-{chunk.end_line}"
        context_lines.append(f"[{index}] {location}\n{chunk.text[:1200]}")

    risk_lines = [f"- {item.level}: {item.reason} ({item.path or item.evidence or 'task'})" for item in risk_findings]
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


def build_markdown(project_summary, task_request, chunks, risk_findings, checklist, handoff_prompt) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chunk_lines = []
    for chunk in chunks:
        location = f"{chunk.path}:{chunk.start_line}-{chunk.end_line}"
        chunk_lines.append(f"- `{location}` — score {chunk.score:.2f}")

    risk_lines = [f"- **{item.level}** — {item.reason} / `{item.path or item.evidence or 'task'}`" for item in risk_findings]
    checklist_lines = [f"- [ ] {item}" for item in checklist]

    return f"""# Context Capsule

Generated at: {generated_at}

## Project Summary

{project_summary}

## Task Request

{task_request}

## Retrieved Context

{chr(10).join(chunk_lines) if chunk_lines else '- 관련 컨텍스트 없음'}

## Risk Findings

{chr(10).join(risk_lines) if risk_lines else '- 특별한 위험 신호 없음'}

## Human Approval Checklist

{chr(10).join(checklist_lines)}

## AI Handoff Prompt

```text
{handoff_prompt}
```
"""
