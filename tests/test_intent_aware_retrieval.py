import pytest

from app.retrievers.persistent_index import build_retrieval_index
from app.scanners.repo_scanner import scan_repo
from app.schemas.capsule_schema import RetrievalMode, RiskLevel
from app.services.capsule_service import generate_capsule_result


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_indexed_repo(repo):
    build_retrieval_index(scan_repo(repo), repo)
    return repo


def paths(result, limit=8):
    return [chunk.path for chunk in result.capsule.relevant_chunks[:limit]]


def write_security_heavy_repo(tmp_path):
    repo = tmp_path / "security_heavy"
    repo.mkdir()
    write(repo / "README.md", "# Security-heavy Demo\nDocumentation entry point.\n")
    write(repo / "docs" / "auth.md", "Auth documentation. Do not change auth code.\n")
    write(
        repo / "app" / "request_understanding.py",
        "\n".join(
            [
                "def normalize_request(): pass",
                "auth jwt token db deploy secret " * 20,
                "AWS_ACCESS_KEY_ID = '" + "AKIA" + "1234FAKE5678SECRET'",
            ]
        ),
    )
    return repo


def write_launcher_repo(tmp_path):
    repo = tmp_path / "launcher_repo"
    repo.mkdir()
    write(repo / "README.md", "# Launcher Demo\n")
    write(repo / "docs" / "local_app.md", "Local app launcher guide for localhost and dashboard.\n" * 4)
    write(repo / "run_context_capsule.bat", "powershell scripts\\run_dashboard.ps1\n")
    write(repo / "scripts" / "run_dashboard.ps1", "python -m streamlit run app/main.py\n")
    write(repo / "scripts" / "install_windows.ps1", "python -m pip install -r requirements.txt\n")
    write(repo / "docker-compose.yml", "services:\n  app:\n    build: .\n")
    write(repo / "app" / "main.py", "def render_dashboard(): return 'streamlit dashboard local run'\n")
    write(repo / "app" / "runtime.py", "def boot(): return 'local run error handler'\n")
    return repo


@pytest.mark.parametrize("mode", [RetrievalMode.HYBRID, RetrievalMode.INDEXED])
def test_docs_only_request_excludes_code_chunks_before_risk_analysis(tmp_path, mode):
    repo = write_security_heavy_repo(tmp_path)
    if mode == RetrievalMode.INDEXED:
        build_indexed_repo(repo)

    result = generate_capsule_result(repo, "auth는 건드리지 말고 문서만 바꾸자", retriever_mode=mode)
    top_paths = paths(result)

    assert "README.md" in top_paths or "docs/auth.md" in top_paths
    assert not any(path.startswith("app/") or path.startswith("tests/") for path in top_paths)
    assert result.execution_packet.risk_level != RiskLevel.BLOCKED
    assert result.execution_packet.auto_start_allowed is True


def test_local_run_request_prefers_launcher_docs_and_config_before_code(tmp_path):
    repo = build_indexed_repo(write_launcher_repo(tmp_path))

    result = generate_capsule_result(repo, "로컬 실행 안돼", retriever_mode=RetrievalMode.INDEXED)
    top_paths = paths(result, 5)

    assert {
        "run_context_capsule.bat",
        "scripts/run_dashboard.ps1",
        "scripts/install_windows.ps1",
        "docker-compose.yml",
        "docs/local_app.md",
    } <= set(top_paths)
    assert not any(path.startswith("app/") for path in top_paths)
