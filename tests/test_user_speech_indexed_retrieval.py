from app.retrievers.persistent_index import build_retrieval_index
from app.scanners.repo_scanner import scan_repo
from app.schemas.capsule_schema import RetrievalMode, RiskKind
from app.services.capsule_service import generate_capsule_result
from scripts.validate_user_speech import run_validation, user_speech_cases


def write_user_speech_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    write(repo / "README.md", "# Context Capsule\nportfolio readme handoff docs\n" * 20)
    write(repo / "docs" / "local_app.md", "local app launcher run_context_capsule dashboard guide\n" * 20)
    write(repo / "docs" / "v0.2_scrum_kickoff_modes.md", "scrum kickoff presentation script slide demo rehearsal\n" * 20)
    write(repo / "docs" / "reports" / "performance_comparison.md", "token reduction performance report baseline\n" * 20)
    write(repo / "app" / "retrievers" / "simple_retriever.py", "def retrieve_relevant_chunks():\n    return 'retriever vector search'\n")
    write(repo / "tests" / "test_simple_retriever.py", "def test_simple_retriever():\n    assert True\n")
    write(repo / "app" / "adapters" / "github_issue_adapter.py", "def create_issue_from_packet():\n    return 'github issue'\n")
    write(repo / "app" / "cli.py", "def create_issue_command():\n    return 'create-issue cli'\n")
    write(repo / "run_context_capsule.bat", "python -m streamlit run app/main.py\n")
    write(repo / "scripts" / "run_dashboard.ps1", "python -m streamlit run app/main.py\n")
    write(repo / "app" / "main.py", "def render_dashboard():\n    return 'streamlit dashboard local run'\n")
    write(repo / "app" / "analyzers" / "token_analyzer.py", "def analyze_token_budget():\n    return 'token budget baseline'\n")
    write(repo / "scripts" / "generate_performance_report.py", "def build_markdown():\n    return 'performance token report'\n")
    write(repo / "app" / "analyzers" / "meeting_analyzer.py", "def analyze_scrum_notes():\n    return 'scrum notes kickoff meeting'\n")
    write(repo / "app" / "generators" / "capsule_generator.py", "def build_markdown():\n    return 'output text copy'\n")
    write(repo / "app" / "generators" / "output_writer.py", "def save_output_packet():\n    return 'output file writer'\n")
    write(repo / "app" / "auth.py", "def login():\n    return 'jwt auth token'\n")
    write(repo / "app" / "models" / "user.py", "class User:\n    pass\n")
    return repo


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def generate(repo, task):
    return generate_capsule_result(
        repo_path=repo,
        task_request=task,
        retriever_mode=RetrievalMode.INDEXED,
    ).capsule


def paths(capsule, limit=5):
    return [chunk.path for chunk in capsule.relevant_chunks[:limit]]


def test_korean_user_speech_indexed_retrieval_targets_expected_files(tmp_path):
    repo = write_user_speech_repo(tmp_path)
    build_retrieval_index(scan_repo(repo), repo)

    cases = [
        ("리드미 손보자", {"README.md"}, 3),
        ("README 포폴용으로 다듬자", {"README.md"}, 3),
        ("심플 리트리버 왜 이럼", {"app/retrievers/simple_retriever.py"}, 3),
        ("simple_retriever에 벡터 검색 추가", {"app/retrievers/simple_retriever.py"}, 3),
        ("깃헙 이슈 생성 안됨", {"app/cli.py", "app/adapters/github_issue_adapter.py"}, 5),
        ("로컬 실행 안돼", {"run_context_capsule.bat", "scripts/run_dashboard.ps1", "docs/local_app.md"}, 5),
        (
            "토큰 계산 뻥튀기 같은데?",
            {"app/analyzers/token_analyzer.py", "docs/reports/performance_comparison.md"},
            5,
        ),
    ]

    for task, expected_paths, limit in cases:
        capsule = generate(repo, task)

        assert capsule.retrieval_report.used_mode == "indexed"
        assert capsule.token_budget.baseline_context_scope == "retrieved_file_contents"
        assert expected_paths <= set(paths(capsule, limit)), (task, paths(capsule, limit))


def test_protected_domains_are_not_treated_as_targets(tmp_path):
    repo = write_user_speech_repo(tmp_path)
    build_retrieval_index(scan_repo(repo), repo)

    capsule = generate(repo, "auth는 건드리지 말고 문서만 바꾸자")

    assert "auth" in capsule.request_understanding.protected_hints
    assert "README.md" in paths(capsule, 3) or "docs/local_app.md" in paths(capsule, 3)
    assert "app/auth.py" not in paths(capsule, 5)
    assert not any(finding.kind == RiskKind.CHANGE for finding in capsule.risk_findings)


def test_output_request_can_protect_db(tmp_path):
    repo = write_user_speech_repo(tmp_path)
    build_retrieval_index(scan_repo(repo), repo)

    capsule = generate(repo, "DB쪽은 냅두고 출력 문구만 바꾸자")

    assert "db" in capsule.request_understanding.protected_hints
    assert "app/models/user.py" not in paths(capsule, 5)
    assert {
        "app/generators/capsule_generator.py",
        "app/generators/output_writer.py",
    } & set(paths(capsule, 5))


def test_ambiguous_user_speech_stops_and_asks_question(tmp_path):
    repo = write_user_speech_repo(tmp_path)
    build_retrieval_index(scan_repo(repo), repo)

    for task in ("이거 왜그래?", "아까 그거 이어서 하자"):
        capsule = generate(repo, task)

        assert capsule.request_understanding.needs_clarification is True
        assert capsule.retrieval_report.used_mode == "clarification_only"
        assert capsule.token_budget.baseline_context_scope == "clarification_only"
        assert capsule.relevant_chunks == []
        assert capsule.request_understanding.clarification_question


def test_user_speech_qa_suite_covers_at_least_50_real_phrases(tmp_path):
    repo = write_user_speech_repo(tmp_path)

    results = run_validation(repo)

    assert len(user_speech_cases()) >= 50
    assert not [result for result in results if result.verdict == "FAIL"]
    assert any(result.hit_at_1 for result in results)
    assert any(result.retrieval_used_mode == "clarification_only" for result in results)
    assert not any(result.protected_false_positive for result in results)
