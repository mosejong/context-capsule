from __future__ import annotations

from pathlib import Path

import streamlit as st

from app.generators.capsule_generator import generate_capsule
from app.scanners.repo_scanner import scan_repo
from app.schemas.capsule_schema import CapsuleInput

st.set_page_config(page_title="Context Capsule", page_icon="🧩", layout="wide")

st.title("🧩 Context Capsule")
st.caption("RAG 기반 AI 코딩 작업 인수인계 패킷 생성 도구")

with st.sidebar:
    st.header("Input")
    repo_path = st.text_input("Local repository path", value=".")
    top_k = st.slider("Retrieved chunks", min_value=3, max_value=20, value=8)

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
        )
        files = scan_repo(input_data.repo_path)
        output = generate_capsule(input_data, files)

        st.success(f"Scanned {len(files)} files and generated capsule.")

        left, right = st.columns([1, 1])
        with left:
            st.markdown("### Retrieved Context")
            for chunk in output.relevant_chunks:
                st.markdown(f"- `{chunk.path}:{chunk.start_line}-{chunk.end_line}` · score `{chunk.score:.2f}`")

            st.markdown("### Risk Findings")
            if output.risk_findings:
                for finding in output.risk_findings:
                    st.markdown(f"- **{finding.level}** — {finding.reason} / `{finding.path or finding.evidence or 'task'}`")
            else:
                st.markdown("- 특별한 위험 신호 없음")

        with right:
            st.markdown("### Human Approval Checklist")
            for item in output.approval_checklist:
                st.checkbox(item, value=False)

        st.markdown("### Capsule Markdown")
        st.code(output.markdown, language="markdown")
        st.download_button(
            label="Download capsule.md",
            data=output.markdown,
            file_name="context_capsule.md",
            mime="text/markdown",
        )
    except Exception as exc:  # pragma: no cover - Streamlit UI guard
        st.error(str(exc))
