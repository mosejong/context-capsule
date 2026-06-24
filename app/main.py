from __future__ import annotations

from pathlib import Path

import streamlit as st

from app.analyzers.chat_analyzer import extract_task_request
from app.analyzers.meeting_analyzer import analyze_project_kickoff, analyze_scrum_notes
from app.generators.output_writer import save_output_packet
from app.services.capsule_service import generate_capsule_result
from app.schemas.capsule_schema import (
    CapsuleOutput,
    ExecutionPacket,
    HandoffTarget,
    ProjectKickoffOutput,
    RetrievalMode,
    ScrumNotesOutput,
)

st.set_page_config(page_title="Context Capsule", page_icon="CC", layout="wide")

st.title("Context Capsule")
st.caption("Local-first handoff packets for AI tools, teammates, scrum notes, and project kickoff planning.")

CAPSULE_LOADING_STEPS = [
    "저장소 파일을 스캔합니다.",
    "요청 의도와 보호 영역을 해석합니다.",
    "관련 파일 후보를 검색합니다.",
    "위험 신호와 승인 체크리스트를 분석합니다.",
    "대상별 작업 패킷을 생성합니다.",
]

INTENT_LABELS = {
    "documentation_edit": "문서 정리",
    "bug_investigation": "버그 조사",
    "feature_addition": "기능 추가",
    "refactor": "리팩터링",
    "test_update": "테스트 수정",
    "release_deploy": "릴리즈/배포 정리",
    "security_review": "보안 점검",
    "metric_validation": "토큰/성능 검증",
    "launcher_troubleshooting": "로컬 실행 문제",
    "meeting_notes": "회의록 정리",
    "project_kickoff": "프로젝트 착수 정리",
    "general": "일반 요청",
}


def render_first_run_guide() -> None:
    st.info(
        "처음이면 대시보드만 써도 됩니다. `Local repository path`를 정하고 "
        "`리드미 손보자` 또는 `로컬 실행 안돼`처럼 입력한 뒤 Generate를 누르세요."
    )
    st.markdown(
        "**한국어 설명서:** ZIP을 풀면 루트에 `START_HERE_KO.md`가 있습니다. "
        "전체 흐름은 `docs/kdt_beta_quickstart.md`에서 볼 수 있습니다."
    )
    with st.expander("KDT beta quickstart: dashboard first, terminal optional", expanded=True):
        st.markdown(
            "\n".join(
                [
                    "Recommended first test:",
                    "",
                    "1. Keep `Local repository path` as `.` if you extracted the ZIP.",
                    "2. Type `리드미 손보자` in the task box.",
                    "3. Click `Generate Capsule`.",
                    "4. Check `Overview`, `AI Handoff Prompt`, and `Risk & Approval` tabs.",
                    "",
                    "Terminal commands are optional. Use them only when you want to diagnose install/index behavior:",
                    "",
                    "```powershell",
                    ".\\context_capsule_cli.bat doctor --repo-path .",
                    ".\\context_capsule_cli.bat index --repo-path . --json",
                    '.\\context_capsule_cli.bat generate --repo-path . --task "리드미 손보자" --retriever indexed --target all --save --json',
                    '.\\context_capsule_cli.bat generate --repo-path . --task "이거 왜 안됨?" --retriever indexed --target all --save --json',
                    '.\\context_capsule_cli.bat feedback-template --project-name "my-project" --tester-name "nickname" --save --json',
                    "```",
                    "",
                    "영어 문서가 부담되면 `START_HERE_KO.md`부터 읽어도 됩니다.",
                    "Read `docs/kdt_beta_quickstart.md` for the full tester flow.",
                ]
            )
        )


def run_capsule_generation(
    repo_path: str,
    task_request: str,
    forbidden_text: str,
    top_k: int,
    handoff_target: HandoffTarget,
    retriever_mode: RetrievalMode,
) -> tuple[CapsuleOutput, ExecutionPacket, int]:
    rules = [line.strip() for line in forbidden_text.splitlines() if line.strip()]
    result = generate_capsule_result(
        repo_path=Path(repo_path),
        task_request=task_request,
        forbidden_rules=rules,
        top_k=top_k,
        handoff_target=handoff_target,
        retriever_mode=retriever_mode,
    )
    return result.capsule, result.execution_packet, result.scanned_file_count


