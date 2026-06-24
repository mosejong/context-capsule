import json
from pathlib import Path

from app.cli import main
from app.services.doctor_service import build_doctor_report


def write_product_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    write(repo / "README.md", "# Demo\n")
    write(repo / "pyproject.toml", "[project]\nname = 'demo'\n")
    write(repo / "requirements.txt", "streamlit\n")
    write(repo / "app" / "main.py", "print('dashboard')\n")
    write(repo / "app" / "cli.py", "print('cli')\n")
    write(repo / "run_context_capsule.bat", "python -m streamlit run app/main.py\n")
    write(repo / "context_capsule_cli.bat", "python -m app.cli %*\n")
    write(repo / ".gitignore", "outputs/\n.context-capsule-index/\n")
    return repo


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_doctor_report_passes_core_local_checks(tmp_path):
    repo = write_product_repo(tmp_path)

    report = build_doctor_report(repo)

    assert report.status == "WARN"
    assert report.scanned_file_count > 0
    checks = {check.name: check for check in report.checks}
    assert checks["repo_path"].status == "PASS"
    assert checks["required_file:README.md"].status == "PASS"
    assert checks["gitignore:outputs/"].status == "PASS"
    assert checks["indexed_retrieval"].status == "WARN"
    assert checks["external_ai_required"].status == "PASS"
    assert checks["github_write_safety"].status == "PASS"


def test_cli_doctor_json(tmp_path, capsys):
    repo = write_product_repo(tmp_path)

    exit_code = main(["doctor", "--repo-path", str(repo), "--json"])

    captured = capsys.readouterr()
    assert exit_code == 0
    data = json.loads(captured.out)
    assert data["status"] == "WARN"
    assert data["scanned_file_count"] > 0
    assert any(check["name"] == "indexed_retrieval" for check in data["checks"])


def test_cli_doctor_fails_for_missing_repo(tmp_path, capsys):
    missing = tmp_path / "missing"

    exit_code = main(["doctor", "--repo-path", str(missing), "--json"])

    captured = capsys.readouterr()
    assert exit_code == 1
    data = json.loads(captured.out)
    assert data["status"] == "FAIL"
    assert data["checks"][-1]["name"] == "repo_path"
