from __future__ import annotations

import re
from collections.abc import Iterable

from app.schemas.capsule_schema import HealthSignal, IssueDraft, ProjectHealthOutput, ProjectKickoffOutput, ScrumNotesOutput


DECISION_HINTS = (
    "decision",
    "decide",
    "decided",
    "fixed",
    "final",
    "go with",
    "mvp",
    "priority",
    "scope",
    "\uacb0\uc815",
    "\ud655\uc815",
    "\uc774\uac78\ub85c",
    "\uac00\uc790",
    "\uc120\ud0dd",
    "\ubc29\ud5a5",
    "\uc77c\ub2e8",
    "\ub2e4\uc2dc \ud14c\uc2a4\ud2b8",
)
BLOCKER_HINTS = (
    "block",
    "blocked",
    "blocker",
    "bug",
    "error",
    "fail",
    "failed",
    "issue",
    "problem",
    "stuck",
    "\ub9c9\ud798",
    "\uc774\uc288",
    "\uc624\ub958",
    "\uc5d0\ub7ec",
    "\ubb38\uc81c",
    "\uc548\ub428",
    "\uc548\ub3fc",
    "\uc548 \ub418",
    "\uc548 \ub420",
    "\uc2e4\ud328",
    "\uac80\uc740\uc0c9",
    "\uc800\uc7a5\uc774 \uc548",
    "\ub7a8",
    "timeout",
)
DIRECTION_HINTS = (
    "defer",
    "feedback",
    "later",
    "mvp",
    "pivot",
    "reduce",
    "roadmap",
    "scope",
    "\uac15\uc0ac\ub2d8",
    "\ud53c\ub4dc\ubc31",
    "\ubc29\ud5a5",
    "\ubc94\uc704",
    "\uc904\uc774",
    "\ubbf8\ub8e8",
    "\ub098\uc911",
    "\uc6b0\uc120\uc21c\uc704",
)
ACTION_HINTS = (
    "add",
    "build",
    "create",
    "fix",
    "implement",
    "make",
    "prepare",
    "refine",
    "test",
    "update",
    "write",
    "\uad6c\ud604",
    "\ucd94\uac00",
    "\uc218\uc815",
    "\uc815\ub9ac",
    "\uc791\uc131",
    "\ub9cc\ub4e4",
    "\ubd99\uc774",
    "\uc5f0\ub3d9",
    "\uac80\uc99d",
    "\ud14c\uc2a4\ud2b8",
    "\ud574\uc57c",
    "\ud655\uc778",
    "\ub298\ub824",
    "\ub9de\ucdb0",
    "\uc81c\uac70",
    "\ud0a4\uc6cc",
)
OUT_OF_SCOPE_HINTS = (
    "defer",
    "deferred",
    "later",
    "not now",
    "out of scope",
    "skip",
    "\uc81c\uc678",
    "\ubbf8\ub8e8",
    "\ub098\uc911",
    "\uc544\uc9c1 \uc544\ub2d8",
    "\ubcf4\ub958",
)
RISK_HINTS = (
    "auth",
    "db",
    "deploy",
    "env",
    "jwt",
    "privacy",
    "schema",
    "secret",
    "security",
    "\uc704\ud5d8",
    "\ub9ac\uc2a4\ud06c",
    "\ubcf4\uc548",
    "\ubc30\ud3ec",
    "\uac1c\uc778\uc815\ubcf4",
)
OWNER_HINTS = (
    "assignee",
    "assigned",
    "owner",
    "responsible",
    "my part",
    "take",
    "\ub2f4\ub2f9",
    "\ub0b4 \ud30c\ud2b8",
    "\uc81c \ud30c\ud2b8",
    "\ub0b4\uac00",
    "\uc81c\uac00",
    "\ub9e1",
    "\ub204\uac00",
)
ACCEPTANCE_HINTS = (
    "acceptance",
    "criteria",
    "done",
    "complete",
    "completed",
    "\uc644\ub8cc \uae30\uc900",
    "\uc644\ub8cc",
    "\ud1b5\uacfc",
    "\ud655\uc778",
    "\uac80\uc99d",
)
TEST_HINTS = (
    "pytest",
    "test",
    "tests",
    "passed",
    "pass",
    "qa",
    "smoke",
    "dry-run",
    "dry run",
    "\ud14c\uc2a4\ud2b8",
    "\uac80\uc99d",
    "\ud1b5\uacfc",
    "\ud655\uc778 \uc644\ub8cc",
)
DEADLINE_HINTS = (
    "deadline",
    "due",
    "today",
    "tomorrow",
    "friday",
    "week",
    "sprint",
    "\uc624\ub298",
    "\ub0b4\uc77c",
    "\uae08\uc694\uc77c",
    "\ub9c8\uac10",
    "\uae4c\uc9c0",
    "\uc81c\ucd9c",
    "\ubc1c\ud45c",
    "\uc2a4\ud504\ub9b0\ud2b8",
    "\uc8fc\ub9d0",
    "\uc7ac\ud14c\uc2a4\ud2b8",
    "\ub2e4\uc74c \ud655\uc778",
)
DEMO_HINTS = (
    "demo",
    "runnable",
    "run",
    "running",
    "dashboard",
    "localhost",
    "release",
    "zip",
    "\uc2dc\uc5f0",
    "\uc2e4\ud589",
    "\ub3d9\uc791",
    "\ud654\uba74",
    "\ub9b4\ub9ac\uc988",
)
FEEDBACK_HINTS = (
    "feedback",
    "tester",
    "beta",
    "review",
    "user",
    "\ud53c\ub4dc\ubc31",
    "\ud14c\uc2a4\ud130",
    "\ub9ac\ubdf0",
    "\uc0ac\uc6a9\uc790",
    "\uac15\uc0ac\ub2d8",
)
ITERATION_HINTS = (
    "release",
    "v0.",
    "hotfix",
    "patch",
    "fix",
    "improve",
    "update",
    "\ub9b4\ub9ac\uc988",
    "\ud328\uce58",
    "\uac1c\uc120",
    "\ubc18\uc601",
)
DOC_HINTS = (
    "readme",
    "docs",
    "guide",
    "quickstart",
    "manual",
    "\ubb38\uc11c",
    "\uac00\uc774\ub4dc",
    "\uc124\uba85\uc11c",
)
WORKSTREAM_HINTS = {
    "Backend/API": (
        "backend",
        "api",
        "fastapi",
        "router",
        "auth",
        "jwt",
        "\uc11c\ubc84",
        "\ubc31\uc5d4\ub4dc",
    ),
    "Frontend/UI": (
        "frontend",
        "ui",
        "screen",
        "streamlit",
        "react",
        "\ud654\uba74",
        "\ud504\ub860\ud2b8",
    ),
    "Data/DB": ("db", "database", "schema", "sqlite", "postgres", "\ub370\uc774\ud130"),
    "Infra/Release": ("deploy", "docker", "release", "zip", "\ubc30\ud3ec", "\ub9b4\ub9ac\uc988"),
    "AI/RAG": ("ai", "embedding", "llm", "prompt", "rag", "\ud504\ub86c\ud504\ud2b8"),
    "Docs/Presentation": (
        "docs",
        "readme",
        "report",
        "presentation",
        "\ubb38\uc11c",
        "\ubc1c\ud45c",
        "\ud3ec\ud2b8\ud3f4\ub9ac\uc624",
    ),
    "Testing/QA": ("pytest", "qa", "test", "validation", "\uac80\uc99d", "\ud14c\uc2a4\ud2b8"),
    "Project Lead": (
        "deadline",
        "meeting",
        "planning",
        "scrum",
        "\uc2a4\ud06c\ub7fc",
        "\ud68c\uc758",
        "\uc77c\uc815",
        "\ub9c8\uac10",
    ),
}