def render_capsule_mode() -> None:
    render_first_run_guide()
    st.header("Work Handoff Packet")
    st.write("Turn a task request or chat/error log into AI, teammate, junior, and future-me handoff packets.")

    with st.sidebar:
        st.subheader("Capsule Settings")
        repo_path = st.text_input("Local repository path", value=".")
        top_k = st.slider("Retrieved chunks", min_value=3, max_value=20, value=8)
        retriever_mode = st.selectbox(
            "Retriever mode",
            options=list(RetrievalMode),
            format_func=lambda item: item.value,
            index=0,
            help=(
                "keyword is the default No-AI fallback. hybrid adds local vector ranking. "
                "indexed reuses a local persistent index and falls back safely."
            ),
        )
        handoff_target = st.selectbox(
            "Primary handoff target",
            options=list(HandoffTarget),
            format_func=lambda item: item.value,
            index=0,
        )
        input_mode = st.radio(
            "Input mode",
            options=["Direct task request", "Chat / error log"],
            index=0,
        )

    if input_mode == "Chat / error log":
        chat_log = st.text_area(
            "Paste Discord/GPT chat, meeting notes, or an error log",
            value=(
                "Leader: Token analyzer should be connected to the generator.\n"
                "Teammate: Where should it go?\n"
                "Leader: Add it near app/generators/capsule_generator.py and show it in Streamlit.\n"
                "Leader: Let's go with this direction."
            ),
            height=180,
        )
        extraction = extract_task_request(chat_log)
        task_request = extraction.task_request
        st.markdown("### Extracted Task Request")
        st.code(task_request, language="markdown")
        st.caption(f"Extraction confidence: {extraction.confidence:.2f}")
    else:
        task_request = st.text_area(
            "Task request",
            value="Create a login API fix handoff packet. Do not edit secrets or DB schema. Ask for a plan first.",
            height=120,
        )

    forbidden_text = st.text_area(
        "Forbidden / caution rules",
        value=(
            "Do not create a new branch automatically.\n"
            "Ask before DB schema changes.\n"
            "Do not edit secrets or environment values.\n"
            "Suggest a plan before applying changes."
        ),
        height=130,
    )

    if "capsule_is_generating" not in st.session_state:
        st.session_state["capsule_is_generating"] = False

    generate_clicked = st.button(
        "Generate Capsule",
        type="primary",
        disabled=st.session_state["capsule_is_generating"],
    )
    result_area = st.container()

    if generate_clicked:
        st.session_state["capsule_is_generating"] = True
        with result_area:
            status_box = st.status("생성 중입니다. 결과는 이 영역에 표시됩니다.", expanded=True)
            for step in CAPSULE_LOADING_STEPS:
                status_box.write(step)
            try:
                output, execution_packet, scanned_count = run_capsule_generation(
                    repo_path,
                    task_request,
                    forbidden_text,
                    top_k,
                    handoff_target,
                    retriever_mode,
                )
                st.session_state["capsule_output"] = output
                st.session_state["execution_packet"] = execution_packet
                st.session_state["scanned_count"] = scanned_count
                st.session_state.pop("saved_output_dir", None)
                status_box.update(
                    label=f"생성 완료: {scanned_count}개 파일을 스캔했습니다.",
                    state="complete",
                    expanded=False,
                )
                st.success(f"Scanned {scanned_count} files and generated {output.handoff_target.value} capsule.")
                render_capsule_output(output, execution_packet)
            except Exception as exc:  # pragma: no cover - Streamlit UI guard
                status_box.update(label="생성 실패: 아래 안내를 확인하세요.", state="error", expanded=True)
                st.error("캡슐 생성 중 오류가 났습니다.")
                st.markdown(
                    "- `Local repository path`가 실제 폴더인지 확인하세요.\n"
                    "- 처음 실행이면 인터넷 연결 상태와 설치 로그를 확인하세요.\n"
                    "- 계속 실패하면 오류 문구를 그대로 피드백에 붙여주세요."
                )
                st.code(str(exc), language="text")
            finally:
                st.session_state["capsule_is_generating"] = False
    else:
        output = st.session_state.get("capsule_output")
        execution_packet = st.session_state.get("execution_packet")
        if output and execution_packet:
            with result_area:
                render_capsule_output(output, execution_packet)


