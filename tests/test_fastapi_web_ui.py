from fastapi.testclient import TestClient

from app.web.server import app


client = TestClient(app)


def test_fastapi_index_is_korean_first_ui():
    response = client.get("/")

    assert response.status_code == 200
    text = response.text
    assert "AI에게 작업 맡기기" in text
    assert "회의록 정리하기" in text
    assert "프로젝트 시작 준비하기" in text
    assert "준비도 점검" in text
    assert "피드백 모아보기" in text
    assert "하고 싶은 작업 입력칸" in text
    assert "내 담당 영역" in text
    assert "신입 개발자" in text
    assert "면접관" in text
    assert "작업 범위" in text
    assert "Primary handoff target" not in text
    assert "Task request 입력칸" not in text
    assert "외부 LLM" not in text


def test_fastapi_health_check_api_returns_scores_and_ownership():
    response = client.post(
        "/api/health-check",
        json={
            "project_context": "Context Capsule v0.2",
            "status_text": "FastAPI UI를 만들고 pytest 85 passed. README와 실행 가이드를 정리했다.",
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
            "task_request": "리드미 포폴용",
            "forbidden_rules": "secret/env 값 출력 금지",
            "top_k": 5,
            "retriever_mode": "keyword",
            "my_scope": "README, docs",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["relevant_files"]
    assert data["relevant_files"][0]["path"] == "README.md"
    assert "ai_handoff_prompt" in data["sections"]
    assert data["ownership_check"]["status"] == "likely_my_part"
    assert data["ownership_check"]["questions"]
    assert data["guided_result"]["primary_files"] == ["README.md"]
    assert data["guided_result"]["reading_order"][0] == "추천 첫 행동"
    assert data["graph_trace"]["workflow"] == "work_handoff"
    assert data["graph_trace"]["steps"][0]["node_id"] == "scan_repository"
    assert any(step["node_id"] == "review_gate" for step in data["graph_trace"]["steps"])


def test_fastapi_work_handoff_flags_possible_other_part(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    backend = repo / "backend" / "auth"
    backend.mkdir(parents=True)
    (backend / "login.py").write_text("def login():\n    return 'ok'\n", encoding="utf-8")

    response = client.post(
        "/api/work-handoff",
        json={
            "repo_path": str(repo),
            "task_request": "로그인 오류 고쳐줘",
            "top_k": 5,
            "retriever_mode": "keyword",
            "my_scope": "frontend UI",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["ownership_check"]["status"] in {"possibly_other_part", "needs_confirmation"}
    assert data["ownership_check"]["questions"]


def test_fastapi_feedback_api_saves_feedback(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    response = client.post(
        "/api/feedback",
        json={
            "version": "0.2.8",
            "mode": "work",
            "project_name": "Demo",
            "request_text": "로그인 안돼",
            "expected_files": ["backend/auth/login.py"],
            "actual_top_files": ["README.md"],
            "result_order_feedback": "먼저 뭘 봐야 하는지 조금 헷갈렸어요.",
            "workflow_trace_feedback": "작업 흐름 탭에서 왜 차단됐는지는 이해됐어요.",
            "confusing_part": "어디를 봐야 할지 헷갈렸어요.",
            "reuse_willingness": "보통",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["output_dir"]
    assert data["markdown_path"].endswith("FEEDBACK.md")


def test_fastapi_feedback_review_api_returns_priorities(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    client.post(
        "/api/feedback",
        json={
            "mode": "work",
            "request_text": "로그인 안돼",
            "expected_files": ["backend/auth/login.py"],
            "actual_top_files": ["README.md"],
            "confusing_part": "결과 탭이 헷갈렸어요.",
        },
    )

    response = client.post("/api/feedback-review", json={"feedback_root": "outputs/feedback"})

    assert response.status_code == 200
    data = response.json()
    assert data["feedback_count"] == 1
    assert data["next_patch_priorities"]
    assert data["regression_test_candidates"]

