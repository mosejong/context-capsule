from __future__ import annotations

import fnmatch
import json
import re
from pathlib import Path, PurePosixPath

from app.schemas.capsule_schema import CapsuleOutput, ExecutionPacket, RiskLevel
from app.schemas.harness_schema import (
    CheckResult,
    ContractViolation,
    TaskContract,
    VerificationResult,
)


PROTECTED_PATH_PATTERNS = {
    "auth": ["**/auth/**", "**/auth.*", "**/*auth*.*", "**/jwt/**", "**/*jwt*.*"],
    "db": ["**/db/**", "**/database/**", "**/migrations/**", "**/*migration*.*"],
    "deploy": ["**/deploy/**", "**/docker-compose*.yml", "**/nginx/**", "**/.github/workflows/**"],
    "secret": [".env", ".env.*", "**/.env", "**/.env.*", "**/*secret*", "**/*credential*"],
}

PROTECTED_ALIASES = {
    "auth": ("auth", "authentication", "login", "jwt", "인증", "로그인"),
    "db": ("db", "database", "schema", "migration", "데이터베이스", "스키마", "마이그레이션"),
    "deploy": ("deploy", "deployment", "docker", "nginx", "배포"),
    "secret": (".env", "secret", "credential", "api key", "token", "시크릿", "자격증명"),
}

NEGATIVE_BOUNDARY_PATTERN = re.compile(
    r"건드리지|수정하지|변경하지|보지\s*마|제외|금지|do\s+not|don't|avoid|exclude",
    re.IGNORECASE,
)


def build_task_contract(
    capsule: CapsuleOutput,
    execution_packet: ExecutionPacket,
    forbidden_rules: list[str] | None = None,
) -> TaskContract:
    allowed_paths = unique(chunk.path for chunk in capsule.relevant_chunks)
    protected = infer_protected_keys(
        capsule.task_request,
        capsule.request_understanding.protected_hints,
        forbidden_rules or [],
    )
    forbidden_paths = unique(
        pattern
        for key in protected
        for pattern in PROTECTED_PATH_PATTERNS.get(key, [])
    )
    approval_required = (
        not execution_packet.auto_start_allowed
        or execution_packet.risk_level in {RiskLevel.HIGH, RiskLevel.BLOCKED}
    )
    return TaskContract(
        task=capsule.task_request,
        allowed_paths=allowed_paths,
        forbidden_paths=forbidden_paths,
        forbidden_rules=forbidden_rules or [],
        acceptance_criteria=execution_packet.acceptance_criteria,
        approval_required=approval_required,
        strict_scope=bool(allowed_paths),
    )


def verify_task_contract(
    contract: TaskContract,
    changed_paths: list[str],
    check_results: list[CheckResult] | None = None,
    approval_granted: bool = False,
) -> VerificationResult:
    normalized_paths = unique(normalize_path(path) for path in changed_paths if path.strip())
    results_by_name = {result.name: result for result in (check_results or [])}
    violations: list[ContractViolation] = []

    for path in normalized_paths:
        if matches_any(path, contract.forbidden_paths):
            violations.append(
                ContractViolation(
                    kind="forbidden_path",
                    path=path,
                    message=f"금지 경로가 변경 목록에 포함됐습니다: {path}",
                )
            )
            continue
        if contract.strict_scope and contract.allowed_paths and not matches_any(path, contract.allowed_paths):
            violations.append(
                ContractViolation(
                    kind="outside_scope",
                    path=path,
                    message=f"허용 범위 밖의 파일이 변경됐습니다: {path}",
                )
            )

    if contract.approval_required and not approval_granted:
        violations.append(
            ContractViolation(
                kind="approval_missing",
                message="HIGH/BLOCKED 작업에 필요한 사람 승인이 확인되지 않았습니다.",
            )
        )

    for result in results_by_name.values():
        if result.status == "failed":
            violations.append(
                ContractViolation(
                    kind="check_failed",
                    message=f"검증 항목이 실패했습니다: {result.name}",
                )
            )

    missing_checks = [
        name
        for name in contract.required_checks
        if name not in results_by_name or results_by_name[name].status == "not_run"
    ]
    if not normalized_paths:
        missing_checks.insert(0, "changed_paths")
    blocked = any(
        violation.kind in {"forbidden_path", "outside_scope", "approval_missing", "check_failed"}
        for violation in violations
    )
    if blocked:
        verdict = "BLOCKED"
        next_action = "위반 파일을 되돌리거나 사람 승인을 받고, 실패한 검증을 다시 실행하세요."
    elif missing_checks:
        verdict = "WARN"
        next_action = f"아직 실행하지 않은 검증을 완료하세요: {', '.join(missing_checks)}"
    else:
        verdict = "PASS"
        next_action = "계약 범위와 필수 검증을 통과했습니다. 변경 내용을 사람이 최종 검토하세요."

    return VerificationResult(
        verdict=verdict,
        changed_paths=normalized_paths,
        violations=violations,
        check_results=list(results_by_name.values()),
        missing_checks=missing_checks,
        next_action=next_action,
        summary=(
            f"변경 파일 {len(normalized_paths)}개, 위반 {len(violations)}개, "
            f"미실행 검증 {len(missing_checks)}개"
        ),
    )


def load_task_contract(path: Path | str) -> TaskContract:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return TaskContract.model_validate(payload)


def infer_protected_keys(task: str, protected_hints: list[str], forbidden_rules: list[str]) -> list[str]:
    keys: list[str] = []
    for hint in protected_hints:
        hint_lower = hint.lower()
        for key, aliases in PROTECTED_ALIASES.items():
            if key in hint_lower or any(alias in hint_lower for alias in aliases):
                keys.append(key)

    for text in [task, *forbidden_rules]:
        lowered = text.lower()
        clauses = re.split(r"[\n,;]|(?:그리고|하지만|대신)", lowered)
        for clause in clauses:
            if not NEGATIVE_BOUNDARY_PATTERN.search(clause) and text == task:
                continue
            for key, aliases in PROTECTED_ALIASES.items():
                if any(alias in clause for alias in aliases):
                    keys.append(key)
    return unique(keys)


def save_task_contract(contract: TaskContract, path: Path | str) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(contract.model_dump_json(indent=2), encoding="utf-8")
    return output


def matches_any(path: str, patterns: list[str]) -> bool:
    normalized = normalize_path(path)
    for pattern in patterns:
        normalized_pattern = normalize_path(pattern)
        if normalized == normalized_pattern:
            return True
        if fnmatch.fnmatchcase(normalized, normalized_pattern):
            return True
        if PurePosixPath(normalized).match(normalized_pattern):
            return True
    return False


def normalize_path(path: str) -> str:
    normalized = path.strip().replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.lstrip("/")


def unique(values) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))
