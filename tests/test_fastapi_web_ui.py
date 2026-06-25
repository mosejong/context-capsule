from fastapi.testclient import TestClient

from app.web.server import app


client = TestClient(app)


def test_fastapi_index_is_korean_first_ui():
    response = client.get("/")

    assert response.status_code == 200
    text = response.text
    assert "작업 하나 넘기기" in text
    assert "회의록 정리" in text
    assert "프로젝트 시작 정리" in text
    assert "준비도 점검" in text
    assert "작업 요청 입력칸" in text
    assert "내 담당 영역" in text
    assert "Primary handoff target" not in text


def test_fastapi_health_check_api_returns_scores_and_ownership():
    response = client.post(
        "/api/health-check",
        json={
            "project_context": "Context Capsule v0.2",
            "status_text": "FastAPI UI를 만들고 pytest 85 passed. README와 실행 가이드를 정리한다.",
            "deadline": "주말 재테스트 전",
            "my_scope": "FastAPI UI, README",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["mvp_completion_percent"] > 0
    assert data["prototype_completion_percent"] > 0
    assert data["ownership_status"] == "likely_my_part"
    assert data["next_meeting_questions"]


def test_fastapi_work_handoff_api_returns_relevant_files(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "README.md").write_text("# Demo\nREADME portfolio guide\n" * 10, encoding="utf-8")

    response = client.post(
        "/api/work-handoff",
        json={
            "repo_path": str(repo),
            "task_request": "리드미 손보자",
            "forbidden_rules": "secret/env 값 출력 금지",
            "top_k": 5,
            "retriever_mode": "keyword",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["relevant_files"]
    assert data["relevant_files"][0]["path"] == "README.md"
    assert "ai_handoff_prompt" in data["sections"]
