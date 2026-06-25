from pathlib import Path


def test_fastapi_ui_shows_loading_in_result_area():
    html = Path("app/web/static/index.html").read_text(encoding="utf-8")
    script = Path("app/web/static/app.js").read_text(encoding="utf-8")

    assert "결과가 여기에 표시됩니다." in html
    assert "생성 중입니다." in html
    assert "요청을 분석하고 있습니다." in html
    assert "입력 내용을 정리하고 있습니다." in script
    assert "관련 파일과 회의 신호를 찾고 있습니다." in script
    assert "위험과 승인 항목을 확인하고 있습니다." in script
    assert "결과 패킷을 만들고 있습니다." in script
    assert "button.disabled = isBusy" in script


def test_fastapi_ui_links_korean_onboarding_and_feedback_loop():
    html = Path("app/web/static/index.html").read_text(encoding="utf-8")
    script = Path("app/web/static/app.js").read_text(encoding="utf-8")

    assert "Context Capsule v0.2.4" in html
    assert "START_HERE_KO.md" in html
    assert "피드백 리뷰" in html
    assert "이 결과가 이상했나요?" in html
    assert "기대한 파일" in html
    assert "다시 쓸 의향" in html
    assert "결과를 보는 순서가 명확했나요?" in html
    assert "작업 흐름 탭이 이해됐나요?" in html
    assert "/api/feedback" in script
    assert "/api/feedback-review" in script


def test_fastapi_ui_explains_token_evidence_honestly():
    script = Path("app/web/static/app.js").read_text(encoding="utf-8")

    assert "token.estimated_reduction_percent" in script
    assert "token.method" in script
    assert "token.verification_status" in script
    assert "토큰 추정 감소" in script


def test_fastapi_ui_shows_workflow_graph_trace():
    script = Path("app/web/static/app.js").read_text(encoding="utf-8")
    styles = Path("app/web/static/styles.css").read_text(encoding="utf-8")

    assert "작업 흐름" in script
    assert "renderGraphTrace(data.graph_trace)" in script
    assert "어떤 순서로 판단했는지" in script
    assert "현재 단계" in script
    assert "nodeLabel(trace.current_node)" in script
    assert "renderGraphEvidence" in script
    assert "statusLabel" in script
    assert "질문 필요" in script
    assert ".graph-step" in styles
    assert ".graph-blocked" in styles
    assert ".graph-needs_input" in styles
    assert ".status-blocked" in styles
    assert ".status-needs_input" in styles
