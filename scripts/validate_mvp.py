from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.analyzers.chat_analyzer import extract_task_request
from app.adapters.github_issue_adapter import create_issue_from_packet
from app.generators.capsule_generator import generate_capsule
from app.generators.execution_packet_generator import build_execution_packet
from app.generators.output_writer import save_output_packet
from app.schemas.capsule_schema import CapsuleInput, FileKind, HandoffTarget, RepoFile


@dataclass(frozen=True)
class Scenario:
    name: str
    task_request: str
    handoff_target: HandoffTarget = HandoffTarget.AI_TOOL
    chat_log: str | None = None
    expect_auto_start: bool | None = None
    expected_prompt_terms: tuple[str, ...] = ()
    expected_paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class ScenarioResult:
    name: str
    auto_start_allowed: bool
    raw_context_tokens: int
    retrieved_context_tokens: int
    handoff_prompt_tokens: int
    reduction_percent: float
    retrieved_chunk_count: int
    risk_count: int

    def summary(self) -> str:
        return (
            f"{self.name}: ok | auto_start={self.auto_start_allowed} | "
            f"reduction={self.reduction_percent:.1f}% | "
            f"chunks={self.retrieved_chunk_count}"
        )


def sample_files() -> list[RepoFile]:
    return [
        RepoFile(
            path="README.md",
            kind=FileKind.DOC,
            content=(
                "# Demo\n"
                "A small project used for Context Capsule validation.\n"
                "This README intentionally repeats project background so token reduction can be measured.\n"
                * 120
            ),
            size=15_000,
        ),
        RepoFile(
            path="app/analyzers/risk_analyzer.py",
            kind=FileKind.CODE,
            content="def analyze_risk():\n    return ['risk finding']\n",
            size=48,
        ),
        RepoFile(
            path="tests/test_risk_analyzer.py",
            kind=FileKind.TEST,
            content="def test_risk_analyzer():\n    assert True\n",
            size=42,
        ),
        RepoFile(
            path="app/auth.py",
            kind=FileKind.CODE,
            content="jwt login password token permission",
            size=35,
        ),
        RepoFile(
            path="app/generators/capsule_generator.py",
            kind=FileKind.CODE,
            content="def generate_capsule():\n    return markdown token budget\n",
            size=58,
        ),
    ]


def scenarios() -> list[Scenario]:
    chat_log = """
    나: 어떤 에러났는데 뭐야?
    Traceback: ValueError in app/analyzers/risk_analyzer.py
    tests/test_risk_analyzer.py failed
    """

    return [
        Scenario(
            name="direct_readme_brief",
            task_request="README 문서를 포트폴리오용으로 정리하는 작업 브리프를 만들어줘",
            expect_auto_start=True,
            expected_paths=("README.md",),
        ),
        Scenario(
            name="chat_error_to_capsule",
            task_request="",
            chat_log=chat_log,
            expect_auto_start=True,
            expected_paths=("app/analyzers/risk_analyzer.py", "tests/test_risk_analyzer.py"),
        ),
        Scenario(
            name="high_risk_auth_blocks_auto_start",
            task_request="로그인 jwt token permission 로직을 수정하는 작업 브리프를 만들어줘",
            expect_auto_start=False,
            expected_paths=("app/auth.py",),
        ),
        Scenario(
            name="teammate_brief",
            task_request="팀원이 capsule generator 작업에서 막히지 않게 오늘 할 일로 쪼개줘",
            handoff_target=HandoffTarget.TEAMMATE,
            expect_auto_start=True,
            expected_prompt_terms=("오늘 할 일", "질문해야 할 것"),
            expected_paths=("app/generators/capsule_generator.py",),
        ),
        Scenario(
            name="future_me_handoff",
            task_request="내일 이어서 볼 수 있게 현재 작업 상태를 정리해줘",
            handoff_target=HandoffTarget.FUTURE_ME,
            expect_auto_start=True,
            expected_prompt_terms=("내일 이어서 작업", "다음 작업"),
        ),
    ]


