from pathlib import Path

from app.analyzers.meeting_analyzer import analyze_project_kickoff, analyze_scrum_notes


FIXTURE_DIR = Path(__file__).parent / "fixtures"


def test_scrum_notes_extracts_decisions_actions_and_safety_notes():
    output = analyze_scrum_notes(
        """
        Coach: MVP scope should be reduced and deployment is deferred.
        Team: Login API handoff packet is the next priority.
        Team: Release notes and Streamlit demo should be ready.
        Question: Which features should be deferred?
        """,
        project_context="Context Capsule v0.2.0",
    )

    assert output.decisions
    assert output.direction_changes
    assert output.next_actions
    assert output.issue_drafts
    assert output.role_discussion_questions
    assert any("No automatic assignment" in note for note in output.safety_notes)
    assert any("human team lead" in note for note in output.team_lead_notes)
    assert "Scrum Notes Packet" in output.markdown
    assert "Role Discussion Questions" in output.markdown


def test_scrum_notes_handles_anonymized_discord_runtime_issue():
    output = analyze_scrum_notes(
        """
        배경이미지가 생성됐다고 나오는데 저장이 안 되고 게임 화면에는 검은색으로 나와요.
        로그에도 저장 위치가 안 찍혀요.
        확인해보니 그래픽카드 사양 때문에 3분 timeout을 넘겨서 생성이 실패한 것 같습니다.
        일단 timeout 시간을 늘려서 다시 테스트해볼게요.
        """,
        project_context="Anonymous KDT project feedback",
    )

    assert output.blockers
    assert output.next_actions
    assert output.issue_drafts
    assert output.role_discussion_questions
    assert any("timeout" in item.lower() for item in output.decisions + output.next_actions + output.blockers)
    assert any("저장" in item or "로그" in item for item in output.blockers + output.next_actions)
    assert any("No automatic assignment" in note for note in output.safety_notes)


def test_scrum_notes_handles_anonymized_presentation_coordination():
    output = analyze_scrum_notes(
        """
        대본 완성했는데 확인 가능하신 분?
        평가 리포트 부분은 지금 바로 추가할게요.
        ppt랑 대본이랑 다른 부분이 많아요.
        내일 아침에 시간 있으니까 그때 대본 맞춰보시죠.
        """,
        project_context="Anonymous presentation prep",
    )

    assert output.open_questions
    assert output.next_actions
    assert output.issue_drafts
    assert any("평가 리포트" in item for item in output.next_actions + output.decisions)
    assert any("대본" in item for item in output.next_actions + output.open_questions)
    assert any("Final assignment stays" in note for note in output.team_lead_notes)


def test_project_kickoff_builds_scope_and_keeps_assignment_human():
    output = analyze_project_kickoff(
        topic="Scrum-to-execution planning tool",
        idea_notes="""
        Build Scrum Notes Mode and Project Kickoff Mode.
        Discord API can wait until after text-input MVP.
        Avoid teammate scoring or automatic assignment.
        Need README, tests, issue drafts, and presentation flow.
        """,
        deadline="2 weeks",
        constraints="No people scoring. No automatic assignment.",
        team_context="Members will self-report capacity before assignment.",
    )

    assert output.one_line_pitch == "Scrum-to-execution planning tool"
    assert output.mvp_scope
    assert output.out_of_scope
    assert output.workstreams
    assert output.issue_drafts
    assert output.role_discussion_questions
    assert output.safety_notes
    assert any("Deadline is confirmed: 2 weeks." == item for item in output.submission_checklist)
    assert any("Final assignment stays" in note for note in output.team_lead_notes)
    assert "Project Kickoff Packet" in output.markdown
    assert "Role Discussion Questions" in output.markdown
    assert "Safety Notes" in output.markdown


def test_scrum_notes_fixture_creates_reviewable_work_packet():
    meeting_text = (FIXTURE_DIR / "scrum_runtime_issue_ko.txt").read_text(encoding="utf-8")

    output = analyze_scrum_notes(meeting_text, project_context="Anonymous game project")

    assert any("timeout" in item.lower() for item in output.blockers + output.next_actions + output.decisions)
    assert any("저장" in item or "로그" in item for item in output.next_actions + output.blockers)
    assert output.issue_drafts
    assert output.role_discussion_questions
    assert all("Do not auto-assign" in draft.body for draft in output.issue_drafts)
    assert "No automatic teammate scoring" in output.markdown


def test_project_kickoff_fixture_keeps_discord_and_assignment_out_of_scope():
    idea_text = (FIXTURE_DIR / "project_kickoff_context_capsule_ko.txt").read_text(encoding="utf-8")

    output = analyze_project_kickoff(
        topic="Context Capsule v0.2",
        idea_notes=idea_text,
        deadline="2 weeks",
        constraints="No teammate scoring. No automatic assignment.",
        team_context="Team members self-report capacity manually.",
    )

    combined_out_of_scope = "\n".join(output.out_of_scope).lower()
    assert "discord" in combined_out_of_scope or "나중" in combined_out_of_scope
    assert any("automatic assignment" in item.lower() or "자동 역할 배정" in item for item in output.out_of_scope)
    assert output.role_discussion_questions
    assert output.issue_drafts
    assert all("needs-human-approval" in draft.labels for draft in output.issue_drafts)
    assert any("Meeting notes should be collected with participant awareness." in note for note in output.safety_notes)