def analyze_scrum_notes(
    meeting_text: str,
    project_context: str = "",
    instructor_feedback: str = "",
) -> ScrumNotesOutput:
    lines = meaningful_lines("\n".join([meeting_text, instructor_feedback]))
    decisions = pick_lines(lines, DECISION_HINTS)
    blockers = pick_lines(lines, BLOCKER_HINTS)
    direction_changes = pick_lines(lines, DIRECTION_HINTS)
    action_lines = pick_lines(lines, ACTION_HINTS)
    open_questions = find_questions(lines)
    next_actions = build_next_actions(action_lines, decisions, blockers)
    issue_drafts = build_issue_drafts(next_actions or decisions, mode="scrum")

    if not open_questions:
        open_questions = [
            "What is the smallest demoable scope before the next scrum?",
            "Which risky work needs explicit approval before implementation?",
            "What should be deferred to keep the sprint realistic?",
        ]

    output = ScrumNotesOutput(
        source_summary=summarize_source(lines, project_context),
        decisions=decisions or ["No explicit decision detected. Confirm the decision before creating issues."],
        blockers=blockers,
        direction_changes=direction_changes,
        next_actions=next_actions,
        open_questions=open_questions,
        role_discussion_questions=build_role_discussion_questions(next_actions, blockers),
        issue_drafts=issue_drafts,
        team_lead_notes=build_team_lead_notes(),
        safety_notes=build_safety_notes(),
        markdown="",
    )
    output.markdown = build_scrum_markdown(output)
    return output


