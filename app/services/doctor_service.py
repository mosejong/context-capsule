from __future__ import annotations

import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from app.retrievers.persistent_index import default_index_path
from app.scanners.repo_scanner import scan_repo


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    status: str
    detail: str
    hint: str | None = None


@dataclass(frozen=True)
class DoctorReport:
    status: str
    repo_path: str
    python_version: str
    scanned_file_count: int
    checks: list[DoctorCheck]

    def to_dict(self) -> dict:
        data = asdict(self)
        data["checks"] = [asdict(check) for check in self.checks]
        return data


REQUIRED_FILES = (
    "README.md",
    "pyproject.toml",
    "requirements.txt",
    "app/main.py",
    "app/cli.py",
    "run_context_capsule.bat",
    "context_capsule_cli.bat",
)

IGNORED_LOCAL_PATHS = (
    "outputs/",
    ".context-capsule-index/",
)
MIN_PYTHON_MAJOR = 3
MIN_PYTHON_MINOR = 11


def build_doctor_report(repo_path: Path | str) -> DoctorReport:
    path = Path(repo_path).expanduser().resolve()
    checks: list[DoctorCheck] = []
    scanned_file_count = 0

    checks.append(check_python_version())
    if not path.exists() or not path.is_dir():
        checks.append(
            DoctorCheck(
                name="repo_path",
                status="FAIL",
                detail=f"Repository path does not exist or is not a directory: {path}",
                hint="Pass --repo-path with the Context Capsule repository path.",
            )
        )
        return DoctorReport(
            status=overall_status(checks),
            repo_path=str(path),
            python_version=python_version_text(),
            scanned_file_count=0,
            checks=checks,
        )

    checks.append(DoctorCheck(name="repo_path", status="PASS", detail=str(path)))
    checks.extend(check_required_files(path))

    try:
        scanned_file_count = len(scan_repo(path))
        checks.append(
            DoctorCheck(
                name="repo_scan",
                status="PASS" if scanned_file_count > 0 else "WARN",
                detail=f"Scanned files: {scanned_file_count}",
                hint="Check scanner ignore rules if this is unexpectedly low." if scanned_file_count == 0 else None,
            )
        )
    except Exception as exc:
        checks.append(
            DoctorCheck(
                name="repo_scan",
                status="FAIL",
                detail=str(exc),
                hint="Confirm the repository path is readable.",
            )
        )

    checks.append(check_local_index(path))
    checks.extend(check_gitignore(path))
    checks.append(check_release_zip(path))
    checks.append(
        DoctorCheck(
            name="external_ai_required",
            status="PASS",
            detail="No external AI API is required for scan/retrieval/risk/Markdown packet generation.",
        )
    )
    checks.append(
        DoctorCheck(
            name="github_write_safety",
            status="PASS",
            detail="GitHub Issue creation is dry-run by default and requires --apply for real writes.",
        )
    )

    return DoctorReport(
        status=overall_status(checks),
        repo_path=str(path),
        python_version=python_version_text(),
        scanned_file_count=scanned_file_count,
        checks=checks,
    )


def check_python_version() -> DoctorCheck:
    version = sys.version_info
    status = "PASS" if is_supported_python(version.major, version.minor) else "FAIL"
    return DoctorCheck(
        name="python_version",
        status=status,
        detail=python_version_text(),
        hint=f"Install or activate Python {MIN_PYTHON_MAJOR}.{MIN_PYTHON_MINOR} or newer." if status == "FAIL" else None,
    )


def is_supported_python(major: int, minor: int) -> bool:
    return major > MIN_PYTHON_MAJOR or (major == MIN_PYTHON_MAJOR and minor >= MIN_PYTHON_MINOR)


def check_required_files(repo_path: Path) -> list[DoctorCheck]:
    checks = []
    for relative_path in REQUIRED_FILES:
        candidate = repo_path / relative_path
        checks.append(
            DoctorCheck(
                name=f"required_file:{relative_path}",
                status="PASS" if candidate.exists() else "FAIL",
                detail="found" if candidate.exists() else "missing",
                hint=f"Expected file at {relative_path}." if not candidate.exists() else None,
            )
        )
    return checks


def check_local_index(repo_path: Path) -> DoctorCheck:
    index_path = default_index_path(repo_path)
    if index_path.exists():
        return DoctorCheck(name="indexed_retrieval", status="PASS", detail=f"Index exists: {index_path}")
    return DoctorCheck(
        name="indexed_retrieval",
        status="WARN",
        detail=f"Index not built yet: {index_path}. This is optional; keyword retrieval still works.",
        hint="Optional: run context_capsule_cli.bat index --repo-path . --json for persistent indexed retrieval.",
    )


def check_gitignore(repo_path: Path) -> list[DoctorCheck]:
    gitignore_path = repo_path / ".gitignore"
    if not gitignore_path.exists():
        return [
            DoctorCheck(
                name="gitignore",
                status="WARN",
                detail=".gitignore is missing.",
                hint="Generated outputs and local indexes should not be committed.",
            )
        ]

    text = gitignore_path.read_text(encoding="utf-8", errors="ignore")
    return [
        DoctorCheck(
            name=f"gitignore:{pattern}",
            status="PASS" if pattern in text else "WARN",
            detail="ignored" if pattern in text else "not listed",
            hint=f"Add {pattern} to .gitignore." if pattern not in text else None,
        )
        for pattern in IGNORED_LOCAL_PATHS
    ]


def check_release_zip(repo_path: Path) -> DoctorCheck:
    candidates = sorted((repo_path / "dist").glob("context-capsule-v*.zip")) if (repo_path / "dist").exists() else []
    if candidates:
        latest = candidates[-1]
        return DoctorCheck(name="release_zip", status="PASS", detail=f"Found {latest}")
    return DoctorCheck(
        name="release_zip",
        status="PASS",
        detail="No local release ZIP found under dist/. This is okay for downloaded/extracted app usage.",
        hint="Only publishers need to run scripts/build_release.ps1 before uploading a release asset.",
    )


def overall_status(checks: list[DoctorCheck]) -> str:
    statuses = {check.status for check in checks}
    if "FAIL" in statuses:
        return "FAIL"
    if "WARN" in statuses:
        return "WARN"
    return "PASS"


def python_version_text() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
