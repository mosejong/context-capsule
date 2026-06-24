from pathlib import Path


def test_dashboard_shows_generation_status_in_result_area():
    source = Path("app/main.py").read_text(encoding="utf-8")

    assert "CAPSULE_LOADING_STEPS" in source
    assert "생성 중입니다. 결과는 이 영역에 표시됩니다." in source
    assert "저장소 파일을 스캔합니다." in source
    assert "요청 의도와 보호 영역을 해석합니다." in source
    assert "관련 파일 후보를 검색합니다." in source
    assert "위험 신호와 승인 체크리스트를 분석합니다." in source
    assert "대상별 작업 패킷을 생성합니다." in source
    assert 'disabled=st.session_state["capsule_is_generating"]' in source
    assert "생성 실패: 아래 안내를 확인하세요." in source


def test_dashboard_links_korean_onboarding():
    source = Path("app/main.py").read_text(encoding="utf-8")

    assert "START_HERE_KO.md" in source
    assert "한국어 설명서" in source
    assert "처음이면 대시보드만 써도 됩니다." in source
