from app.scanners.repo_scanner import scan_repo


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
