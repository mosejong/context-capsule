from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


CheckStatus = Literal["passed", "failed", "not_run"]
VerificationVerdict = Literal["PASS", "WARN", "BLOCKED"]


class TaskContract(BaseModel):
    """Read-only execution boundary generated before an AI coding task starts."""

    schema_version: str = "1.0"
    task: str
    allowed_paths: list[str] = Field(default_factory=list)
    forbidden_paths: list[str] = Field(default_factory=list)
    forbidden_rules: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    required_checks: list[str] = Field(
        default_factory=lambda: ["scope_review", "test_or_run_result", "acceptance_criteria_review"]
    )
    approval_required: bool = False
    strict_scope: bool = True
    source: str = "context_capsule"


class CheckResult(BaseModel):
    name: str
    status: CheckStatus = "not_run"
    evidence: str = ""


class ContractViolation(BaseModel):
    kind: Literal["forbidden_path", "outside_scope", "approval_missing", "check_failed"]
    message: str
    path: str | None = None


class VerificationResult(BaseModel):
    verdict: VerificationVerdict
    changed_paths: list[str] = Field(default_factory=list)
    violations: list[ContractViolation] = Field(default_factory=list)
    check_results: list[CheckResult] = Field(default_factory=list)
    missing_checks: list[str] = Field(default_factory=list)
    next_action: str
    summary: str

