from __future__ import annotations

from pathlib import Path

from app.scanners.file_classifier import classify_file
from app.schemas.capsule_schema import FileKind, RepoFile

IGNORE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".streamlit",
    "dist",
    "build",
    ".next",
    "htmlcov",
    "outputs",
}

ALLOWED_KINDS = {FileKind.DOC, FileKind.CODE, FileKind.CONFIG, FileKind.TEST}


def scan_repo(repo_path: Path, max_file_size: int = 80_000) -> list[RepoFile]:
    """Scan a local repository and return readable files for capsule generation."""
    repo_path = repo_path.expanduser().resolve()
    if not repo_path.exists() or not repo_path.is_dir():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")

    files: list[RepoFile] = []
    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue
        if any(should_ignore_part(part) for part in path.parts):
            continue

        kind = classify_file(path)
        if kind not in ALLOWED_KINDS:
            continue

        try:
            size = path.stat().st_size
            if size > max_file_size:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        relative_path = str(path.relative_to(repo_path)).replace("\\", "/")
        files.append(RepoFile(path=relative_path, kind=kind, content=content, size=size))

    return sorted(files, key=lambda item: item.path)


def should_ignore_part(part: str) -> bool:
    return part in IGNORE_DIRS or part.endswith(".egg-info")
