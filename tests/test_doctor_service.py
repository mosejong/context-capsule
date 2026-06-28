import json
from pathlib import Path

from app.cli import main
from app.services.doctor_service import build_doctor_report, is_supported_python, release_zip_sort_key


def write_product_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    write(repo / "README.md", "# Demo\n")
    write(repo / "pyproject.toml", "[project]\nname = 'demo'\nversion = '0.2.11'\n")
    write(repo / "requirements.txt", "streamlit\nfastapi\nuvicorn\n")
    write(repo / "app" / "main.py", "print('dashboard')\n")
    write(repo / "app" / "web" / "server.py", "print('fastapi')\n")
    write(repo / "app" / "web" / "static" / "index.html", "<h1>Context Capsule</h1>\n")
    write(repo / "app" / "cli.py", "print('cli')\n")
    write(repo / "run_context_capsule.bat", "python -m uvicorn app.web.server:app\n")
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
    assert "optional" in checks["indexed_retrieval"].detail.lower()


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


def test_python_version_policy_allows_311_and_newer():
    assert is_supported_python(3, 11)
    assert is_supported_python(3, 12)
    assert is_supported_python(3, 13)


def test_python_version_policy_rejects_310_and_older():
    assert not is_supported_python(3, 10)
    assert not is_supported_python(2, 7)


def test_doctor_prefers_current_release_zip(tmp_path):
    repo = write_product_repo(tmp_path)
    write(repo / "dist" / "context-capsule-v0.2.9.zip", "old")
    write(repo / "dist" / "context-capsule-v0.2.10.zip", "old-current")
    write(repo / "dist" / "context-capsule-v0.2.11.zip", "current")

    report = build_doctor_report(repo)
    checks = {check.name: check for check in report.checks}

    assert checks["release_zip"].status == "PASS"
    assert "v0.2.11.zip" in checks["release_zip"].detail


def test_doctor_warns_when_current_release_zip_is_missing(tmp_path):
    repo = write_product_repo(tmp_path)
    write(repo / "dist" / "context-capsule-v0.2.10.zip", "old")

    report = build_doctor_report(repo)
    checks = {check.name: check for check in report.checks}

    assert checks["release_zip"].status == "WARN"
    assert "Expected context-capsule-v0.2.11.zip" in checks["release_zip"].detail


def test_release_zip_sort_key_handles_semver_order():
    paths = [
        Path("context-capsule-v0.2.9.zip"),
        Path("context-capsule-v0.2.10.zip"),
        Path("context-capsule-v0.2.11.zip"),
        Path("context-capsule-v0.10.0.zip"),
    ]

    assert sorted(paths, key=release_zip_sort_key)[-1].name == "context-capsule-v0.10.0.zip"
