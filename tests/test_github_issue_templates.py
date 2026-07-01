from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ISSUE_TEMPLATE_DIR = ROOT / ".github" / "ISSUE_TEMPLATE"


def read_template(name: str) -> str:
    return (ISSUE_TEMPLATE_DIR / name).read_text(encoding="utf-8")


def assert_required_field(template: str, field_id: str) -> None:
    marker = f"    id: {field_id}"
    assert marker in template
    field_section = template.split(marker, 1)[1].split("  - type:", 1)[0]
    assert "required: true" in field_section


def test_beta_feedback_issue_template_has_required_collection_fields():
    template = read_template("beta-feedback.yml")

    assert 'name: KDT beta feedback' in template
    assert 'labels: ["beta-feedback"]' in template
    assert "처음 쓰는 사람이 어디서 막히는지" in template
    assert ".env" in template
    assert "API key" in template
    assert "GitHub token" in template

    assert_required_field(template, "version")
    assert_required_field(template, "repo_type")
    assert_required_field(template, "request_text")

    for field_id in [
        "environment",
        "expected_files",
        "actual_files",
        "risk_conflict",
        "prompt_usefulness",
        "confusion",
        "reuse",
        "notes",
    ]:
        assert f"    id: {field_id}" in template


def test_bug_report_issue_template_has_repro_and_actual_result_fields():
    template = read_template("bug-report.yml")

    assert "name: Bug report" in template
    assert 'labels: ["bug"]' in template
    assert "secret" in template
    assert ".env" in template

    assert_required_field(template, "version")
    assert_required_field(template, "area")
    assert_required_field(template, "steps")
    assert_required_field(template, "actual")

    for option in [
        "설치/실행",
        "파일 검색",
        "위험/충돌 표시",
        "복붙 프롬프트",
        "GitHub Issue dry-run",
        "Scrum/Kickoff/Health",
        "피드백 저장/리뷰",
    ]:
        assert f"        - {option}" in template


def test_issue_template_config_links_to_release_and_quickstart():
    template = read_template("config.yml")

    assert "blank_issues_enabled: true" in template
    assert "https://github.com/mosejong/context-capsule/releases/latest" in template
    assert "docs/kdt_beta_quickstart.md" in template
