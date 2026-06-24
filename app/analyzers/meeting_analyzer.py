from __future__ import annotations

import re
from collections.abc import Iterable

from app.schemas.capsule_schema import IssueDraft, ProjectKickoffOutput, ScrumNotesOutput


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


def dedupe(items: Iterable[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result
