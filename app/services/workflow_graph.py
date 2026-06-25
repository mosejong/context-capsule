from __future__ import annotations

from app.generators.output_writer import SavedOutputPacket
from app.schemas.capsule_schema import CapsuleInput, CapsuleOutput, ExecutionPacket, GraphStep, GraphTrace, RiskLevel


def build_work_handoff_trace(
    input_data: CapsuleInput,
    capsule: CapsuleOutput,
    execution_packet: ExecutionPacket,
    scanned_file_count: int,
    saved_packet: SavedOutputPacket | None = None,
) -> GraphTrace:
    steps = [
        build_scan_step(scanned_file_count),
        build_understanding_step(capsule),
        build_retrieval_step(capsule),
        build_risk_step(capsule, execution_packet),
        build_generation_step(input_data, capsule),
        build_review_gate_step(execution_packet, capsule.request_understanding.needs_clarification),
        build_save_step(saved_packet),
    ]
    final_status = infer_final_status(capsule, execution_packet)
    current_node = infer_current_node(final_status, steps)
    return GraphTrace(
        workflow="work_handoff",
        final_status=final_status,
        current_node=current_node,
        steps=steps,
        safety_notes=[
            "This graph is a deterministic workflow trace, not autonomous multi-agent execution.",
            "Nodes do not call external AI services.",
            "Blocked or unclear requests require human approval or clarification.",
        ],
    )


def build_scan_step(scanned_file_count: int) -> GraphStep:
    return GraphStep(
        node_id="scan_repository",
        label="레포 스캔",
        status="completed",
        summary=f"{scanned_file_count}개 파일을 스캔했습니다.",
        evidence=[f"scanned_file_count={scanned_file_count}"],
        next_action="요청 해석 단계로 이동",
    )


def build_understanding_step(capsule: CapsuleOutput) -> GraphStep:
    understanding = capsule.request_understanding
    status = "needs_input" if understanding.needs_clarification else "completed"
    evidence = [
        f"intent={understanding.intent}",
        f"confidence={understanding.confidence_label} ({understanding.confidence:.2f})",
    ]
    if understanding.target_hints:
        evidence.append(f"target_hints={', '.join(understanding.target_hints)}")
    if understanding.protected_hints:
        evidence.append(f"protected_hints={', '.join(understanding.protected_hints)}")
    if understanding.include_extensions:
        evidence.append(f"include_extensions={', '.join(understanding.include_extensions)}")
    if understanding.exclude_extensions:
        evidence.append(f"exclude_extensions={', '.join(understanding.exclude_extensions)}")
    if understanding.clarification_question:
        evidence.append(f"question={understanding.clarification_question}")
    return GraphStep(
        node_id="understand_request",
        label="요청 해석",
        status=status,
        summary=(
            "요청 대상이 모호해서 질문이 필요합니다."
            if understanding.needs_clarification
            else f"요청 의도를 {understanding.intent}로 해석했습니다."
        ),
        evidence=evidence,
        next_action=(
            "사용자에게 clarification question을 먼저 묻기"
            if understanding.needs_clarification
            else "관련 컨텍스트 검색 단계로 이동"
        ),
    )


def build_retrieval_step(capsule: CapsuleOutput) -> GraphStep:
    if capsule.request_understanding.needs_clarification:
        return GraphStep(
            node_id="retrieve_context",
            label="관련 컨텍스트 검색",
            status="skipped",
            summary="요청이 모호해서 레포 검색을 건너뛰었습니다.",
            evidence=[f"used_mode={capsule.retrieval_report.used_mode}"],
            next_action="질문 답변을 받은 뒤 검색 재시도",
        )
    paths = [chunk.path for chunk in capsule.relevant_chunks[:5]]
    return GraphStep(
        node_id="retrieve_context",
        label="관련 컨텍스트 검색",
        status="completed",
        summary=f"{len(capsule.relevant_chunks)}개 후보 chunk를 찾았습니다.",
        evidence=[
            f"requested_mode={capsule.retrieval_report.requested_mode}",
            f"used_mode={capsule.retrieval_report.used_mode}",
            *(f"path={path}" for path in paths),
        ],
        next_action="위험 분석 단계로 이동",
    )


