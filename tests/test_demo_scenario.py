from scripts.demo_scenario import run_demo


def test_login_demo_scenario_creates_saved_packet_and_dry_run(tmp_path):
    result = run_demo(tmp_path, "mosejong/context-capsule")

    assert result["scenario"] == "login_api_error_handoff"
    assert result["dry_run"]["mode"] == "dry-run"
    assert result["dry_run"]["repository"] == "mosejong/context-capsule"
    assert result["dry_run"]["payload"]["title"]
    assert result["token_budget"]["method"] == "approx_local_v1"
    assert result["token_budget"]["estimated_reduction_percent"] > 0
    assert "backend/auth/router.py" in result["retrieved_paths"]