def render_capsule_output(output: CapsuleOutput, execution_packet: ExecutionPacket) -> None:
    if output.request_understanding.needs_clarification:
        render_clarification_guidance(output)

    tabs = st.tabs(
        [
            "Overview",
            "Future Me",
            "Teammate Brief",
            "Junior Guide",
            "AI Handoff",
            "Risk & Approval",
            "GitHub Issue",
            "Saved Packet",
        ]
    )

    with tabs[0]:
        render_request_understanding(output)
        st.markdown(output.sections.overview)
        st.caption(f"Retriever mode: {output.retriever_mode.value}")
        st.caption(
            "Retrieval report: "
            f"requested={output.retrieval_report.requested_mode}, "
            f"used={output.retrieval_report.used_mode}, "
            f"fallback={output.retrieval_report.fallback_reason or 'None'}"
        )
        if execution_packet.auto_start_allowed:
            st.success("Auto-start gate: allowed. No HIGH/BLOCKED change risk was found.")
        else:
            st.warning(f"Auto-start gate: blocked. {execution_packet.block_reason}")
        render_token_budget(output)

    with tabs[1]:
        st.markdown(output.sections.future_me_letter)

    with tabs[2]:
        st.markdown(output.sections.teammate_brief)

    with tabs[3]:
        st.markdown(output.sections.junior_guide)

    with tabs[4]:
        st.code(output.sections.ai_handoff_prompt, language="text")
        st.download_button(
            "Download AI_HANDOFF_PROMPT.md",
            data=output.sections.ai_handoff_prompt,
            file_name="AI_HANDOFF_PROMPT.md",
            mime="text/markdown",
            key="download_ai_handoff_prompt",
        )

    with tabs[5]:
        st.markdown(output.sections.risk_checklist)
        st.markdown("### Human Approval Checklist")
        for index, item in enumerate(output.approval_checklist):
            st.checkbox(item, value=False, key=f"developer_checklist_{index}")

    with tabs[6]:
        st.markdown(f"**Issue Title:** {execution_packet.title}")
        st.markdown(f"**Recommended Branch:** `{execution_packet.recommended_branch}`")
        st.markdown(f"**Risk Level:** `{execution_packet.risk_level.value}`")
        st.markdown("**Labels:** " + ", ".join(f"`{label}`" for label in execution_packet.labels))
        st.code(execution_packet.issue_body, language="markdown")

    with tabs[7]:
        if st.button("Save packet to outputs/", type="secondary"):
            saved = save_output_packet(output, execution_packet)
            st.session_state["saved_output_dir"] = str(saved.output_dir)
            st.success(f"Saved output packet: {saved.output_dir}")
            for name, path in saved.files.items():
                st.markdown(f"- `{name}`: `{path}`")

        saved_output_dir = st.session_state.get("saved_output_dir")
        if saved_output_dir:
            st.info(f"Last saved packet: {saved_output_dir}")
        st.download_button(
            "Download CONTEXT_CAPSULE.md",
            data=output.markdown,
            file_name="CONTEXT_CAPSULE.md",
            mime="text/markdown",
            key="download_capsule",
        )


def render_clarification_guidance(output: CapsuleOutput) -> None:
    question = output.request_understanding.clarification_question or "대상 파일, 기능명, 또는 오류 로그 중 하나를 알려주세요."
    st.warning(f"검색 전에 정보가 더 필요합니다: {question}")
    st.markdown(
        "관련 없는 파일을 뒤지지 않도록 여기서 멈췄습니다. 파일명, 기능명, 오류 로그 중 하나를 더 적고 다시 실행하세요."
    )
    st.code(
        "\n".join(
            [
                '예: "README.md를 포트폴리오용으로 다듬어줘"',
                '예: "로컬 실행 안돼. run_context_capsule.bat 쪽 봐줘"',
                '예: "이 에러 로그 기준으로 관련 파일만 찾아줘"',
            ]
        ),
        language="text",
    )


