from pathlib import Path

from app.schemas.capsule_schema import RetrievalMode
from app.services.capsule_service import generate_capsule_result, summarize_generation_result


def write_nested_readme_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    write(repo / "README.md", "# Main Portfolio\n프로젝트 전체 소개와 검증 결과.\n" * 6)
    write(repo / "ai" / "liveportrait" / "driving" / "README.md", "# Driving Detail\n하위 모듈 실험 기록.\n" * 6)
    write(repo / "frontend-rn" / ".expo" / "README.md", "# Expo Internal\nGenerated internal folder.\n" * 6)
    write(repo / "docs" / "devlog" / "README.md", "# Dev Logs\n작업 기록.\n" * 6)
    return repo


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_guided_result_prioritizes_root_readme_for_portfolio_request(tmp_path):
    repo = write_nested_readme_repo(tmp_path)

    result = generate_capsule_result(
        repo_path=repo,
        task_request="리드미를 포트폴리오용으로 다듬어줘",
        retriever_mode=RetrievalMode.KEYWORD,
        top_k=8,
    )

    guide = result.guided_result
    assert guide is not None
    assert guide.primary_files == ["README.md"]
    assert "root README.md" in guide.first_action
    assert any(path.endswith("README.md") and path != "README.md" for path in guide.supporting_files)
    assert "참고" in guide.first_action


def test_guided_result_is_exposed_in_generation_summary(tmp_path):
    repo = write_nested_readme_repo(tmp_path)

    result = generate_capsule_result(
        repo_path=repo,
        task_request="리드미 손보자",
        retriever_mode=RetrievalMode.KEYWORD,
    )
    summary = summarize_generation_result(result)

    assert summary["guided_result"]["primary_files"] == ["README.md"]
    assert summary["guided_result"]["reading_order"][:5] == ["요약", "추천 첫 행동", "근거 파일", "충돌/위험", "복붙 프롬프트"]
