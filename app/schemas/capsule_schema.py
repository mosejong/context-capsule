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


class RiskKind(str, Enum):
    MENTION = "mention_risk"
    CHANGE = "change_risk"


class HandoffTarget(str, Enum):
    AI_TOOL = "ai_tool"
    TEAMMATE = "teammate"
    JUNIOR_DEVELOPER = "junior_developer"
    FUTURE_ME = "future_me"


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
    kind: RiskKind = RiskKind.CHANGE
    reason: str
    evidence: str | None = None
    path: str | None = None


class TokenBudget(BaseModel):
    raw_context_tokens: int = 0
    retrieved_context_tokens: int = 0
    handoff_prompt_tokens: int = 0
    estimated_reduction_percent: float = 0.0
    method: str = "approx_local_v1"
    verification_status: str = "Estimated only"
    actual_provider_usage: str = "Not measured yet"


class ChatTaskExtraction(BaseModel):
    task_request: str
    detected_paths: list[str] = Field(default_factory=list)
    error_hints: list[str] = Field(default_factory=list)
    decision_hints: list[str] = Field(default_factory=list)
    source_excerpt: str = ""
    confidence: float = 0.0


class CapsuleInput(BaseModel):
    repo_path: Path
    task_request: str = Field(min_length=1)
    forbidden_rules: list[str] = Field(default_factory=list)
    top_k: int = 8
    handoff_target: HandoffTarget = HandoffTarget.AI_TOOL


class HandoffSections(BaseModel):
    overview: str
    future_me_letter: str
    teammate_brief: str
    junior_guide: str
    ai_handoff_prompt: str
    risk_checklist: str


class CapsuleOutput(BaseModel):
    handoff_target: HandoffTarget
    project_summary: str
    task_request: str
    relevant_chunks: list[RepoChunk]
    risk_findings: list[RiskFinding]
    approval_checklist: list[str]
    token_budget: TokenBudget
    sections: HandoffSections
    handoff_prompt: str
    markdown: str


class ExecutionPacket(BaseModel):
    title: str
    issue_body: str
    decision_record: str
    auto_start_allowed: bool
    block_reason: str | None = None
    recommended_branch: str
    labels: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.LOW
    acceptance_criteria: list[str] = Field(default_factory=list)


OutputFormat = Literal["markdown", "json"]
