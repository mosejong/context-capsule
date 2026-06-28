from pathlib import Path


def test_windows_launcher_files_exist():
    assert Path("run_context_capsule.bat").exists()
    assert Path("context_capsule_cli.bat").exists()
    assert Path("scripts/install_windows.ps1").exists()
    assert Path("scripts/run_dashboard.ps1").exists()
    assert Path("scripts/context_capsule_cli.ps1").exists()
    assert Path("app/web/server.py").exists()
    assert Path("app/web/static/index.html").exists()
    assert Path("docs/local_app.md").exists()


def test_dashboard_launcher_uses_fastapi_localhost_and_venv():
    script = Path("scripts/run_dashboard.ps1").read_text(encoding="utf-8")

    assert ".venv\\Scripts\\python.exe" in script
    assert "uvicorn" in script
    assert "app.web.server:app" in script
    assert "--host" in script
    assert "localhost" in script
    assert "--port" in script


def test_bat_launcher_uses_execution_policy_bypass_only_for_local_script():
    launcher = Path("run_context_capsule.bat").read_text(encoding="utf-8")

    assert "ExecutionPolicy Bypass" in launcher
    assert "scripts\\run_dashboard.ps1" in launcher


def test_windows_launcher_scripts_write_first_run_logs_and_korean_guidance():
    install_script = Path("scripts/install_windows.ps1").read_text(encoding="utf-8")
    dashboard_script = Path("scripts/run_dashboard.ps1").read_text(encoding="utf-8")
    cli_script = Path("scripts/context_capsule_cli.ps1").read_text(encoding="utf-8")
    launcher = Path("run_context_capsule.bat").read_text(encoding="utf-8")

    for text in (install_script, dashboard_script, cli_script):
        assert "outputs\\logs" in text
        assert "Write-FailureGuide" in text
        assert "START_HERE_KO.md" in text
        assert "docs\\local_app.md" in text

    assert "설치 중 문제가 발생했습니다." in install_script
    assert "실행 중 문제가 발생했습니다." in dashboard_script
    assert "CLI 실행 중 문제가 발생했습니다." in cli_script
    assert "outputs\\logs 폴더" in launcher
