from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field


class FileKind(str, Enum):
    DOC = "doc"
    CODE = "code"
    CONFIG = "config"
    TEST = "test"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    BLOCKED = "BLOCKED"


class RepoFile(BaseModel):
    path: str
    kind: FileKind
    content: str
    size: int = 0


class RepoChunk(BaseModel):
    path: str
    kind: FileKind
    text: str
    start_line: int | None = None
    end_line: int | None = None
    score: float = 0.0


class RiskFinding(BaseModel):
    level: RiskLevel
    reason: str
    evidence: str | None = None
    path: str | None = None


class CapsuleInput(BaseModel):
    repo_path: Path
    task_request: str = Field(min_length=1)
    forbidden_rules: list[str] = Field(default_factory=list)
    top_k: int = 8


class CapsuleOutput(BaseModel):
    project_summary: str
    task_request: str
    relevant_chunks: list[RepoChunk]
    risk_findings: list[RiskFinding]
    approval_checklist: list[str]
    handoff_prompt: str
    markdown: str


OutputFormat = Literal["markdown", "json"]