def analyze_project_kickoff(
    topic: str,
    idea_notes: str,
    deadline: str = "",
    constraints: str = "",
    team_context: str = "",
) -> ProjectKickoffOutput:
    combined = "\n".join([topic, idea_notes, constraints, team_context])
    lines = meaningful_lines(combined)
    decisions = pick_lines(lines, DECISION_HINTS)
    actions = pick_lines(lines, ACTION_HINTS)
    risks = pick_lines(lines, RISK_HINTS)
    out_of_scope = pick_lines(lines, OUT_OF_SCOPE_HINTS)
    questions = find_questions(lines)
    workstreams = detect_workstreams(combined)

    out_of_scope = dedupe([*out_of_scope, *build_default_out_of_scope()])
    if not questions:
        questions = [
            "What must be shown in the final demo?",
            "Which features can be safely deferred?",
            "Which tasks require instructor or team-lead approval?",
        ]
    if deadline:
        questions.append(f"Can the MVP scope be completed before {deadline}?")

    output = ProjectKickoffOutput(
        one_line_pitch=build_one_line_pitch(topic, decisions, lines),
        mvp_scope=build_mvp_scope(topic, actions, decisions, workstreams),
        out_of_scope=out_of_scope,
        workstreams=workstreams,
        risks=risks or ["No explicit technical risk detected. Re-check auth, DB, deploy, and credential scope."],
        open_questions=questions,
        role_discussion_questions=build_role_discussion_questions(output_candidates_from(workstreams, actions, decisions), risks),
        issue_drafts=[],
        submission_checklist=build_submission_checklist(deadline),
        team_lead_notes=build_team_lead_notes(),
        safety_notes=build_safety_notes(),
        markdown="",
    )
    output.issue_drafts = build_issue_drafts(output.mvp_scope, mode="kickoff")
    output.markdown = build_kickoff_markdown(output)
    return output