def build_risk_step(capsule: CapsuleOutput, execution_packet: ExecutionPacket) -> GraphStep:
    if capsule.request_understanding.needs_clarification:
        return GraphStep(
            node_id="analyze_risk",
            label="위험 분석",
            status="skipped",
            summary="요청이 모호해서 위험 분석을 보류했습니다.",
            evidence=["reason=needs_clarification"],
            next_action="질문 답변을 받은 뒤 위험 분석 재시도",
        )
    max_risk = execution_packet.risk_level
    status = "blocked" if max_risk == RiskLevel.BLOCKED else "completed"
    evidence = [
        f"risk_level={max_risk.value}",
        f"findings={len(capsule.risk_findings)}",
    ]
    if execution_packet.block_reason:
        evidence.append(f"block_reason={execution_packet.block_reason}")
    for finding in capsule.risk_findings[:5]:
        evidence.append(f"{finding.kind.value}/{finding.level.value}: {finding.reason}")
    return GraphStep(
        node_id="analyze_risk",
        label="위험 분석",
        status=status,
        summary=(
            "BLOCKED 위험이 있어 자동 시작을 차단했습니다."
            if status == "blocked"
            else f"최대 위험도는 {max_risk.value}입니다."
        ),
        evidence=evidence,
        next_action="사람 승인 필요" if status == "blocked" else "작업 정리본 생성 단계로 이동",
    )


def build_generation_step(input_data: CapsuleInput, capsule: CapsuleOutput) -> GraphStep:
    return GraphStep(
        node_id="generate_packet",
        label="작업 정리본 생성",
        status="completed",
        summary=f"{input_data.handoff_target.value} 기준 작업 정리본을 생성했습니다.",
        evidence=[
            "sections=overview,future_me,teammate,junior,ai,risk",
            f"handoff_prompt_tokens={capsule.token_budget.handoff_prompt_tokens}",
            f"estimated_reduction={capsule.token_budget.estimated_reduction_percent:.1f}%",
        ],
        next_action="승인 게이트 확인",
    )


def build_review_gate_step(execution_packet: ExecutionPacket, needs_clarification: bool = False) -> GraphStep:
    if needs_clarification:
        return GraphStep(
            node_id="review_gate",
            label="사람 승인 게이트",
            status="needs_input",
            summary="작업을 시작하기 전에 사용자의 추가 설명이 필요합니다.",
            evidence=["auto_start_allowed=False", "reason=needs_clarification"],
            next_action="clarification question에 먼저 답하기",
        )
    status = "completed" if execution_packet.auto_start_allowed else "blocked"
    return GraphStep(
        node_id="review_gate",
        label="사람 승인 게이트",
        status=status,
        summary=(
            "자동 시작이 허용되는 낮은 위험 작업 정리본입니다."
            if execution_packet.auto_start_allowed
            else "자동 시작이 차단되었습니다. 사람이 먼저 확인해야 합니다."
        ),
        evidence=[
            f"auto_start_allowed={execution_packet.auto_start_allowed}",
            f"recommended_branch={execution_packet.recommended_branch}",
            f"labels={', '.join(execution_packet.labels) if execution_packet.labels else '(none)'}",
        ],
        next_action="저장 또는 GitHub Issue dry-run" if execution_packet.auto_start_allowed else "위험 근거 확인 후 범위 재조정",
    )


def build_save_step(saved_packet: SavedOutputPacket | None) -> GraphStep:
    if not saved_packet:
        return GraphStep(
            node_id="save_output",
            label="출력 저장",
            status="skipped",
            summary="저장 옵션이 꺼져 있어 파일을 쓰지 않았습니다.",
            evidence=["save=False"],
            next_action="필요하면 --save 또는 대시보드 저장 기능 사용",
        )
    return GraphStep(
        node_id="save_output",
        label="출력 저장",
        status="completed",
        summary="작업 정리본을 outputs 폴더에 저장했습니다.",
        evidence=[f"output_dir={saved_packet.output_dir}"],
        next_action="GitHub Issue dry-run 또는 피드백 저장",
    )


def infer_final_status(capsule: CapsuleOutput, execution_packet: ExecutionPacket):
    if capsule.request_understanding.needs_clarification:
        return "needs_input"
    if not execution_packet.auto_start_allowed:
        return "blocked"
    return "completed"


def infer_current_node(final_status: str, steps: list[GraphStep]) -> str:
    if final_status == "needs_input":
        return "understand_request"
    if final_status == "blocked":
        for step in steps:
            if step.status == "blocked":
                return step.node_id
    return steps[-1].node_id if steps else ""
