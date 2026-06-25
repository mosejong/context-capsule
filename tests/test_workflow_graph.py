from pathlib import Path

from app.services.capsule_service import generate_capsule_result, summarize_generation_result


def write_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\nREADME portfolio guide\n" * 10, encoding="utf-8")
    (repo / "app.py").write_text("def login():\n    return 'ok'\n", encoding="utf-8")
    return repo


def statuses(result) -> dict[str, str]:
    return {step.node_id: step.status for step in result.graph_trace.steps}


def test_work_handoff_graph_trace_records_completed_flow(tmp_path):
    repo = write_repo(tmp_path)

    result = generate_capsule_result(
        repo_path=repo,
        task_request="리드미 손보자",
        save=True,
        output_root=tmp_path / "outputs",
    )
    trace = result.graph_trace

    assert trace is not None
    assert trace.workflow == "work_handoff"
    assert trace.final_status == "completed"
    assert trace.current_node == "save_output"
    assert statuses(result) == {
        "scan_repository": "completed",
        "understand_request": "completed",
        "retrieve_context": "completed",
        "analyze_risk": "completed",
        "generate_packet": "completed",
        "review_gate": "completed",
        "save_output": "completed",
    }
    assert any("external AI" in note for note in trace.safety_notes)


def test_work_handoff_graph_trace_stops_for_ambiguous_request(tmp_path):
    repo = write_repo(tmp_path)

    result = generate_capsule_result(repo_path=repo, task_request="이거 왜그래?")
    step_statuses = statuses(result)

    assert result.graph_trace.final_status == "needs_input"
    assert result.graph_trace.current_node == "understand_request"
    assert step_statuses["understand_request"] == "needs_input"
    assert step_statuses["retrieve_context"] == "skipped"
    assert step_statuses["analyze_risk"] == "skipped"
    assert step_statuses["review_gate"] == "needs_input"


def test_work_handoff_graph_trace_blocks_secret_change_request(tmp_path):
    repo = write_repo(tmp_path)

    result = generate_capsule_result(repo_path=repo, task_request="JWT secret/env 값을 수정해줘")
    step_statuses = statuses(result)

    assert result.graph_trace.final_status == "blocked"
    assert result.graph_trace.current_node == "analyze_risk"
    assert step_statuses["analyze_risk"] == "blocked"
    assert step_statuses["review_gate"] == "blocked"


def test_summary_json_includes_graph_trace(tmp_path):
    repo = write_repo(tmp_path)

    result = generate_capsule_result(repo_path=repo, task_request="리드미 손보자")
    summary = summarize_generation_result(result)

    assert summary["graph_trace"]["workflow"] == "work_handoff"
    assert summary["graph_trace"]["steps"]
    assert summary["graph_trace"]["steps"][0]["node_id"] == "scan_repository"
