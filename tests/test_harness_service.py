import json

from app.schemas.harness_schema import CheckResult, TaskContract
from app.services.harness_service import infer_protected_keys, verify_task_contract


def passing_checks():
    return [
        CheckResult(name="scope_review", status="passed"),
        CheckResult(name="test_or_run_result", status="passed"),
        CheckResult(name="acceptance_criteria_review", status="passed"),
    ]


def test_verifier_passes_allowed_change_with_all_checks():
    contract = TaskContract(task="Fix login", allowed_paths=["app/auth.py"])

    result = verify_task_contract(contract, ["app/auth.py"], passing_checks())

    assert result.verdict == "PASS"
    assert not result.violations
    assert not result.missing_checks


def test_verifier_blocks_outside_scope_and_forbidden_path():
    contract = TaskContract(
        task="Fix login",
        allowed_paths=["app/auth.py"],
        forbidden_paths=[".env", "**/db/**"],
    )

    result = verify_task_contract(contract, ["app/auth.py", "app/db/models.py", ".env"], passing_checks())

    assert result.verdict == "BLOCKED"
    assert {item.kind for item in result.violations} == {"forbidden_path"}
    assert {item.path for item in result.violations} == {"app/db/models.py", ".env"}


def test_verifier_warns_when_evidence_is_missing():
    contract = TaskContract(task="Docs", allowed_paths=["README.md"])

    result = verify_task_contract(contract, ["README.md"], [CheckResult(name="scope_review", status="passed")])

    assert result.verdict == "WARN"
    assert result.missing_checks == ["test_or_run_result", "acceptance_criteria_review"]

    no_changes = verify_task_contract(contract, [], passing_checks())
    assert no_changes.verdict == "WARN"
    assert no_changes.missing_checks == ["changed_paths"]


def test_verifier_requires_human_approval_for_guarded_contract():
    contract = TaskContract(task="JWT change", allowed_paths=["app/auth.py"], approval_required=True)

    blocked = verify_task_contract(contract, ["app/auth.py"], passing_checks())
    passed = verify_task_contract(contract, ["app/auth.py"], passing_checks(), approval_granted=True)

    assert blocked.verdict == "BLOCKED"
    assert any(item.kind == "approval_missing" for item in blocked.violations)
    assert passed.verdict == "PASS"


def test_task_contract_json_round_trip():
    contract = TaskContract(task="Docs", allowed_paths=["README.md"])

    loaded = TaskContract.model_validate(json.loads(contract.model_dump_json()))

    assert loaded == contract


def test_contract_safety_infers_auth_and_env_from_negative_korean_context():
    keys = infer_protected_keys("README만 수정하고 auth와 .env는 건드리지 마", [], [])

    assert keys == ["auth", "secret"]
