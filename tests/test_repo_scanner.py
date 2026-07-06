import os

import pytest

from app.scanners.repo_scanner import scan_repo, scan_repo_with_report


def test_scan_repo_ignores_generated_output_packets(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\nlogin api\n", encoding="utf-8")

    output_dir = repo / "outputs" / "20260623_demo"
    output_dir.mkdir(parents=True)
    (output_dir / "CONTEXT_CAPSULE.md").write_text("secret auth schema", encoding="utf-8")
    (output_dir / "metadata.json").write_text('{"risk": "blocked"}', encoding="utf-8")

    files = scan_repo(repo)

    assert [file.path for file in files] == ["README.md"]


def test_scan_repo_ignores_egg_info_metadata(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\nlogin api\n", encoding="utf-8")

    egg_info = repo / "context_capsule.egg-info"
    egg_info.mkdir()
    (egg_info / "SOURCES.txt").write_text("app/retrievers/simple_retriever.py", encoding="utf-8")

    files = scan_repo(repo)

    assert [file.path for file in files] == ["README.md"]


def test_scan_repo_ignores_build_virtualenv(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\nlogin api\n", encoding="utf-8")

    build_venv = repo / ".build-venv" / "Lib" / "site-packages"
    build_venv.mkdir(parents=True)
    (build_venv / "installed_package.py").write_text("def noisy_dependency(): pass\n", encoding="utf-8")

    files = scan_repo(repo)

    assert [file.path for file in files] == ["README.md"]


def test_scan_repo_ignores_local_retrieval_index(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\nlogin api\n", encoding="utf-8")

    index_dir = repo / ".context-capsule-index"
    index_dir.mkdir()
    (index_dir / "retrieval_index.json").write_text('{"chunks": []}', encoding="utf-8")

    files = scan_repo(repo)

    assert [file.path for file in files] == ["README.md"]


def test_scan_repo_ignores_personal_korean_notes(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\nlogin api\n", encoding="utf-8")

    personal_notes = repo / "local-ko"
    personal_notes.mkdir()
    (personal_notes / "README.md").write_text("개인용 한글 설명서", encoding="utf-8")

    files = scan_repo(repo)

    assert [file.path for file in files] == ["README.md"]


def test_scan_repo_reports_max_file_cap_truncation(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    for index in range(3):
        (repo / f"file_{index}.md").write_text(f"# File {index}\n", encoding="utf-8")

    report = scan_repo_with_report(repo, max_files=2)

    assert len(report.files) == 2
    assert report.truncated is True
    assert report.warnings
    assert report.warnings[0].code == "max_files_reached"
    assert report.warnings[0].risk_level == "MEDIUM"


def test_scan_repo_reports_max_total_bytes_truncation(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "a.md").write_text("a" * 20, encoding="utf-8")
    (repo / "b.md").write_text("b" * 20, encoding="utf-8")

    report = scan_repo_with_report(repo, max_total_bytes=25)

    assert len(report.files) == 1
    assert report.truncated is True
    assert report.warnings[0].code == "max_total_bytes_reached"


def test_scan_repo_skips_symlink_to_outside_repo(tmp_path):
    repo = tmp_path / "repo"
    outside = tmp_path / "outside"
    repo.mkdir()
    outside.mkdir()
    (repo / "README.md").write_text("# Demo\n", encoding="utf-8")
    secret_file = outside / "secret.md"
    secret_file.write_text("DB_PASSWORD=outside-secret\n", encoding="utf-8")
    symlink_path = repo / "linked_secret.md"
    try:
        os.symlink(secret_file, symlink_path)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation unavailable in this environment: {exc}")

    report = scan_repo_with_report(repo)

    assert [file.path for file in report.files] == ["README.md"]
    assert any(warning.code == "symlink_skipped" for warning in report.warnings)
    assert "outside-secret" not in "\n".join(file.content for file in report.files)
