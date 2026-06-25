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


def write_planning_docs_repo(tmp_path):
    repo = tmp_path / "planning_docs"
    repo.mkdir()
    write(repo / "README.md", "# Planning Demo\nRoot portfolio entry.\n")
    write(repo / "event_judgement_system.md", "이벤트 판정 시스템 기획서 자료입니다.\n" * 5)
    write(repo / "npc_schedule_system.md", "NPC 스케줄 시스템 기획서 자료입니다.\n" * 5)
    write(repo / "test" / "test1.json", '{"purpose": "기획서 검증 자료", "type": "json"}\n')
    write(repo / "test" / "test2.json", '{"purpose": "기획서 테스트 fixture", "type": "json"}\n')
    return repo


def write_nested_readme_repo(tmp_path):
    repo = tmp_path / "nested_readmes"
    repo.mkdir()
    write(repo / "README.md", "# Main Portfolio\n프로젝트 전체 소개와 검증 결과.\n" * 4)
    write(repo / "ai" / "liveportrait" / "driving" / "README.md", "# Driving Detail\n하위 모듈 실험 기록.\n" * 4)
    write(repo / "frontend-rn" / ".expo" / "README.md", "# Expo Internal\nGenerated internal folder.\n" * 4)
    write(repo / "docs" / "architecture.md", "# Architecture\n전체 구조와 흐름.\n" * 4)
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


@pytest.mark.parametrize("mode", [RetrievalMode.KEYWORD, RetrievalMode.HYBRID, RetrievalMode.INDEXED])
def test_explicit_md_scope_excludes_json_primary_candidates(tmp_path, mode):
    repo = write_planning_docs_repo(tmp_path)
    if mode == RetrievalMode.INDEXED:
        build_indexed_repo(repo)

    result = generate_capsule_result(
        repo,
        "전체 폴더의 md파일들을 확인하고 기획서.md를 하나 만들어줘",
        retriever_mode=mode,
        top_k=5,
    )
    top_paths = paths(result, 5)

    assert top_paths
    assert all(path.endswith(".md") for path in top_paths)
    assert not any(path.endswith(".json") for path in top_paths)


def test_json_exclusion_scope_keeps_json_out_of_primary_candidates(tmp_path):
    repo = write_planning_docs_repo(tmp_path)

    result = generate_capsule_result(
        repo,
        "전체 폴더를 확인하되 json은 보지 말고 기획서.md를 만들어줘",
        retriever_mode=RetrievalMode.KEYWORD,
        top_k=5,
    )

    assert not any(path.endswith(".json") for path in paths(result, 5))


@pytest.mark.parametrize("mode", [RetrievalMode.KEYWORD, RetrievalMode.HYBRID, RetrievalMode.INDEXED])
def test_portfolio_readme_request_prefers_root_readme_over_nested_readmes(tmp_path, mode):
    repo = write_nested_readme_repo(tmp_path)
    if mode == RetrievalMode.INDEXED:
        build_indexed_repo(repo)

    result = generate_capsule_result(repo, "리드미를 포트폴리오용으로 다듬어줘", retriever_mode=mode, top_k=5)

    assert paths(result, 3)[0] == "README.md"
