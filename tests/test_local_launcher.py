from pathlib import Path


def test_windows_launcher_files_exist():
    assert Path("run_context_capsule.bat").exists()
    assert Path("context_capsule_cli.bat").exists()
    assert Path("scripts/install_windows.ps1").exists()
    assert Path("scripts/run_dashboard.ps1").exists()
    assert Path("scripts/context_capsule_cli.ps1").exists()
    assert Path("docs/local_app.md").exists()


def test_dashboard_launcher_uses_localhost_and_venv():
    script = Path("scripts/run_dashboard.ps1").read_text(encoding="utf-8")

    assert ".venv\\Scripts\\python.exe" in script
    assert "--server.address" in script
    assert "localhost" in script
    assert "--server.port" in script


def test_bat_launcher_uses_execution_policy_bypass_only_for_local_script():
    launcher = Path("run_context_capsule.bat").read_text(encoding="utf-8")

    assert "ExecutionPolicy Bypass" in launcher
    assert "scripts\\run_dashboard.ps1" in launcher