def analyze_project_health(
    status_text: str,
    project_context: str = "",
    deadline: str = "",
    my_scope: str = "",
) -> ProjectHealthOutput:
    combined_text = "\n".join([project_context, status_text, deadline, my_scope])
    lines = meaningful_lines(combined_text)

    decisions = pick_lines(lines, DECISION_HINTS)
    actions = pick_lines(lines, ACTION_HINTS)
    acceptance = positive_signal_lines(pick_lines(lines, ACCEPTANCE_HINTS))
    tests = pick_lines(lines, TEST_HINTS)
    owners = positive_signal_lines(pick_lines(lines, OWNER_HINTS))
    blockers = pick_lines(lines, BLOCKER_HINTS)
    risks = pick_lines(lines, RISK_HINTS)
    schedules = pick_lines(lines, DEADLINE_HINTS)
    demos = pick_lines(lines, DEMO_HINTS)
    feedback = pick_lines(lines, FEEDBACK_HINTS)
    iterations = pick_lines(lines, ITERATION_HINTS)
    docs = pick_lines(lines, DOC_HINTS)

    mvp_signals = [
        build_health_signal("결정사항", 20, decisions, "회의에서 확정된 방향이나 우선순위가 없습니다."),
        build_health_signal("다음 액션", 20, actions, "다음에 바로 할 작업이 부족합니다."),
        build_health_signal("완료 기준", 15, acceptance, "끝났다고 판단할 기준이 부족합니다."),
        build_health_signal("테스트/검증", 15, tests, "검증 명령이나 테스트 결과가 부족합니다."),
        build_health_signal("담당 영역", 10, owners, "누가 어떤 영역을 맡는지 확인이 필요합니다."),
        build_health_signal("리스크/막힌 점", 10, [*blockers, *risks], "막힌 점이나 불확실성이 드러나지 않았습니다."),
        build_health_signal("마감/일정", 10, schedules, "마감이나 다음 확인 시점이 부족합니다."),
    ]
    prototype_signals = [
        build_health_signal("실행 가능한 데모", 25, demos, "사용자가 직접 볼 수 있는 실행/시연 신호가 부족합니다."),
        build_health_signal("핵심 플로우", 20, [*decisions, *actions], "핵심 사용자 흐름이나 MVP 범위가 부족합니다."),
        build_health_signal("테스터 피드백", 15, feedback, "외부 사용자나 팀원 피드백이 부족합니다."),
        build_health_signal("반복 개선 기록", 15, iterations, "릴리즈/패치/개선 기록이 부족합니다."),
        build_health_signal("문서/설치 안내", 10, docs, "README, 가이드, 설치 문서 신호가 부족합니다."),
        build_health_signal("검증 명령", 10, tests, "테스트 명령이나 검증 결과가 부족합니다."),
        build_health_signal("남은 리스크", 5, [*blockers, *risks], "남은 리스크를 명시하면 다음 회의가 더 빨라집니다."),
    ]

    mvp_percent = score_health_signals(mvp_signals)
    prototype_percent = score_health_signals(prototype_signals)
    stability_score = calculate_stability_score(mvp_percent, prototype_percent, blockers, tests, decisions, actions)
    missing_items = build_missing_meeting_items(mvp_signals)
    next_questions = build_next_meeting_questions(missing_items)
    ownership_status, ownership_notes, ownership_questions = analyze_ownership(status_text, my_scope)

    output = ProjectHealthOutput(
        mvp_completion_percent=mvp_percent,
        prototype_completion_percent=prototype_percent,
        stability_label=label_stability(stability_score),
        stability_score=stability_score,
        ownership_status=ownership_status,
        ownership_notes=ownership_notes,
        ownership_questions=ownership_questions,
        summary=build_health_summary(mvp_percent, prototype_percent, stability_score, missing_items),
        missing_meeting_items=missing_items,
        next_meeting_questions=next_questions,
        mvp_signals=mvp_signals,
        prototype_signals=prototype_signals,
        risk_notes=dedupe([*blockers[:4], *risks[:4]]) or ["명시된 리스크가 적습니다. 다음 회의에서 불확실성을 한 번 더 확인하세요."],
        safety_notes=build_safety_notes(),
        markdown="",
    )
    output.markdown = build_health_markdown(output)
    return output


def meaningful_lines(text: str) -> list[str]:
    return dedupe(normalize_line(line) for line in text.splitlines() if normalize_line(line))


def normalize_line(line: str) -> str:
    line = line.strip()
    line = re.sub(r"\s+", " ", line)
    line = re.sub(r"^[>\-\*\d\.\)\s]+", "", line)
    return line.strip()


def pick_lines(lines: list[str], hints: tuple[str, ...]) -> list[str]:
    selected = []
    for line in lines:
        lower = line.lower()
        if any(hint.lower() in lower for hint in hints):
            selected.append(line)
    return dedupe(selected)


