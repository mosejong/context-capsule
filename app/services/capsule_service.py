from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.generators.capsule_generator import generate_capsule
from app.generators.execution_packet_generator import build_execution_packet
from app.generators.output_writer import SavedOutputPacket, save_output_packet
from app.scanners.repo_scanner import scan_repo
from app.schemas.capsule_schema import CapsuleInput, CapsuleOutput, ExecutionPacket, GraphTrace, HandoffTarget, RetrievalMode
from app.services.workflow_graph import build_work_handoff_trace


@dataclass(frozen=True)
class CapsuleGenerationResult:
    capsule: CapsuleOutput
    execution_packet: ExecutionPacket
    scanned_file_count: int
    saved_packet: SavedOutputPacket | None = None
    graph_trace: GraphTrace | None = None


def generate_capsule_result(
    repo_path: Path | str,
    task_request: str,
    forbidden_rules: list[str] | None = None,
    top_k: int = 8,
    handoff_target: HandoffTarget = HandoffTarget.AI_TOOL,
    retriever_mode: RetrievalMode = RetrievalMode.KEYWORD,
    my_scope: str = "",
    save: bool = False,
    output_root: Path | str = "outputs",
) -> CapsuleGenerationResult:
    input_data = CapsuleInput(
        repo_path=Path(repo_path),
        task_request=task_request,
        forbidden_rules=forbidden_rules or [],
        top_k=top_k,
        handoff_target=handoff_target,
        retriever_mode=retriever_mode,
        my_scope=my_scope,
    )
    files = scan_repo(input_data.repo_path)
    capsule = generate_capsule(input_data, files)
    execution_packet = build_execution_packet(capsule)
    saved_packet = save_output_packet(capsule, execution_packet, output_root=output_root) if save else None
    graph_trace = build_work_handoff_trace(input_data, capsule, execution_packet, len(files), saved_packet)
    return CapsuleGenerationResult(
        capsule=capsule,
        execution_packet=execution_packet,
        scanned_file_count=len(files),
        saved_packet=saved_packet,
        graph_trace=graph_trace,
    )


def summarize_generation_result(result: CapsuleGenerationResult) -> dict:
    packet = result.execution_packet
    capsule = result.capsule
    return {
        "task_request": capsule.task_request,
        "request_understanding": capsule.request_understanding.model_dump(mode="json"),
        "handoff_target": capsule.handoff_target.value,
        "retriever_mode": capsule.retriever_mode.value,
        "retrieval_report": capsule.retrieval_report.model_dump(mode="json"),
        "scanned_file_count": result.scanned_file_count,
        "saved_output_dir": str(result.saved_packet.output_dir) if result.saved_packet else None,
        "github_issue": {
            "title": packet.title,
            "recommended_branch": packet.recommended_branch,
            "labels": packet.labels,
            "risk_level": packet.risk_level.value,
            "auto_start_allowed": packet.auto_start_allowed,
            "block_reason": packet.block_reason,
            "acceptance_criteria": packet.acceptance_criteria,
        },
        "token_budget": capsule.token_budget.model_dump(mode="json"),
        "ownership_check": capsule.ownership_check.model_dump(mode="json"),
        "relevant_paths": [chunk.path for chunk in capsule.relevant_chunks],
        "risk_findings": [finding.model_dump(mode="json") for finding in capsule.risk_findings],
        "graph_trace": result.graph_trace.model_dump(mode="json") if result.graph_trace else None,
    }
