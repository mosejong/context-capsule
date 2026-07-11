import tomllib
from pathlib import Path

from app.schemas.capsule_schema import BetaFeedback
from app.version import __version__
from app.web.server import health


def test_active_version_surfaces_match():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    build_script = Path("scripts/build_release.ps1").read_text(encoding="utf-8")

    assert __version__ == "0.5.0"
    assert pyproject["project"]["version"] == __version__
    assert BetaFeedback().version == __version__
    assert health()["version"] == __version__
    assert f'[string]$Version = "{__version__}"' in build_script

