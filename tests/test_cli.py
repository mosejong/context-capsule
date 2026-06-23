import json

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
