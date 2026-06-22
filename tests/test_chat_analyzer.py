from app.analyzers.chat_analyzer import extract_task_request


def test_extracts_error_task_from_chat_log():
    chat_log = """
    나: 어떤 에러났는데 뭐야?
    Traceback: ValueError in app/analyzers/risk_analyzer.py
    tests/test_risk_analyzer.py failed
    """

    extraction = extract_task_request(chat_log)

    assert "오류 원인" in extraction.task_request
    assert "app/analyzers/risk_analyzer.py" in extraction.detected_paths
    assert "tests/test_risk_analyzer.py" in extraction.detected_paths
    assert extraction.error_hints
    assert extraction.confidence >= 0.7


def test_extracts_decision_task_from_chat_log():
    chat_log = """
    모세종: Discord 회의에서 아이디어 픽스되면 GitHub Issue 만들자
    496: 오 너무 좋은데요
    모세종: 이걸로 가자
    """

    extraction = extract_task_request(chat_log)

    assert "작업 브리프" in extraction.task_request
    assert extraction.decision_hints
    assert extraction.confidence >= 0.45
