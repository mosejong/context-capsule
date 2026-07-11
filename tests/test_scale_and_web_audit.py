from scripts.audit_scale_and_web import audit_scale, audit_web, build_markdown, create_synthetic_repo


def test_scale_audit_measures_generated_repo(tmp_path):
    repo = create_synthetic_repo(tmp_path, 40)

    result = audit_scale(repo, 40)

    assert result.requested_files == 40
    assert result.included_files == 40
    assert result.truncated is False
    assert result.elapsed_seconds >= 0
    assert result.peak_memory_mb >= 0


def test_app_web_audit_selects_explicit_path(tmp_path):
    repo = create_synthetic_repo(tmp_path, 20)

    result = audit_web(repo)

    assert result.health_status == 200
    assert result.handoff_status == 200
    assert result.app_web_selected is True


def test_audit_report_states_scanner_cap(tmp_path):
    repo = create_synthetic_repo(tmp_path, 10)
    scale = audit_scale(repo, 10)
    web = audit_web(repo)

    markdown = build_markdown([scale], web)

    assert "5,000 included files" in markdown
    assert "not a 10k full-scan claim" in markdown
