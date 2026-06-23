import json
from pathlib import Path

from app.cli import main


def write_packet(tmp_path):
    packet_dir = tmp_path / "packet"
    packet_dir.mkdir()
    (packet_dir / "GITHUB_ISSUE.md").write_text("# Issue\n\nBody", encoding="utf-8")
    (packet_dir / "metadata.json").write_text(
        json.dumps(
            {
                "task_request": "Fallback title",
                "github_issue": {
                    "title": "CLI dry-run issue",
                    "labels": ["context-capsule"],
                    "risk_level": "LOW",
                    "auto_start_allowed": True,
                },
            }
        ),
        encoding="utf-8",
    )
    return packet_dir


def test_cli_create_issue_dry_run(tmp_path, capsys):
    packet_dir = write_packet(tmp_path)

    exit_code = main(["create-issue", str(packet_dir), "--repo", "mosejong/context-capsule"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Dry-run" in captured.out
    assert "CLI dry-run issue" in captured.out


def test_cli_create_issue_json(tmp_path, capsys):
    packet_dir = write_packet(tmp_path)

    exit_code = main(["create-issue", str(packet_dir), "--repo", "mosejong/context-capsule", "--json"])

    captured = capsys.readouterr()
    assert exit_code == 0
    result = json.loads(captured.out)
    assert result["mode"] == "dry-run"
    assert result["repository"] == "mosejong/context-capsule"
    assert result["title"] == "CLI dry-run issue"


def write_demo_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\nLogin API project.\n" * 20, encoding="utf-8")
    app_dir = repo / "app"
    app_dir.mkdir()
    (app_dir / "auth.py").write_text("def login():\n    return {'access_token': 'demo'}\n", encoding="utf-8")
    return repo


def test_cli_generate_save_json_then_create_issue(tmp_path, capsys):
    repo = write_demo_repo(tmp_path)
    output_root = tmp_path / "outputs"

    exit_code = main(
        [
            "generate",
            "--repo-path",
            str(repo),
            "--task",
            "Create a login API handoff packet",
            "--target",
            "all",
            "--save",
            "--output-dir",
            str(output_root),
            "--json",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    generated = json.loads(captured.out)
    output_dir = Path(generated["saved_output_dir"])
    assert output_dir.exists()
    assert (output_dir / "AI_HANDOFF_PROMPT.md").exists()
    assert (output_dir / "GITHUB_ISSUE.md").exists()
    assert (output_dir / "metadata.json").exists()

    exit_code = main(["create-issue", str(output_dir), "--repo", "mosejong/context-capsule", "--json"])

    captured = capsys.readouterr()
    assert exit_code == 0
    dry_run = json.loads(captured.out)
    assert dry_run["mode"] == "dry-run"
    assert dry_run["payload"]["title"]


def test_cli_generate_supports_hybrid_retriever(tmp_path, capsys):
    repo = write_demo_repo(tmp_path)

    exit_code = main(
        [
            "generate",
            "--repo-path",
            str(repo),
            "--task",
            "Create a login API handoff packet",
            "--retriever",
            "hybrid",
            "--json",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    generated = json.loads(captured.out)
    assert generated["retriever_mode"] == "hybrid"
    assert generated["relevant_paths"]


def test_cli_scrum_notes_json_and_save(tmp_path, capsys):
    output_root = tmp_path / "outputs"

    exit_code = main(
        [
            "scrum-notes",
            "--text",
            "Coach: Reduce MVP scope. Team: Build release notes. Question: What is deferred?",
            "--project-context",
            "Context Capsule",
            "--save",
            "--output-dir",
            str(output_root),
            "--json",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    data = json.loads(captured.out)
    assert data["decisions"]
    assert data["next_actions"]
    assert data["saved_output_dir"]
    assert (Path(data["saved_output_dir"]) / "SCRUM_NOTES.md").exists()


def test_cli_kickoff_json_and_save(tmp_path, capsys):
    output_root = tmp_path / "outputs"

    exit_code = main(
        [
            "kickoff",
            "--topic",
            "Scrum-to-execution planning tool",
            "--notes",
            "Build Scrum Notes Mode. Discord API later. No automatic assignment.",
            "--deadline",
            "2 weeks",
            "--save",
            "--output-dir",
            str(output_root),
            "--json",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    data = json.loads(captured.out)
    assert data["mvp_scope"]
    assert data["issue_drafts"]
    assert data["saved_output_dir"]
    assert (Path(data["saved_output_dir"]) / "PROJECT_KICKOFF.md").exists()