def find_questions(lines: list[str]) -> list[str]:
    korean_question_endings = ("\ub098\uc694", "\uc744\uae4c\uc694", "\uc5b4\uc694", "\uc8e0")
    questions = [
        line
        for line in lines
        if "?" in line or any(line.endswith(ending) for ending in korean_question_endings)
    ]
    return dedupe(questions)


def positive_signal_lines(lines: list[str]) -> list[str]:
    incomplete_hints = (
        "not decided",
        "not confirmed",
        "need to confirm",
        "needs confirmation",
        "\uc544\uc9c1",
        "\ubd80\uc871",
        "\uc5c6",
        "\uc815\ud574\uc57c",
        "\ud655\uc778\ud574\uc57c",
        "\ud655\uc778 \ud544\uc694",
        "\ub2e4\uc2dc \ud655\uc778",
    )
    return [line for line in lines if not any(hint in line.lower() for hint in incomplete_hints)]


def summarize_source(lines: list[str], project_context: str) -> str:
    if not lines:
        return "No meeting content was provided."
    summary = " / ".join(lines[:5])
    if project_context.strip():
        return f"{summary}\n\nProject context: {project_context.strip()}"
    return summary


def build_next_actions(action_lines: list[str], decisions: list[str], blockers: list[str]) -> list[str]:
    candidates = action_lines or decisions
    actions = [f"Turn into an executable task: {line}" for line in candidates[:8]]
    actions.extend(f"Resolve blocker or ask for help: {blocker}" for blocker in blockers[:3])
    if not actions:
        actions.append("Confirm the final decision, then create one small issue for the next work session.")
    return dedupe(actions)


def build_issue_drafts(items: list[str], mode: str) -> list[IssueDraft]:
    drafts = []
    for item in items[:5]:
        acceptance_criteria = [
            "Task scope is clear.",
            "Risks and dependencies are listed.",
            "Final owner is approved by a human lead.",
        ]
        body = "\n".join(
            [
                "# Context Capsule Draft Issue",
                "",
                "## Source",
                item,
                "",
                "## Scope",
                "- Convert this into the smallest reviewable task.",
                "- Confirm owner and priority manually.",
                "- Do not auto-assign based on meeting participation.",
                "- Do not evaluate teammate skill from this issue draft.",
                "",
                "## Acceptance Criteria",
                *[f"- [ ] {criterion}" for criterion in acceptance_criteria],
            ]
        )
        drafts.append(
            IssueDraft(
                title=build_issue_title(item),
                body=body,
                labels=["context-capsule", f"mode:{mode}", "needs-human-approval"],
                acceptance_criteria=acceptance_criteria,
            )
        )
    return drafts


def build_issue_title(text: str) -> str:
    title = re.sub(r"^(Turn into an executable task:|Resolve blocker or ask for help:)\s*", "", text).strip()
    title = re.sub(r"\s+", " ", title)
    if len(title) > 72:
        title = title[:69].rstrip() + "..."
    return title or "Context Capsule task"


def build_one_line_pitch(topic: str, decisions: list[str], lines: list[str]) -> str:
    if topic.strip():
        return topic.strip()
    if decisions:
        return decisions[0]
    if lines:
        return lines[0]
    return "Project kickoff brief"


def output_candidates_from(workstreams: list[str], actions: list[str], decisions: list[str]) -> list[str]:
    candidates = [f"Workstream: {item}" for item in workstreams]
    candidates.extend(actions[:3])
    candidates.extend(decisions[:3])
    return dedupe(candidates)


def build_mvp_scope(
    topic: str,
    actions: list[str],
    decisions: list[str],
    workstreams: list[str],
) -> list[str]:
    scope = [item for item in (actions or decisions)[:6]]
    if not scope:
        scope.append(f"Define the smallest demoable workflow for {topic or 'the project'}.")
    if workstreams:
        scope.append("Prepare work packets for: " + ", ".join(workstreams[:4]))
    return dedupe(scope)


def build_default_out_of_scope() -> list[str]:
    return [
        "Automatic teammate evaluation or scoring",
        "Automatic assignment without human approval",
        "Automatic deployment or submission",
    ]


