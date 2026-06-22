from __future__ import annotations

from pathlib import Path

import streamlit as st

from app.analyzers.chat_analyzer import extract_task_request
from app.generators.capsule_generator import generate_capsule
from app.generators.execution_packet_generator import build_execution_packet
from app.scanners.repo_scanner import scan_repo
from app.schemas.capsule_schema import CapsuleInput, HandoffTarget

st.set_page_config(page_title="Context Capsule", page_icon="🧩", layout="wide")

st.title("🧩 Context Capsule")
st.caption("RAG 기반 AI 코딩 작업 인수인계 패킷 생성 도구")

with st.sidebar:
    st.header("Input")
    repo_path = st.text_input("Local repository path", value=".")
    top_k = st.slider("Retrieved chunks", min_value=3, max_value=20, value=8)
    handoff_target = st.selectbox(
        "Handoff target",
        options=list(HandoffTarget),
        format_func=lambda item: item.value,
        index=0,
    )
    input_mode = st.radio(
        "Input mode",
        options=["Direct task request", "Chat / error log"],
        index=0,
    )

task_request = ""
if input_mode == "Chat / error log":
    st.subheader("대화 / 에러 로그")
    chat_log = st.text_area(
        "Discord, GPT 대화, 에러 로그를 붙여넣으면 작업 요청으로 정리합니다.",
        value=(
            "모세종 — 이거 토큰 분석기 붙이고 싶음\n"
            "496 — 어디에 붙일건데요?\n"
            "모세종 — app/generators/capsule_generator.py 쪽에 붙이고 Streamlit에서 보여주자\n"
            "모세종 — 이걸로 가자"
        ),
        height=170,
    )
    extraction = extract_task_request(chat_log)
    task_request = extraction.task_request

    st.markdown("### Extracted Task Request")
    st.code(task_request, language="markdown")
    st.caption(f"Extraction confidence: {extraction.confidence:.2f}")
    if extraction.detected_paths:
        st.markdown("Detected paths: " + ", ".join(f"`{path}`" for path in extraction.detected_paths))
    if extraction.error_hints:
        with st.expander("Error hints"):
            for hint in extraction.error_hints:
                st.markdown(f"- {hint}")
    if extraction.decision_hints:
        with st.expander("Decision hints"):
            for hint in extraction.decision_hints:
                st.markdown(f"- {hint}")
else:
    st.subheader("작업 요청")
    task_request = st.text_area(
        "AI 코딩 도구에게 넘기기 전, 어떤 작업을 하려는지 적어주세요.",
        value="README를 포트폴리오용으로 다듬고, 위험한 코드 변경은 하지 않게 작업 브리프를 만들어줘.",
        height=110,
    )

st.subheader("금지/주의 규칙")
forbidden_text = st.text_area(
    "한 줄에 하나씩 적어주세요.",
    value="새 브랜치 만들지 말 것\nDB 스키마 변경 전 반드시 확인\n환경변수와 secret 값 수정 금지\n자동 적용하지 말고 수정안만 제안",
    height=130,
)

