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
            "--my-scope",
            "app auth",
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
    assert generated["graph_trace"]["workflow"] == "work_handoff"
    assert generated["graph_trace"]["current_node"] == "save_output"
    assert generated["ownership_check"]["status"] == "likely_my_part"
    assert generated["guided_result"]["reading_order"][0] == "추천 첫 행동"
    assert generated["guided_result"]["first_action"]
    assert (output_dir / "AI_HANDOFF_PROMPT.md").exists()
    assert (output_dir / "GITHUB_ISSUE.md").exists()
    assert (output_dir / "metadata.json").exists()
    assert "Ownership Check" in (output_dir / "GITHUB_ISSUE.md").read_text(encoding="utf-8")

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


def test_cli_index_then_generate_indexed(tmp_path, capsys):
    repo = write_demo_repo(tmp_path)

    exit_code = main(["index", "--repo-path", str(repo), "--json"])

    captured = capsys.readouterr()
    assert exit_code == 0
    index_result = json.loads(captured.out)
    assert index_result["chunk_count"] > 0
    assert Path(index_result["index_path"]).exists()

    exit_code = main(
        [
            "generate",
            "--repo-path",
            str(repo),
            "--task",
            "Create a login API handoff packet",
            "--retriever",
            "indexed",
            "--json",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    generated = json.loads(captured.out)
    assert generated["retriever_mode"] == "indexed"
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
    assert data["role_discussion_questions"]
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
    assert data["role_discussion_questions"]
    assert data["safety_notes"]
    assert data["saved_output_dir"]
    assert (Path(data["saved_output_dir"]) / "PROJECT_KICKOFF.md").exists()


def test_cli_health_json_and_save(tmp_path, capsys):
    output_root = tmp_path / "outputs"
    fixture = Path("tests/fixtures/project_health_status_ko.txt")

    exit_code = main(
        [
            "health",
            "--text-file",
            str(fixture),
            "--project-context",
            "Context Capsule v0.2",
            "--deadline",
            "주말 재테스트 전",
            "--my-scope",
            "README, START_HERE_KO.md, FastAPI UI",
            "--save",
            "--output-dir",
            str(output_root),
            "--json",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    data = json.loads(captured.out)
    assert data["mvp_completion_percent"] >= 40
    assert data["prototype_completion_percent"] >= 50
    assert data["ownership_status"] == "likely_my_part"
    assert data["missing_meeting_items"]
    assert data["next_meeting_questions"]
    assert data["saved_output_dir"]
    assert (Path(data["saved_output_dir"]) / "PROJECT_HEALTH.md").exists()


def test_cli_feedback_save_and_review_json(tmp_path, capsys):
    feedback_root = tmp_path / "feedback"

    exit_code = main(
        [
            "feedback-save",
            "--mode",
            "work",
            "--project-name",
            "Shop app",
            "--request",
            "로그인이 모바일에서만 안돼",
            "--expected-file",
            "backend/auth/login.py",
            "--actual-file",
            "README.md",
            "--confusing-part",
            "결과 탭에서 어디를 봐야 하는지 헷갈렸어요.",
            "--token-evidence",
            "토큰 절감 기준이 궁금합니다.",
            "--result-order-feedback",
            "먼저 무엇을 봐야 하는지 헷갈렸습니다.",
            "--workflow-trace-feedback",
            "작업 흐름 탭에서 현재 단계가 어려웠습니다.",
            "--risk-result",
            "Risk MEDIUM",
            "--output-dir",
            str(feedback_root),
            "--json",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    saved = json.loads(captured.out)
    assert Path(saved["json_path"]).exists()

    exit_code = main(["feedback-review", "--feedback-root", str(feedback_root), "--json"])

    captured = capsys.readouterr()
    assert exit_code == 0
    review = json.loads(captured.out)
    assert review["feedback_count"] == 1
    assert review["missed_file_cases"]
    assert review["workflow_trace_questions"]
    assert review["next_patch_priorities"]


def test_cli_feedback_review_save_writes_packet(tmp_path, capsys):
    feedback_root = tmp_path / "feedback"
    output_root = tmp_path / "outputs"
    main(
        [
            "feedback-save",
            "--request",
            "리드미 손보자",
            "--expected-file",
            "README.md",
            "--actual-file",
            "README.md",
            "--output-dir",
            str(feedback_root),
        ]
    )
    capsys.readouterr()

    exit_code = main(
        [
            "feedback-review",
            "--feedback-root",
            str(feedback_root),
            "--save",
            "--output-dir",
            str(output_root),
            "--json",
        ]
    )

    captured = capsys.readouterr()
    assert exit_code == 0
    data = json.loads(captured.out)
    assert data["saved_output_dir"]
    assert (Path(data["saved_output_dir"]) / "FEEDBACK_REVIEW.md").exists()