def detect_workstreams(text: str) -> list[str]:
    lower = text.lower()
    workstreams = []
    for workstream, hints in WORKSTREAM_HINTS.items():
        if any(hint.lower() in lower for hint in hints):
            workstreams.append(workstream)
    return workstreams or ["Project Lead", "Docs/Presentation", "Testing/QA"]


def build_submission_checklist(deadline: str) -> list[str]:
    checklist = [
        "One-line project definition is written.",
        "MVP scope and out-of-scope items are separated.",
        "Issue drafts are reviewed by the team lead.",
        "Risky work has explicit approval before implementation.",
        "Demo scenario and validation commands are fixed.",
        "README and release/demo notes are updated.",
    ]
    if deadline:
        checklist.insert(0, f"Deadline is confirmed: {deadline}.")
    return checklist


def build_team_lead_notes() -> list[str]:
    return [
        "Do not evaluate people from speaking volume or meeting style.",
        "Ask teammates to self-report capacity, preferred work, and blockers.",
        "Use recommendations as planning hints only.",
        "Final assignment stays with the human team lead.",
    ]


def build_role_discussion_questions(work_items: list[str], blockers: list[str]) -> list[str]:
    questions = [
        "Which task has a volunteer based on self-reported capacity?",
        "Which task needs pairing, review, or instructor help before someone takes it?",
        "Which task should stay unassigned until the team lead confirms scope?",
        "What is the smallest next action for the next work session?",
    ]
    if work_items:
        questions.insert(0, f"Who wants to take the first small task related to: {work_items[0]}")
    if blockers:
        questions.append(f"Who can help unblock this without assigning blame: {blockers[0]}")
    return dedupe(questions)


def build_safety_notes() -> list[str]:
    return [
        "No automatic teammate scoring.",
        "No automatic assignment.",
        "No hidden meeting analysis.",
        "Meeting notes should be collected with participant awareness.",
    ]


def build_health_signal(name: str, weight: int, evidence: list[str], missing_message: str) -> HealthSignal:
    compact_evidence = dedupe(evidence)[:4]
    return HealthSignal(
        name=name,
        detected=bool(compact_evidence),
        weight=weight,
        evidence=compact_evidence,
        missing_message=missing_message,
    )


def score_health_signals(signals: list[HealthSignal]) -> int:
    total = sum(signal.weight for signal in signals)
    if total <= 0:
        return 0
    earned = sum(signal.weight for signal in signals if signal.detected)
    return round(earned / total * 100)


def calculate_stability_score(
    mvp_percent: int,
    prototype_percent: int,
    blockers: list[str],
    tests: list[str],
    decisions: list[str],
    actions: list[str],
) -> int:
    score = round((mvp_percent * 0.6) + (prototype_percent * 0.4))
    if blockers:
        score -= 8
    if not tests:
        score -= 10
    if not decisions:
        score -= 8
    if not actions:
        score -= 8
    return max(0, min(100, score))


def label_stability(score: int) -> str:
    if score >= 85:
        return "안정적 베타"
    if score >= 70:
        return "베타 가능"
    if score >= 50:
        return "회의 보강 필요"
    return "착수 전 정리 필요"


def build_missing_meeting_items(signals: list[HealthSignal]) -> list[str]:
    missing = [f"{signal.name}: {signal.missing_message}" for signal in signals if not signal.detected]
    return missing or ["큰 누락 항목은 없습니다. 다음 회의에서는 담당자, 완료 기준, 검증 명령을 다시 확인하세요."]


