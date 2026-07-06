from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app.scanners.file_classifier import classify_file
from app.security.redaction import sanitize_untrusted_text
from app.schemas.capsule_schema import FileKind, RiskLevel, RepoFile

IGNORE_DIRS = {
    ".git",
    ".venv",
    ".build-venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".streamlit",
    ".context-capsule-index",
    "dist",
    "build",
    ".next",
    "htmlcov",
    "local-ko",
    "outputs",
}

ALLOWED_KINDS = {FileKind.DOC, FileKind.CODE, FileKind.CONFIG, FileKind.TEST}
DEFAULT_MAX_FILE_SIZE = 80_000
DEFAULT_MAX_FILES = 5_000
DEFAULT_MAX_TOTAL_BYTES = 20_000_000


@dataclass(frozen=True)
class ScanWarning:
    code: str
    message: str
    risk_level: str = RiskLevel.MEDIUM.value
    path: str | None = None


@dataclass(frozen=True)
class RepoScanReport:
    files: list[RepoFile]
    included_file_count: int
    skipped_file_count: int = 0
    total_bytes: int = 0
    truncated: bool = False
    warnings: list[ScanWarning] = field(default_factory=list)


def scan_repo(
    repo_path: Path,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
    max_files: int = DEFAULT_MAX_FILES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> list[RepoFile]:
    """Scan a local repository and return readable files for capsule generation."""
    return scan_repo_with_report(
        repo_path,
        max_file_size=max_file_size,
        max_files=max_files,
        max_total_bytes=max_total_bytes,
    ).files


def scan_repo_with_report(
    repo_path: Path,
    max_file_size: int = DEFAULT_MAX_FILE_SIZE,
    max_files: int = DEFAULT_MAX_FILES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> RepoScanReport:
    repo_path = repo_path.expanduser().resolve()
    if not repo_path.exists() or not repo_path.is_dir():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    files: list[RepoFile] = []
    warnings: list[ScanWarning] = []
    skipped_file_count = 0
    total_bytes = 0
    truncated = False
    for path in repo_path.rglob("*"):
        if path.is_symlink():
            skipped_file_count += 1
            warnings.append(
                ScanWarning(
                    code="symlink_skipped",
                    message="Skipped symlink during repository scan to avoid reading outside the repository root.",
                    risk_level=RiskLevel.MEDIUM.value,
                    path=safe_relative_path(path, repo_path),
                )
            )
            continue
        if not path.is_file():
            continue
        if any(should_ignore_part(part) for part in path.parts):
            continue

        kind = classify_file(path)
        if kind not in ALLOWED_KINDS:
            skipped_file_count += 1
            continue

        try:
            size = path.stat().st_size
            if size > max_file_size:
                skipped_file_count += 1
                continue
            if len(files) >= max_files:
                truncated = True
                warnings.append(
                    ScanWarning(
                        code="max_files_reached",
                        message=f"Repository scan stopped after {max_files} included files.",
                        risk_level=RiskLevel.MEDIUM.value,
                    )
                )
                break
            if total_bytes + size > max_total_bytes:
                truncated = True
                warnings.append(
                    ScanWarning(
                        code="max_total_bytes_reached",
                        message=f"Repository scan stopped before exceeding {max_total_bytes} total bytes.",
                        risk_level=RiskLevel.MEDIUM.value,
                    )
                )
                break
            raw_content = path.read_text(encoding="utf-8", errors="ignore")
            content = sanitize_untrusted_text(raw_content).text
        except OSError:
            skipped_file_count += 1
            continue

        relative_path = str(path.relative_to(repo_path)).replace("\\", "/")
        files.append(RepoFile(path=relative_path, kind=kind, content=content, size=size))
        total_bytes += size

    sorted_files = sorted(files, key=lambda item: item.path)
    return RepoScanReport(
        files=sorted_files,
        included_file_count=len(sorted_files),
        skipped_file_count=skipped_file_count,
        total_bytes=total_bytes,
        truncated=truncated,
        warnings=warnings,
    )


def should_ignore_part(part: str) -> bool:
    return part in IGNORE_DIRS or part.endswith(".egg-info")


def safe_relative_path(path: Path, repo_path: Path) -> str:
    try:
        return str(path.relative_to(repo_path)).replace("\\", "/")
    except ValueError:
        return str(path)