if st.button("Generate Capsule", type="primary"):
    try:
        rules = [line.strip() for line in forbidden_text.splitlines() if line.strip()]
        input_data = CapsuleInput(
            repo_path=Path(repo_path),
            task_request=task_request,
            forbidden_rules=rules,
            top_k=top_k,
            handoff_target=handoff_target,
        )
        files = scan_repo(input_data.repo_path)
        output = generate_capsule(input_data, files)
        execution_packet = build_execution_packet(output)

        st.success(f"Scanned {len(files)} files and generated {output.handoff_target.value} capsule.")

        tabs = st.tabs(
            [
                "Overview",
                "내일의 나에게",
                "팀원 작업 가이드",
                "Junior Guide",
                "AI Handoff Prompt",
                "Risk & Approval",
                "GitHub Issue Packet",
            ]
        )

        with tabs[0]:
            st.markdown("### Overview")
            st.markdown(output.sections.overview)

            if execution_packet.auto_start_allowed:
                st.success("Auto-start gate: allowed. HIGH/BLOCKED 위험 신호가 없습니다.")
            else:
                st.warning(f"Auto-start gate: blocked. {execution_packet.block_reason}")

            st.markdown("#### Token Budget")
            budget_col1, budget_col2, budget_col3, budget_col4 = st.columns(4)
            budget_col1.metric("Raw context", f"{output.token_budget.raw_context_tokens:,}")
            budget_col2.metric("Retrieved", f"{output.token_budget.retrieved_context_tokens:,}")
            budget_col3.metric("Handoff prompt", f"{output.token_budget.handoff_prompt_tokens:,}")
            budget_col4.metric("Reduction", f"{output.token_budget.estimated_reduction_percent:.1f}%")
            st.caption(
                f"Method: {output.token_budget.method} · "
                f"Verification status: {output.token_budget.verification_status} · "
                f"Actual provider usage: {output.token_budget.actual_provider_usage}"
            )

        with tabs[1]:
            st.markdown("### 내일의 나에게")
            st.markdown(output.sections.future_me_letter)

        with tabs[2]:
            st.markdown("### 팀원 작업 가이드")
            st.markdown(output.sections.teammate_brief)

        with tabs[3]:
            st.markdown("### Junior Guide")
            st.markdown(output.sections.junior_guide)

        with tabs[4]:
            st.markdown("### AI Handoff Prompt")
            st.caption("Claude, Codex, ChatGPT에 복사해서 넘기는 프롬프트입니다.")
            st.code(output.sections.ai_handoff_prompt, language="text")
            st.download_button(
                label="Download ai_handoff_prompt.txt",
                data=output.sections.ai_handoff_prompt,
                file_name="ai_handoff_prompt.txt",
                mime="text/plain",
                key="download_ai_handoff_prompt",
            )

        with tabs[5]:
            st.markdown("### Risk & Approval")
            st.markdown(output.sections.risk_checklist)
            left, right = st.columns([1, 1])
            with left:
                st.markdown("#### Retrieved Context")
                for chunk in output.relevant_chunks:
                    st.markdown(f"- `{chunk.path}:{chunk.start_line}-{chunk.end_line}` · score `{chunk.score:.2f}`")

                st.markdown("#### Risk Findings")
                if output.risk_findings:
                    for finding in output.risk_findings:
                        st.markdown(
                            f"- **{finding.kind.value} / {finding.level.value}** — {finding.reason} / "
                            f"`{finding.path or finding.evidence or 'task'}`"
                        )
                else:
                    st.markdown("- 특별한 위험 신호 없음")

            with right:
                st.markdown("#### Human Approval Checklist")
                for index, item in enumerate(output.approval_checklist):
                    st.checkbox(item, value=False, key=f"developer_checklist_{index}")

        with tabs[6]:
            st.markdown("### GitHub Issue Packet")
            st.markdown(f"**Issue Title:** {execution_packet.title}")
            st.markdown(f"**Recommended Branch:** `{execution_packet.recommended_branch}`")
            st.code(execution_packet.issue_body, language="markdown")
            st.download_button(
                label="Download execution_packet.md",
                data=execution_packet.issue_body,
                file_name="execution_packet.md",
                mime="text/markdown",
                key="download_execution_packet",
            )

            st.markdown("#### Capsule Markdown")
            st.code(output.markdown, language="markdown")
            st.download_button(
                label="Download capsule.md",
                data=output.markdown,
                file_name="context_capsule.md",
                mime="text/markdown",
                key="download_capsule",
            )

            with st.expander("Decision Record"):
                st.code(execution_packet.decision_record, language="markdown")
    except Exception as exc:  # pragma: no cover - Streamlit UI guard
        st.error(str(exc))