def render_request_understanding(output: CapsuleOutput) -> None:
    understanding = output.request_understanding
    with st.expander("요청 해석 상세", expanded=understanding.needs_clarification):
        st.write(f"요청 의도: `{INTENT_LABELS.get(understanding.intent, understanding.intent)}` (`{understanding.intent}`)")
        st.write(f"확신도: `{understanding.confidence_label}` ({understanding.confidence:.2f})")
        st.write(f"추가 질문 필요: `{understanding.needs_clarification}`")
        if understanding.clarification_question:
            st.warning(understanding.clarification_question)
        st.write(f"수정 대상 힌트: {', '.join(understanding.target_hints) if understanding.target_hints else '없음'}")
        st.write(f"보호 영역: {', '.join(understanding.protected_hints) if understanding.protected_hints else '없음'}")
        st.write(f"파일 힌트: {', '.join(understanding.file_hints) if understanding.file_hints else '없음'}")
        st.caption("아래 검색용 쿼리는 내부 디버그 정보입니다. 팀원/주니어 브리프에는 원문 요청 중심으로 보여줍니다.")
        st.code(understanding.search_query or output.task_request, language="text")


def render_token_budget(output: CapsuleOutput) -> None:
    st.markdown("### Token Budget")
    budget_col1, budget_col2, budget_col3, budget_col4 = st.columns(4)
    budget_col1.metric("Candidate files", f"{output.token_budget.raw_context_tokens:,}")
    budget_col2.metric("Retrieved", f"{output.token_budget.retrieved_context_tokens:,}")
    budget_col3.metric("Handoff prompt", f"{output.token_budget.handoff_prompt_tokens:,}")
    budget_col4.metric("Reduction", f"{output.token_budget.estimated_reduction_percent:.1f}%")
    st.caption(
        f"Method: {output.token_budget.method} | "
        f"Baseline scope: {output.token_budget.baseline_context_scope} | "
        f"Verification status: {output.token_budget.verification_status} | "
        f"Actual provider usage: {output.token_budget.actual_provider_usage}"
    )


def render_scrum_mode() -> None:
    st.header("Scrum Notes Mode")
    st.write("Paste scrum notes or instructor feedback. Context Capsule will extract decisions, blockers, next actions, and issue drafts.")

    meeting_text = st.text_area(
        "Scrum / meeting notes",
        value=(
            "Instructor: Reduce the MVP scope and avoid deployment this sprint.\n"
            "Team: Login API handoff is the next priority.\n"
            "Team: Streamlit demo and release notes must be ready before presentation.\n"
            "Question: Which features should be deferred?"
        ),
        height=220,
    )
    project_context = st.text_input("Optional project context", value="Context Capsule v0.2.0 planning")
    instructor_feedback = st.text_area("Instructor / team-lead feedback", value="", height=100)

    if st.button("Generate Scrum Notes", type="primary"):
        output = analyze_scrum_notes(
            meeting_text,
            project_context=project_context,
            instructor_feedback=instructor_feedback,
        )
        st.session_state["scrum_output"] = output

    output = st.session_state.get("scrum_output")
    if output:
        render_scrum_output(output)


