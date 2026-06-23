from __future__ import annotations

from pathlib import Path

import streamlit as st

from app.analyzers.chat_analyzer import extract_task_request
from app.generators.output_writer import save_output_packet
from app.services.capsule_service import generate_capsule_result
from app.schemas.capsule_schema import CapsuleOutput, ExecutionPacket, HandoffTarget

st.set_page_config(page_title="Context Capsule", page_icon="CC", layout="wide")

st.title("Context Capsule")
st.caption("레포와 작업 요청을 실제 착수 가능한 handoff packet으로 바꾸는 로컬 우선 개발 보조 도구")


def generate_result(
    repo_path: str,
    task_request: str,
    forbidden_text: str,
    top_k: int,
    handoff_target: HandoffTarget,
) -> tuple[CapsuleOutput, ExecutionPacket, int]:
    rules = [line.strip() for line in forbidden_text.splitlines() if line.strip()]
    result = generate_capsule_result(
        repo_path=Path(repo_path),
        task_request=task_request,
        forbidden_rules=rules,
        top_k=top_k,
        handoff_target=handoff_target,
    )
    return result.capsule, result.execution_packet, result.scanned_file_count


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
    st.subheader("Chat / Error Log")
    chat_log = st.text_area(
        "Discord, GPT 대화, 에러 로그를 붙여넣으면 작업 요청으로 정리합니다.",
        value=(
            "모세종: 토큰 분석기 붙이고 싶음\n"
            "496: 어디에 붙일 건데요?\n"
            "모세종: app/generators/capsule_generator.py 쪽에 붙이고 Streamlit에서 보여주자\n"
            "모세종: 이걸로 가자"
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
        "AI 코딩 도구, 팀원, 미래의 나에게 넘길 작업을 적어주세요.",
        value="README를 포트폴리오용으로 다듬되, 위험한 코드 변경은 하지 않게 작업 브리프를 만들어줘.",
        height=110,
    )

st.subheader("금지 / 주의 규칙")
forbidden_text = st.text_area(
    "한 줄에 하나씩 적어주세요.",
    value=(
        "새 브랜치 만들지 말 것\n"
        "DB 스키마 변경 전 반드시 확인\n"
        "환경변수와 secret 값 수정 금지\n"
        "자동 적용하지 말고 수정안만 제안"
    ),
    height=130,
)

if st.button("Generate Capsule", type="primary"):
    try:
        output, execution_packet, scanned_count = generate_result(
            repo_path,
            task_request,
            forbidden_text,
            top_k,
            handoff_target,
        )
        st.session_state["capsule_output"] = output
        st.session_state["execution_packet"] = execution_packet
        st.session_state["scanned_count"] = scanned_count
        st.session_state.pop("saved_output_dir", None)
        st.success(f"Scanned {scanned_count} files and generated {output.handoff_target.value} capsule.")
    except Exception as exc:  # pragma: no cover - Streamlit UI guard
        st.error(str(exc))

output = st.session_state.get("capsule_output")
execution_packet = st.session_state.get("execution_packet")

if output and execution_packet:
    tabs = st.tabs(
        [
            "Overview",
            "내일의 나에게",
            "팀원 작업 가이드",
            "Junior Guide",
            "AI Handoff Prompt",
            "Risk & Approval",
            "GitHub Issue Packet",
            "Saved Packet",
        ]
    )

    with tabs[0]:
        st.markdown("### Overview")
        st.markdown(output.sections.overview)

        if execution_packet.auto_start_allowed:
            st.success("Auto-start gate: allowed. HIGH/BLOCKED change risk가 없습니다.")
        else:
            st.warning(f"Auto-start gate: blocked. {execution_packet.block_reason}")

        st.markdown("#### Token Budget")
        budget_col1, budget_col2, budget_col3, budget_col4 = st.columns(4)
        budget_col1.metric("Raw context", f"{output.token_budget.raw_context_tokens:,}")
        budget_col2.metric("Retrieved", f"{output.token_budget.retrieved_context_tokens:,}")
        budget_col3.metric("Handoff prompt", f"{output.token_budget.handoff_prompt_tokens:,}")
        budget_col4.metric("Reduction", f"{output.token_budget.estimated_reduction_percent:.1f}%")
        st.caption(
            f"Method: {output.token_budget.method} | "
            f"Verification status: {output.token_budget.verification_status} | "
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
        st.caption("Claude, Codex, ChatGPT에 복사해서 넘기기 위한 프롬프트입니다.")
        st.code(output.sections.ai_handoff_prompt, language="text")
        st.download_button(
            label="Download AI_HANDOFF_PROMPT.md",
            data=output.sections.ai_handoff_prompt,
            file_name="AI_HANDOFF_PROMPT.md",
            mime="text/markdown",
            key="download_ai_handoff_prompt",
        )

    with tabs[5]:
        st.markdown("### Risk & Approval")
        st.markdown(output.sections.risk_checklist)
        left, right = st.columns([1, 1])
        with left:
            st.markdown("#### Retrieved Context")
            for chunk in output.relevant_chunks:
                st.markdown(f"- `{chunk.path}:{chunk.start_line}-{chunk.end_line}` - score `{chunk.score:.2f}`")

            st.markdown("#### Risk Findings")
            if output.risk_findings:
                for finding in output.risk_findings:
                    st.markdown(
                        f"- **{finding.kind.value} / {finding.level.value}** - {finding.reason} / "
                        f"`{finding.path or finding.evidence or 'task'}`"
                    )
            else:
                st.markdown("- 뚜렷한 위험 신호 없음")

        with right:
            st.markdown("#### Human Approval Checklist")
            for index, item in enumerate(output.approval_checklist):
                st.checkbox(item, value=False, key=f"developer_checklist_{index}")

    with tabs[6]:
        st.markdown("### GitHub Issue Packet")
        st.markdown(f"**Issue Title:** {execution_packet.title}")
        st.markdown(f"**Recommended Branch:** `{execution_packet.recommended_branch}`")
        st.markdown(f"**Risk Level:** `{execution_packet.risk_level.value}`")
        st.markdown("**Labels:** " + ", ".join(f"`{label}`" for label in execution_packet.labels))
        st.code(execution_packet.issue_body, language="markdown")
        st.download_button(
            label="Download GITHUB_ISSUE.md",
            data=execution_packet.issue_body,
            file_name="GITHUB_ISSUE.md",
            mime="text/markdown",
            key="download_execution_packet",
        )

        with st.expander("Decision Record"):
            st.code(execution_packet.decision_record, language="markdown")

    with tabs[7]:
        st.markdown("### Saved Packet")
        st.caption("생성된 결과를 outputs/ 아래에 실제 작업 패킷 파일로 저장합니다.")
        if st.button("Save packet to outputs/", type="secondary"):
            saved = save_output_packet(output, execution_packet)
            st.session_state["saved_output_dir"] = str(saved.output_dir)
            st.success(f"Saved output packet: {saved.output_dir}")
            for name, path in saved.files.items():
                st.markdown(f"- `{name}`: `{path}`")

        saved_output_dir = st.session_state.get("saved_output_dir")
        if saved_output_dir:
            st.info(f"Last saved packet: {saved_output_dir}")

        st.markdown("#### Full Capsule Markdown")
        st.download_button(
            label="Download CONTEXT_CAPSULE.md",
            data=output.markdown,
            file_name="CONTEXT_CAPSULE.md",
            mime="text/markdown",
            key="download_capsule",
        )
        st.code(output.markdown, language="markdown")