def build_next_meeting_questions(missing_items: list[str]) -> list[str]:
    questions = []
    joined = "\n".join(missing_items)
    if "담당" in joined:
        questions.append("각 작업의 담당자는 누구인가요? 내 파트와 다른 사람 파트를 어떻게 구분하나요?")
    if "완료 기준" in joined:
        questions.append("이 작업이 끝났다고 판단할 기준은 무엇인가요?")
    if "테스트" in joined or "검증" in joined:
        questions.append("어떤 명령이나 시나리오로 검증할 예정인가요?")
    if "마감" in joined or "일정" in joined:
        questions.append("언제까지 완료해야 하고, 다음 확인 시점은 언제인가요?")
    if "리스크" in joined or "막힌" in joined:
        questions.append("현재 가장 큰 불확실성이나 막힌 점은 무엇인가요?")
    if "다음 액션" in joined:
        questions.append("다음 작업 1개를 오늘 바로 시작 가능한 크기로 줄이면 무엇인가요?")
    if "결정사항" in joined:
        questions.append("이번 회의에서 확정된 결정은 무엇이고, 아직 보류된 것은 무엇인가요?")
    return dedupe(questions) or [
        "다음 회의에서 담당자, 완료 기준, 검증 방법을 다시 확인할까요?",
        "현재 작업 중 내 파트와 다른 사람 파트가 겹치는 파일은 없나요?",
    ]


def analyze_ownership(status_text: str, my_scope: str) -> tuple[str, list[str], list[str]]:
    if not my_scope.strip():
        return (
            "needs_confirmation",
            ["내 담당 영역이 입력되지 않았습니다. 지금 결과는 팀 전체 기준입니다."],
            ["내가 맡은 폴더, 기능, 파일명을 적으면 내 파트 여부를 더 잘 확인할 수 있습니다."],
        )

    status_tokens = ownership_tokens(status_text)
    scope_tokens = ownership_tokens(my_scope)
    overlap = sorted(status_tokens & scope_tokens)
    protected_other_hints = {"다른사람", "다른", "팀원", "백엔드", "프론트", "frontend", "backend"} & status_tokens

    if overlap:
        return (
            "likely_my_part",
            [
                "회의 내용과 내 담당 영역 사이에 겹치는 단어가 있습니다.",
                "겹친 힌트: " + ", ".join(overlap[:8]),
            ],
            ["겹치는 파일을 수정하기 전에 같은 파일을 맡은 사람이 없는지 PR/Issue에서 확인하세요."],
        )

    if protected_other_hints:
        return (
            "possibly_other_part",
            ["회의 내용이 다른 영역과 관련 있어 보입니다. 내 파트인지 확인이 필요합니다."],
            ["이 작업은 누구 담당인가요?", "내 파트에서 수정해야 하는 파일이 맞나요?"],
        )

    return (
        "needs_confirmation",
        ["내 담당 영역과 회의 내용의 직접적인 단어 겹침이 적습니다."],
        ["이 작업이 내 파트인지, 다른 사람 파트인지 회의에서 먼저 확인하세요."],
    )


def ownership_tokens(text: str) -> set[str]:
    lower = text.lower()
    raw_tokens = re.findall(r"[a-zA-Z0-9_./-]+|[가-힣]{2,}", lower)
    stopwords = {
        "그리고",
        "하지만",
        "있습니다",
        "합니다",
        "해야",
        "확인",
        "작업",
        "회의",
        "프로젝트",
        "기능",
    }
    return {token.strip("./-_") for token in raw_tokens if len(token.strip("./-_")) >= 2 and token not in stopwords}


def build_health_summary(
    mvp_percent: int,
    prototype_percent: int,
    stability_score: int,
    missing_items: list[str],
) -> str:
    if stability_score >= 70:
        base = "현재 회의 내용은 작업으로 이어질 수 있는 수준입니다."
    elif stability_score >= 50:
        base = "작업 착수는 가능하지만 회의에서 몇 가지 항목을 더 확정해야 합니다."
    else:
        base = "아직 작업 착수 전에 결정사항과 완료 기준을 더 정리해야 합니다."
    first_missing = missing_items[0] if missing_items else "담당자/완료 기준 재확인"
    if ":" in first_missing:
        first_missing = first_missing.split(":", 1)[0]
    return (
        f"{base} MVP 준비도는 {mvp_percent}%, 프로토타입 준비도는 {prototype_percent}%입니다. "
        f"우선 보강할 항목은 {first_missing}입니다."
    )


