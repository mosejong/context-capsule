from app.analyzers.meeting_analyzer import analyze_project_kickoff, analyze_scrum_notes


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
    assert any("No automatic assignment" in note for note in output.safety_notes)
    assert any("human team lead" in note for note in output.team_lead_notes)
    assert "Scrum Notes Packet" in output.markdown


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
    assert any("Deadline is confirmed: 2 weeks." == item for item in output.submission_checklist)
    assert any("Final assignment stays" in note for note in output.team_lead_notes)
    assert "Project Kickoff Packet" in output.markdown
