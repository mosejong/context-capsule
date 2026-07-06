from app.schemas.capsule_schema import HandoffTarget
from app.services.capsule_service import generate_capsule_result, summarize_generation_result


def write_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\nA login service.\n" * 30, encoding="utf-8")
    (repo / "auth.py").write_text("jwt login response schema", encoding="utf-8")
    return repo


def test_generate_capsule_result_can_save_packet(tmp_path):
    repo = write_repo(tmp_path)

    result = generate_capsule_result(
        repo_path=repo,
        task_request="Create login API handoff",
        forbidden_rules=["Do not edit secrets"],
        handoff_target=HandoffTarget.AI_TOOL,
        save=True,
        output_root=tmp_path / "outputs",
    )
    summary = summarize_generation_result(result)

    assert result.scanned_file_count == 2
    assert result.saved_packet is not None
    assert (result.saved_packet.output_dir / "GITHUB_ISSUE.md").exists()
    assert summary["saved_output_dir"] == str(result.saved_packet.output_dir)
    assert summary["github_issue"]["title"]
    assert summary["retriever_mode"] == "keyword"
    assert summary["token_budget"]["method"] == "approx_local_v1"
    assert summary["graph_trace"]["workflow"] == "work_handoff"
    assert summary["graph_trace"]["steps"][-1]["node_id"] == "save_output"


def test_generation_summary_json_contract_for_capsule_router(tmp_path):
    repo = write_repo(tmp_path)

    result = generate_capsule_result(
        repo_path=repo,
        task_request="Create login API handoff",
        handoff_target=HandoffTarget.AI_TOOL,
        save=True,
        output_root=tmp_path / "outputs",
    )
    summary = summarize_generation_result(result)

    expected_top_level = {
        "task_request",
        "request_understanding",
        "handoff_target",
        "retriever_mode",
        "retrieval_report",
        "scanned_file_count",
        "scan_report",
        "saved_output_dir",
        "github_issue",
        "token_budget",
        "ownership_check",
        "guided_result",
        "relevant_paths",
        "risk_findings",
        "graph_trace",
    }
    assert expected_top_level.issubset(summary)
    assert {
        "included_file_count",
        "skipped_file_count",
        "total_bytes",
        "truncated",
        "risk_level",
        "warnings",
    }.issubset(summary["scan_report"])
    assert {
        "title",
        "recommended_branch",
        "labels",
        "risk_level",
        "auto_start_allowed",
        "block_reason",
        "acceptance_criteria",
    }.issubset(summary["github_issue"])
    assert {
        "raw_context_tokens",
        "retrieved_context_tokens",
        "handoff_prompt_tokens",
        "estimated_reduction_percent",
        "method",
        "baseline_context_scope",
        "verification_status",
        "actual_provider_usage",
    }.issubset(summary["token_budget"])
    assert isinstance(summary["saved_output_dir"], str)
    assert isinstance(summary["relevant_paths"], list)
    assert isinstance(summary["github_issue"]["risk_level"], str)
    assert isinstance(summary["token_budget"]["estimated_reduction_percent"], float)
