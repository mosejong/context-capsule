from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.analyzers.chat_analyzer import extract_task_request
from app.analyzers.meeting_analyzer import analyze_project_health, analyze_project_kickoff, analyze_scrum_notes
from app.schemas.capsule_schema import BetaFeedback, HandoffTarget, RetrievalMode
from app.services.capsule_service import generate_capsule_result, summarize_generation_result
from app.services.feedback_service import review_feedback, save_beta_feedback


STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(
    title="Context Capsule Local UI",
    description="Korean-first local web UI for Context Capsule v0.2.",
    version="0.2.13",
)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


class WorkHandoffRequest(BaseModel):
    repo_path: str = "."
    task_request: str = Field(min_length=1)
    forbidden_rules: str = ""
    top_k: int = 8
    retriever_mode: RetrievalMode = RetrievalMode.KEYWORD
    handoff_target: HandoffTarget = HandoffTarget.AI_TOOL
    input_mode: str = "direct"
    my_scope: str = ""


class ScrumNotesRequest(BaseModel):
    meeting_text: str = Field(min_length=1)
    project_context: str = ""
    instructor_feedback: str = ""


class KickoffRequest(BaseModel):
    topic: str = Field(min_length=1)
    idea_notes: str = Field(min_length=1)
    deadline: str = ""
    constraints: str = ""
    team_context: str = ""


class HealthCheckRequest(BaseModel):
    status_text: str = Field(min_length=1)
    project_context: str = ""
    deadline: str = ""
    my_scope: str = ""


class FeedbackSaveRequest(BaseModel):
    version: str = "0.2.13"
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


class FeedbackReviewRequest(BaseModel):
    feedback_root: str = "outputs/feedback"


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "ui": "fastapi",
        "version": "0.2.13",
        "note": "No external AI is required.",
    }


@app.post("/api/work-handoff")
def work_handoff(request: WorkHandoffRequest) -> dict:
    try:
        task_request = request.task_request
        extraction = None
        if request.input_mode == "chat":
            extraction = extract_task_request(task_request)
            task_request = extraction.task_request

        rules = [line.strip() for line in request.forbidden_rules.splitlines() if line.strip()]
        result = generate_capsule_result(
            repo_path=Path(request.repo_path),
            task_request=task_request,
            forbidden_rules=rules,
            top_k=request.top_k,
            handoff_target=request.handoff_target,
            retriever_mode=request.retriever_mode,
            my_scope=request.my_scope,
        )
        summary = summarize_generation_result(result)
        capsule = result.capsule
        packet = result.execution_packet
        return {
            "summary": summary,
            "extraction": extraction.model_dump(mode="json") if extraction else None,
            "request_understanding": capsule.request_understanding.model_dump(mode="json"),
            "sections": capsule.sections.model_dump(mode="json"),
            "risk_findings": [finding.model_dump(mode="json") for finding in capsule.risk_findings],
            "approval_checklist": capsule.approval_checklist,
            "token_budget": capsule.token_budget.model_dump(mode="json"),
            "ownership_check": capsule.ownership_check.model_dump(mode="json"),
            "guided_result": result.guided_result.model_dump(mode="json") if result.guided_result else None,
            "relevant_files": [
                {
                    "path": chunk.path,
                    "kind": chunk.kind.value,
                    "score": chunk.score,
                    "lines": f"{chunk.start_line or '?'}-{chunk.end_line or '?'}",
                    "preview": chunk.text[:350],
                }
                for chunk in capsule.relevant_chunks[:12]
            ],
            "github_issue": {
                "title": packet.title,
                "recommended_branch": packet.recommended_branch,
                "risk_level": packet.risk_level.value,
                "auto_start_allowed": packet.auto_start_allowed,
                "block_reason": packet.block_reason,
                "labels": packet.labels,
                "body": packet.issue_body,
            },
            "graph_trace": result.graph_trace.model_dump(mode="json") if result.graph_trace else None,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/scrum-notes")
def scrum_notes(request: ScrumNotesRequest) -> dict:
    output = analyze_scrum_notes(
        request.meeting_text,
        project_context=request.project_context,
        instructor_feedback=request.instructor_feedback,
    )
    return output.model_dump(mode="json")


@app.post("/api/kickoff")
def kickoff(request: KickoffRequest) -> dict:
    output = analyze_project_kickoff(
        topic=request.topic,
        idea_notes=request.idea_notes,
        deadline=request.deadline,
        constraints=request.constraints,
        team_context=request.team_context,
    )
    return output.model_dump(mode="json")


@app.post("/api/health-check")
def health_check(request: HealthCheckRequest) -> dict:
    output = analyze_project_health(
        status_text=request.status_text,
        project_context=request.project_context,
        deadline=request.deadline,
        my_scope=request.my_scope,
    )
    return output.model_dump(mode="json")


@app.post("/api/feedback")
def feedback(request: FeedbackSaveRequest) -> dict:
    try:
        result = save_beta_feedback(BetaFeedback(**request.model_dump(mode="json")))
        return result.model_dump(mode="json")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/feedback-review")
def feedback_review(request: FeedbackReviewRequest) -> dict:
    try:
        output = review_feedback(Path(request.feedback_root))
        return output.model_dump(mode="json")
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
