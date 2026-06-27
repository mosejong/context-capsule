from __future__ import annotations

from app.schemas.capsule_schema import CapsuleOutput, ExecutionPacket, GuidedResult


DEFAULT_READING_ORDER = [
    "추천 첫 행동",
    "먼저 볼 파일",
    "위험/승인",
    "AI 지시문",
    "작업 흐름",
]


def build_guided_result(capsule: CapsuleOutput, packet: ExecutionPacket) -> GuidedResult:
    files = unique_paths([chunk.path for chunk in capsule.relevant_chunks])
    primary_files = select_primary_files(capsule, files)
    supporting_files = [path for path in files if path not in primary_files][:6]
    return GuidedResult(
        first_action=build_first_action(capsule, packet, primary_files),
        primary_files=primary_files,
        supporting_files=supporting_files,
        warning=build_warning(capsule, packet),
        reading_order=DEFAULT_READING_ORDER,
        detail_note=(
            "처음에는 추천 첫 행동, 먼저 볼 파일, 위험/승인만 확인하세요. "
            "AI 지시문과 작업 흐름은 복붙하거나 판단 근거가 필요할 때 보면 됩니다."
        ),
    )


def select_primary_files(capsule: CapsuleOutput, files: list[str]) -> list[str]:
    if is_readme_portfolio_request(capsule):
        if "README.md" in files:
            return ["README.md"]
        root_like = [path for path in files if path.lower() == "readme.md"]
        if root_like:
            return root_like[:1]
    return files[:3]


def build_first_action(capsule: CapsuleOutput, packet: ExecutionPacket, primary_files: list[str]) -> str:
    understanding = capsule.request_understanding
    if understanding.needs_clarification:
        question = understanding.clarification_question or "대상 파일, 기능, 오류 로그 중 하나를 더 구체적으로 알려주세요."
        return f"요청이 아직 모호합니다. 파일을 찾기 전에 먼저 확인하세요: {question}"

    if not packet.auto_start_allowed:
        return "위험/승인 탭에서 차단 사유를 먼저 확인하고, 수정 범위를 사람에게 승인받으세요."

    if is_readme_portfolio_request(capsule):
        if primary_files:
            return (
                "이 요청은 포트폴리오용 README 정리로 보입니다. "
                "root README.md를 기준으로 수정 범위를 잡고, 하위 README는 참고 문서로만 확인하세요."
            )
        return (
            "이 요청은 포트폴리오용 README 정리로 보이지만 root README.md를 찾지 못했습니다. "
            "대표 README가 어디인지 먼저 확인하세요."
        )

    if capsule.ownership_check.status == "possibly_other_part":
        return "내 담당 영역과 직접 겹치지 않을 수 있습니다. 작업 시작 전에 담당 범위를 먼저 확인하세요."

    if primary_files:
        return f"`{primary_files[0]}`부터 확인하고, 수정 전 계획을 먼저 제안하세요."
    return "관련 파일을 확정하기 어렵습니다. 작업 대상 파일이나 오류 로그를 먼저 보강하세요."


def build_warning(capsule: CapsuleOutput, packet: ExecutionPacket) -> str:
    if not packet.auto_start_allowed:
        return packet.block_reason or "위험도가 높아 자동 시작을 차단했습니다."
    if capsule.ownership_check.status == "possibly_other_part":
        return "다른 사람 담당 영역일 수 있습니다. PR/회의에서 범위를 확인하세요."
    if is_readme_portfolio_request(capsule):
        return "포트폴리오 README는 실제 구현/검증 수치를 과장하지 않는 것이 중요합니다."
    return "자동 수정 전에 변경 파일과 예상 영향도를 먼저 확인하세요."


def is_readme_portfolio_request(capsule: CapsuleOutput) -> bool:
    understanding = capsule.request_understanding
    text = " ".join(
        [
            capsule.task_request,
            understanding.normalized_request,
            understanding.search_query,
            " ".join(understanding.file_hints),
            " ".join(understanding.target_hints),
        ]
    ).lower()
    return understanding.intent == "documentation_edit" and "readme" in text and any(
        term in text for term in ["portfolio", "포트폴리오", "포폴", "readme.md"]
    )


def unique_paths(paths: list[str]) -> list[str]:
    return list(dict.fromkeys(paths))
