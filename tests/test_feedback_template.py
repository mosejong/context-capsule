import json
from pathlib import Path

from app.cli import main
from app.generators.feedback_template_generator import build_feedback_template


def test_feedback_template_contains_beta_questions():
    template = build_feedback_template(project_name="Rainbow Bridge", tester_name="tester-a")

    assert template.project_name == "Rainbow Bridge"
    assert template.tester_name == "tester-a"
    assert "Context Capsule KDT Beta Feedback" in template.markdown
    assert "리드미 손보자" in template.markdown
    assert "Protected-Area Check" in template.markdown
    assert "Do not paste secrets" in template.markdown
    assert template.commands


def test_cli_feedback_template_json_and_save(tmp_path, capsys):
    output_root = tmp_path / "outputs"

    exit_code = main(
        [
            "feedback-template",
            "--project-name",
            "Rainbow Bridge",
            "--tester-name",
            "tester-a",
            "--save",
            "--output-dir",
            str(output_root),
            "--json",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    data = json.loads(captured.out)
    assert data["project_name"] == "Rainbow Bridge"
    assert data["tester_name"] == "tester-a"
    saved_output_dir = Path(data["saved_output_dir"])
    assert (saved_output_dir / "KDT_FEEDBACK_TEMPLATE.md").exists()
    saved_text = (saved_output_dir / "KDT_FEEDBACK_TEMPLATE.md").read_text(encoding="utf-8")
    assert "Rainbow Bridge" in saved_text
    assert "Issue dry-run" in saved_text
