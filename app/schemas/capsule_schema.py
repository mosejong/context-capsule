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


class RetrievalMode(str, Enum):
    KEYWORD = "keyword"
    HYBRID = "hybrid"
    INDEXED = "indexed"


class RetrievalReport(BaseModel):
    requested_mode: str = RetrievalMode.KEYWORD.value
    used_mode: str = RetrievalMode.KEYWORD.value
    fallback_reason: str | None = None
    index_path: str | None = None


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
    baseline_context_scope: str = "retrieved_file_contents"
    verification_status: str = "Estimated only"
    actual_provider_usage: str = "Not measured yet"


class ChatTaskExtraction(BaseModel):
    task_request: str
    detected_paths: list[str] = Field(default_factory=list)
    error_hints: list[str] = Field(default_factory=list)
    decision_hints: list[str] = Field(default_factory=list)
    source_excerpt: str = ""
    confidence: float = 0.0


class RequestUnderstanding(BaseModel):
    original_request: str = ""
    normalized_request: str = ""
    search_query: str = ""
    intent: str = "general"
    confidence: float = 0.0
    confidence_label: str = "low"
    target_hints: list[str] = Field(default_factory=list)
    protected_hints: list[str] = Field(default_factory=list)
    file_hints: list[str] = Field(default_factory=list)
    include_extensions: list[str] = Field(default_factory=list)
    exclude_extensions: list[str] = Field(default_factory=list)
    applied_aliases: list[str] = Field(default_factory=list)
    clarification_question: str | None = None
    needs_clarification: bool = False


class IssueDraft(BaseModel):
    title: str
    body: str
    labels: list[str] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)


class ScrumNotesOutput(BaseModel):
    source_summary: str
    decisions: list[str] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    direction_changes: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    role_discussion_questions: list[str] = Field(default_factory=list)
    issue_drafts: list[IssueDraft] = Field(default_factory=list)
    team_lead_notes: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    markdown: str


class ProjectKickoffOutput(BaseModel):
    one_line_pitch: str
    mvp_scope: list[str] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)
    workstreams: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    open_questions: list[str] = Field(default_factory=list)
    role_discussion_questions: list[str] = Field(default_factory=list)
    issue_drafts: list[IssueDraft] = Field(default_factory=list)
    submission_checklist: list[str] = Field(default_factory=list)
    team_lead_notes: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    markdown: str


class HealthSignal(BaseModel):
    name: str
    detected: bool
    weight: int
    evidence: list[str] = Field(default_factory=list)
    missing_message: str = ""


class ProjectHealthOutput(BaseModel):
    mvp_completion_percent: int
    prototype_completion_percent: int
    stability_label: str
    stability_score: int
    ownership_status: str = "needs_confirmation"
    ownership_notes: list[str] = Field(default_factory=list)
    ownership_questions: list[str] = Field(default_factory=list)
    summary: str
    missing_meeting_items: list[str] = Field(default_factory=list)
    next_meeting_questions: list[str] = Field(default_factory=list)
    mvp_signals: list[HealthSignal] = Field(default_factory=list)
    prototype_signals: list[HealthSignal] = Field(default_factory=list)
    risk_notes: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    markdown: str


class BetaFeedback(BaseModel):
    version: str = "0.2.14"
    mode: str = "work"
    project_name: str = ""
    repo_path: str = ""
    repo_type: str = ""
    request_text: str = ""
    expected_files: list[str] = Field(default_factory=list)
    actual_top_files: list[str] = Field(default_factory=list)
    risk_result: str = ""
    token_evidence: str = ""
    result_order_feedback: str = ""
    workflow_trace_feedback: str = ""
    confusing_part: str = ""
    reuse_willingness: str = ""
    notes: str = ""
    screenshot_note: str = ""
    created_at: str = ""


class FeedbackSaveResult(BaseModel):
    output_dir: str
    markdown_path: str
    json_path: str
    redacted_secret_count: int = 0
    redacted_prompt_injection_count: int = 0


class FeedbackIssue(BaseModel):
    category: str
    summary: str
    count: int
    evidence: list[str] = Field(default_factory=list)


class FeedbackReviewOutput(BaseModel):
    feedback_count: int
    common_issues: list[FeedbackIssue] = Field(default_factory=list)
    missed_file_cases: list[str] = Field(default_factory=list)
    ui_confusion_points: list[str] = Field(default_factory=list)
    token_questions: list[str] = Field(default_factory=list)
    risk_questions: list[str] = Field(default_factory=list)
    workflow_trace_questions: list[str] = Field(default_factory=list)
    next_patch_priorities: list[str] = Field(default_factory=list)
    regression_test_candidates: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    markdown: str


class GraphStep(BaseModel):
    node_id: str
    label: str
    status: Literal["completed", "skipped", "blocked", "needs_input"]
    summary: str
    evidence: list[str] = Field(default_factory=list)
    next_action: str = ""


class GraphTrace(BaseModel):
    workflow: str = "work_handoff"
    final_status: Literal["completed", "blocked", "needs_input"] = "completed"
    current_node: str = ""
    steps: list[GraphStep] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)


class CapsuleInput(BaseModel):
    repo_path: Path
    task_request: str = Field(min_length=1)
    forbidden_rules: list[str] = Field(default_factory=list)
    top_k: int = 8
    handoff_target: HandoffTarget = HandoffTarget.AI_TOOL
    retriever_mode: RetrievalMode = RetrievalMode.KEYWORD
    my_scope: str = ""


class HandoffSections(BaseModel):
    overview: str
    future_me_letter: str
    teammate_brief: str
    junior_guide: str
    ai_handoff_prompt: str
    risk_checklist: str


class OwnershipCheck(BaseModel):
    status: str = "needs_confirmation"
    notes: list[str] = Field(default_factory=list)
    questions: list[str] = Field(default_factory=list)


class GuidedResult(BaseModel):
    first_action: str = ""
    primary_files: list[str] = Field(default_factory=list)
    supporting_files: list[str] = Field(default_factory=list)
    warning: str = ""
    reading_order: list[str] = Field(default_factory=list)
    detail_note: str = ""


class CapsuleOutput(BaseModel):
    handoff_target: HandoffTarget
    retriever_mode: RetrievalMode = RetrievalMode.KEYWORD
    retrieval_report: RetrievalReport = Field(default_factory=RetrievalReport)
    project_summary: str
    task_request: str
    request_understanding: RequestUnderstanding = Field(default_factory=RequestUnderstanding)
    relevant_chunks: list[RepoChunk]
    risk_findings: list[RiskFinding]
    approval_checklist: list[str]
    token_budget: TokenBudget
    ownership_check: OwnershipCheck = Field(default_factory=OwnershipCheck)
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
