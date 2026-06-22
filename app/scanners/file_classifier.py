from __future__ import annotations

from pathlib import Path

from app.schemas.capsule_schema import FileKind

DOC_EXTENSIONS = {".md", ".txt", ".rst"}
CODE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".kt", ".go", ".rs"}
CONFIG_NAMES = {
    "requirements.txt",
    "pyproject.toml",
    "package.json",
    "docker-compose.yml",
    "Dockerfile",
    ".env.example",
    "nginx.conf",
}
TEST_HINTS = {"test_", "_test", ".spec.", ".test."}


def classify_file(path: Path) -> FileKind:
    name = path.name
    lower_name = name.lower()

    if name in CONFIG_NAMES or path.suffix in {".yml", ".yaml", ".toml", ".json", ".ini"}:
        return FileKind.CONFIG

    if path.suffix.lower() in DOC_EXTENSIONS:
        return FileKind.DOC

    if any(hint in lower_name for hint in TEST_HINTS):
        return FileKind.TEST

    if path.suffix.lower() in CODE_EXTENSIONS:
        return FileKind.CODE

    return FileKind.UNKNOWN