def evaluate_scenario(scenario: Scenario) -> ScenarioResult:
    task_request = scenario.task_request
    if scenario.chat_log:
        extraction = extract_task_request(scenario.chat_log)
        task_request = extraction.task_request
        for expected_path in scenario.expected_paths:
            assert expected_path in extraction.detected_paths, (
                f"{scenario.name}: expected extracted path {expected_path}, got {extraction.detected_paths}"
            )

    capsule = generate_capsule(
        CapsuleInput(
            repo_path=Path("."),
            task_request=task_request,
            handoff_target=scenario.handoff_target,
        ),
        sample_files(),
    )
    packet = build_execution_packet(capsule)

    assert capsule.token_budget.raw_context_tokens > 0, f"{scenario.name}: missing raw token count"
    assert capsule.token_budget.handoff_prompt_tokens > 0, f"{scenario.name}: missing prompt token count"
    assert capsule.token_budget.estimated_reduction_percent >= 0, f"{scenario.name}: invalid reduction"
    assert "RiskLevel." not in capsule.markdown, f"{scenario.name}: leaked enum repr in capsule"
    assert "RiskLevel." not in packet.issue_body, f"{scenario.name}: leaked enum repr in issue body"
    assert "Auto Start Gate" in packet.issue_body, f"{scenario.name}: missing auto-start gate"
    assert packet.recommended_branch.startswith("task/"), f"{scenario.name}: invalid branch name"
    assert packet.labels, f"{scenario.name}: missing issue labels"
    assert packet.acceptance_criteria, f"{scenario.name}: missing acceptance criteria"

    with TemporaryDirectory() as tmp_dir:
        saved = save_output_packet(capsule, packet, output_root=Path(tmp_dir))
        assert (saved.output_dir / "GITHUB_ISSUE.md").exists(), f"{scenario.name}: missing saved issue file"
        assert (saved.output_dir / "metadata.json").exists(), f"{scenario.name}: missing saved metadata"
        issue_result = create_issue_from_packet(saved.output_dir, repository="mosejong/context-capsule", apply=False)
        assert issue_result.mode == "dry-run", f"{scenario.name}: issue adapter should default to dry-run"
        assert issue_result.payload["title"], f"{scenario.name}: missing GitHub issue title"

    if scenario.expect_auto_start is not None:
        assert packet.auto_start_allowed is scenario.expect_auto_start, (
            f"{scenario.name}: expected auto_start={scenario.expect_auto_start}, got {packet.auto_start_allowed}"
        )

    retrieved_paths = {chunk.path for chunk in capsule.relevant_chunks}
    for expected_path in scenario.expected_paths:
        assert expected_path in retrieved_paths, (
            f"{scenario.name}: expected retrieved path {expected_path}, got {sorted(retrieved_paths)}"
        )

    for term in scenario.expected_prompt_terms:
        assert term in capsule.handoff_prompt, f"{scenario.name}: missing prompt term {term!r}"

    return ScenarioResult(
        name=scenario.name,
        auto_start_allowed=packet.auto_start_allowed,
        raw_context_tokens=capsule.token_budget.raw_context_tokens,
        retrieved_context_tokens=capsule.token_budget.retrieved_context_tokens,
        handoff_prompt_tokens=capsule.token_budget.handoff_prompt_tokens,
        reduction_percent=capsule.token_budget.estimated_reduction_percent,
        retrieved_chunk_count=len(capsule.relevant_chunks),
        risk_count=len(capsule.risk_findings),
    )


def run_scenario(scenario: Scenario) -> str:
    return evaluate_scenario(scenario).summary()


def run_validation(repeat: int) -> list[str]:
    results: list[str] = []
    for index in range(1, repeat + 1):
        for scenario in scenarios():
            results.append(f"run {index}/{repeat} | {run_scenario(scenario)}")
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Context Capsule MVP scenario validation.")
    parser.add_argument("--repeat", type=int, default=1, help="Number of validation loops to run.")
    args = parser.parse_args()

    if args.repeat < 1:
        raise SystemExit("--repeat must be 1 or greater")

    for line in run_validation(args.repeat):
        print(line)
    print(f"validated {len(scenarios())} scenarios x {args.repeat} run(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