def render_scrum_output(output: ScrumNotesOutput) -> None:
    tabs = st.tabs(["Summary", "Decisions", "Next Actions", "Issue Drafts", "Team Lead Notes", "Markdown"])
    with tabs[0]:
        st.markdown("### Source Summary")
        st.markdown(output.source_summary)
        st.markdown("### Direction Changes")
        render_list(output.direction_changes or ["No direction change detected."])
        st.markdown("### Blockers")
        render_list(output.blockers or ["No blocker detected."])
    with tabs[1]:
        render_list(output.decisions)
        st.markdown("### Open Questions")
        render_list(output.open_questions)
    with tabs[2]:
        render_list(output.next_actions)
    with tabs[3]:
        render_issue_drafts(output.issue_drafts)
    with tabs[4]:
        st.markdown("### Team Lead Notes")
        render_list(output.team_lead_notes)
        st.markdown("### Safety Notes")
        render_list(output.safety_notes)
    with tabs[5]:
        st.code(output.markdown, language="markdown")
        st.download_button("Download SCRUM_NOTES.md", output.markdown, "SCRUM_NOTES.md", "text/markdown")


def render_kickoff_mode() -> None:
    st.header("Project Kickoff Mode")
    st.write("Turn a contest/project topic and idea meeting notes into MVP scope, workstreams, issue drafts, and a submission checklist.")

    topic = st.text_input("Project / contest topic", value="Context Capsule v0.2.0 for scrum-to-execution planning")
    idea_notes = st.text_area(
        "Idea meeting notes",
        value=(
            "Build Scrum Notes Mode and Project Kickoff Mode first.\n"
            "Discord API can wait until after text-input MVP.\n"
            "Avoid teammate scoring or automatic assignment.\n"
            "Need demo, README, tests, and issue drafts."
        ),
        height=220,
    )
    deadline = st.text_input("Deadline", value="2 weeks")
    constraints = st.text_area(
        "Constraints",
        value="No people scoring. No automatic assignment. Human approval required for risky work.",
        height=100,
    )
    team_context = st.text_area(
        "Team context (self-reported capacity/preferences only)",
        value="Team lead will confirm owner assignments manually.",
        height=100,
    )

    if st.button("Generate Kickoff Packet", type="primary"):
        output = analyze_project_kickoff(
            topic=topic,
            idea_notes=idea_notes,
            deadline=deadline,
            constraints=constraints,
            team_context=team_context,
        )
        st.session_state["kickoff_output"] = output

    output = st.session_state.get("kickoff_output")
    if output:
        render_kickoff_output(output)


def render_kickoff_output(output: ProjectKickoffOutput) -> None:
    tabs = st.tabs(["MVP Scope", "Workstreams", "Questions", "Issue Drafts", "Submission", "Markdown"])
    with tabs[0]:
        st.markdown("### One-Line Pitch")
        st.markdown(output.one_line_pitch)
        st.markdown("### MVP Scope")
        render_list(output.mvp_scope)
        st.markdown("### Out of Scope")
        render_list(output.out_of_scope)
    with tabs[1]:
        render_list(output.workstreams)
        st.markdown("### Risks")
        render_list(output.risks)
    with tabs[2]:
        render_list(output.open_questions)
        st.markdown("### Team Lead Notes")
        render_list(output.team_lead_notes)
    with tabs[3]:
        render_issue_drafts(output.issue_drafts)
    with tabs[4]:
        render_checklist(output.submission_checklist)
    with tabs[5]:
        st.code(output.markdown, language="markdown")
        st.download_button("Download PROJECT_KICKOFF.md", output.markdown, "PROJECT_KICKOFF.md", "text/markdown")


def render_list(items: list[str]) -> None:
    for item in items:
        st.markdown(f"- {item}")


def render_checklist(items: list[str]) -> None:
    for index, item in enumerate(items):
        st.checkbox(item, value=False, key=f"checklist_{index}_{item}")


def render_issue_drafts(issue_drafts) -> None:
    for index, issue in enumerate(issue_drafts, start=1):
        with st.expander(f"{index}. {issue.title}"):
            st.markdown("**Labels:** " + ", ".join(f"`{label}`" for label in issue.labels))
            st.code(issue.body, language="markdown")


mode = st.sidebar.radio(
    "Workflow",
    options=["Work Handoff", "Scrum Notes", "Project Kickoff"],
    index=0,
)

if mode == "Work Handoff":
    render_capsule_mode()
elif mode == "Scrum Notes":
    render_scrum_mode()
else:
    render_kickoff_mode()