def build_scrum_markdown(output: ScrumNotesOutput) -> str:
    return "\n\n".join(
        [
            "# Scrum Notes Packet",
            "## Source Summary\n" + output.source_summary,
            "## Decisions\n" + markdown_list(output.decisions),
            "## Blockers\n" + markdown_list(output.blockers or ["No blocker detected."]),
            "## Direction Changes\n" + markdown_list(output.direction_changes or ["No direction change detected."]),
            "## Next Actions\n" + markdown_list(output.next_actions),
            "## Open Questions\n" + markdown_list(output.open_questions),
            "## Role Discussion Questions\n" + markdown_list(output.role_discussion_questions),
            "## Issue Drafts\n" + issue_drafts_markdown(output.issue_drafts),
            "## Team Lead Notes\n" + markdown_list(output.team_lead_notes),
            "## Safety Notes\n" + markdown_list(output.safety_notes),
        ]
    )


def build_kickoff_markdown(output: ProjectKickoffOutput) -> str:
    return "\n\n".join(
        [
            "# Project Kickoff Packet",
            "## One-Line Pitch\n" + output.one_line_pitch,
            "## MVP Scope\n" + markdown_list(output.mvp_scope),
            "## Out of Scope\n" + markdown_list(output.out_of_scope),
            "## Workstreams\n" + markdown_list(output.workstreams),
            "## Risks\n" + markdown_list(output.risks),
            "## Open Questions\n" + markdown_list(output.open_questions),
            "## Role Discussion Questions\n" + markdown_list(output.role_discussion_questions),
            "## Issue Drafts\n" + issue_drafts_markdown(output.issue_drafts),
            "## Submission Checklist\n" + markdown_checklist(output.submission_checklist),
            "## Team Lead Notes\n" + markdown_list(output.team_lead_notes),
            "## Safety Notes\n" + markdown_list(output.safety_notes),
        ]
    )


def build_health_markdown(output: ProjectHealthOutput) -> str:
    return "\n\n".join(
        [
            "# Project Health Check",
            "## Summary\n" + output.summary,
            "## Scoreboard\n"
            + "\n".join(
                [
                    f"- MVP readiness: {output.mvp_completion_percent}%",
                    f"- Prototype readiness: {output.prototype_completion_percent}%",
                    f"- Stability: {output.stability_label} ({output.stability_score}/100)",
                    f"- Ownership status: {output.ownership_status}",
                ]
            ),
            "## Ownership Check\n" + markdown_list(output.ownership_notes + output.ownership_questions),
            "## Missing Meeting Items\n" + markdown_list(output.missing_meeting_items),
            "## Next Meeting Questions\n" + markdown_list(output.next_meeting_questions),
            "## MVP Signals\n" + health_signals_markdown(output.mvp_signals),
            "## Prototype Signals\n" + health_signals_markdown(output.prototype_signals),
            "## Risk Notes\n" + markdown_list(output.risk_notes),
            "## Safety Notes\n" + markdown_list(output.safety_notes),
        ]
    )


def markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items) if items else "- None"


def markdown_checklist(items: list[str]) -> str:
    return "\n".join(f"- [ ] {item}" for item in items) if items else "- [ ] None"


def issue_drafts_markdown(drafts: list[IssueDraft]) -> str:
    if not drafts:
        return "- No issue draft generated."
    blocks = []
    for draft in drafts:
        blocks.append(
            "\n".join(
                [
                    f"### {draft.title}",
                    "",
                    "**Labels:** " + ", ".join(f"`{label}`" for label in draft.labels),
                    "",
                    draft.body,
                ]
            )
        )
    return "\n\n".join(blocks)


def health_signals_markdown(signals: list[HealthSignal]) -> str:
    lines = []
    for signal in signals:
        mark = "x" if signal.detected else " "
        lines.append(f"- [{mark}] {signal.name} (+{signal.weight})")
        for item in signal.evidence:
            lines.append(f"  - evidence: {item}")
        if not signal.detected and signal.missing_message:
            lines.append(f"  - missing: {signal.missing_message}")
    return "\n".join(lines) if lines else "- None"


def dedupe(items: Iterable[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result
