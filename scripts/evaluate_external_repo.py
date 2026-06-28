from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.schemas.capsule_schema import RetrievalMode, RiskLevel
from app.services.capsule_service import generate_capsule_result

DEFAULT_REPO_PATH = Path("tests/fixtures/external_repos/ecommerce")
DEFAULT_CASES_PATH = Path("tests/fixtures/external_repo_eval_cases.json")
DEFAULT_REPORT_PATH = Path("docs/reports/external_repo_eval.md")

RISK_PRIORITY = {
    RiskLevel.LOW.value: 0,
    RiskLevel.MEDIUM.value: 1,
    RiskLevel.HIGH.value: 2,
    RiskLevel.BLOCKED.value: 3,
}


@dataclass(frozen=True)
class ExternalRepoCase:
    name: str
    task: str
    expected_paths: list[str]
    expected_risk: str = RiskLevel.MEDIUM.value
    max_rank_for_pass: int = 3


@dataclass(frozen=True)
class ExternalRepoResult:
    name: str
    task: str
    verdict: str
    expected_paths: list[str]
    top_paths: list[str]
    best_rank: int | None
    hit_at_1: bool
    hit_at_3: bool
    target_included: bool
    expected_risk: str
    actual_risk: str
    risk_floor_ok: bool
    estimated_reduction_percent: float
    token_baseline_scope: str
    notes: list[str]


def load_cases(path: Path) -> list[ExternalRepoCase]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [ExternalRepoCase(**item) for item in data]


def evaluate_case(repo_path: Path, case: ExternalRepoCase, retriever_mode: RetrievalMode, top_k: int) -> ExternalRepoResult:
    result = generate_capsule_result(
        repo_path=repo_path,
        task_request=case.task,
        retriever_mode=retriever_mode,
        top_k=top_k,
    )
    top_paths = [chunk.path for chunk in result.capsule.relevant_chunks]
    best_rank = first_rank(top_paths, case.expected_paths)
    target_included = best_rank is not None
    hit_at_1 = best_rank == 1
    hit_at_3 = bool(best_rank and best_rank <= 3)
    actual_risk = result.execution_packet.risk_level.value
    risk_floor_ok = RISK_PRIORITY[actual_risk] >= RISK_PRIORITY[case.expected_risk]
    notes: list[str] = []

    if not target_included:
        notes.append("expected target file was not retrieved")
    elif best_rank and best_rank > case.max_rank_for_pass:
        notes.append(f"target file ranked {best_rank}, expected <= {case.max_rank_for_pass}")

    if not risk_floor_ok:
        notes.append(f"risk below expectation: expected at least {case.expected_risk}, got {actual_risk}")
    elif RISK_PRIORITY[actual_risk] > RISK_PRIORITY[case.expected_risk]:
        notes.append(f"risk is stricter than expected: expected {case.expected_risk}, got {actual_risk}")

    if result.capsule.token_budget.baseline_context_scope != "retrieved_file_contents":
        notes.append(f"unexpected token baseline scope: {result.capsule.token_budget.baseline_context_scope}")

    verdict = classify_verdict(target_included, best_rank, case.max_rank_for_pass, risk_floor_ok)
    return ExternalRepoResult(
        name=case.name,
        task=case.task,
        verdict=verdict,
        expected_paths=case.expected_paths,
        top_paths=top_paths[:top_k],
        best_rank=best_rank,
        hit_at_1=hit_at_1,
        hit_at_3=hit_at_3,
        target_included=target_included,
        expected_risk=case.expected_risk,
        actual_risk=actual_risk,
        risk_floor_ok=risk_floor_ok,
        estimated_reduction_percent=result.capsule.token_budget.estimated_reduction_percent,
        token_baseline_scope=result.capsule.token_budget.baseline_context_scope,
        notes=notes,
    )


def first_rank(top_paths: list[str], expected_paths: list[str]) -> int | None:
    expected = set(expected_paths)
    for index, path in enumerate(top_paths, start=1):
        if path in expected:
            return index
    return None


def classify_verdict(target_included: bool, best_rank: int | None, max_rank_for_pass: int, risk_floor_ok: bool) -> str:
    if not target_included or not risk_floor_ok:
        return "FAIL"
    if best_rank and best_rank <= max_rank_for_pass:
        return "PASS"
    return "WARN"


def evaluate_cases(
    repo_path: Path,
    cases: list[ExternalRepoCase],
    retriever_mode: RetrievalMode = RetrievalMode.KEYWORD,
    top_k: int = 8,
) -> list[ExternalRepoResult]:
    return [evaluate_case(repo_path, case, retriever_mode, top_k) for case in cases]


def summarize(results: list[ExternalRepoResult]) -> dict:
    target_count = len(results)
    pass_count = sum(1 for result in results if result.verdict == "PASS")
    warn_count = sum(1 for result in results if result.verdict == "WARN")
    fail_count = sum(1 for result in results if result.verdict == "FAIL")
    hit_at_1 = sum(1 for result in results if result.hit_at_1)
    hit_at_3 = sum(1 for result in results if result.hit_at_3)
    included = sum(1 for result in results if result.target_included)
    risk_floor_ok = sum(1 for result in results if result.risk_floor_ok)
    avg_reduction = (
        sum(result.estimated_reduction_percent for result in results) / len(results)
        if results
        else 0.0
    )
    return {
        "cases": target_count,
        "pass": pass_count,
        "warn": warn_count,
        "fail": fail_count,
        "hit_at_1": hit_at_1,
        "hit_at_3": hit_at_3,
        "target_included": included,
        "risk_floor_ok": risk_floor_ok,
        "average_estimated_reduction_percent": round(avg_reduction, 1),
    }


def build_markdown(results: list[ExternalRepoResult], repo_path: Path, cases_path: Path, retriever_mode: RetrievalMode) -> str:
    summary = summarize(results)
    rows = [
        "| Case | Verdict | Best Rank | Expected Target | Actual Top Paths | Risk | Token Reduction | Notes |",
        "| --- | --- | ---: | --- | --- | --- | ---: | --- |",
    ]
    for result in results:
        rows.append(
            "| "
            f"{escape(result.name)} | "
            f"{result.verdict} | "
            f"{result.best_rank or '-'} | "
            f"{escape(', '.join(result.expected_paths))} | "
            f"{escape(', '.join(result.top_paths[:5]))} | "
            f"{result.actual_risk} (expected >= {result.expected_risk}) | "
            f"{result.estimated_reduction_percent:.1f}% | "
            f"{escape('; '.join(result.notes) or 'OK')} |"
        )

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"""# External Repo Evaluation

Generated at: {generated_at}

Repository fixture: `{repo_path}`
Case file: `{cases_path}`
Retriever mode: `{retriever_mode.value}`

This report validates Context Capsule against a small external-style FastAPI ecommerce repository. It is a regression harness and product signal, not a broad benchmark claim.

## Summary

- Cases: {summary["cases"]}
- PASS: {summary["pass"]}
- WARN: {summary["warn"]}
- FAIL: {summary["fail"]}
- hit@1: {summary["hit_at_1"]}/{summary["cases"]}
- hit@3: {summary["hit_at_3"]}/{summary["cases"]}
- target included in top results: {summary["target_included"]}/{summary["cases"]}
- risk floor satisfied: {summary["risk_floor_ok"]}/{summary["cases"]}
- average estimated token reduction: {summary["average_estimated_reduction_percent"]:.1f}%

## Results

{chr(10).join(rows)}

## Interpretation

- `PASS` means the core target file ranked within the case threshold and risk was not under-warned.
- `WARN` means the target was found, but ranking was weaker than expected or risk was stricter than expected.
- `FAIL` means the core target file was missing or risk was below the expected floor.
- This fixture is intentionally small, so token reduction may be `0.0%`. In small repositories, this harness mainly validates target-file selection and risk floor behavior.

## How To Regenerate

```powershell
.\\.venv\\Scripts\\python.exe scripts\\evaluate_external_repo.py
```
"""


def escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Context Capsule on an external-style fixture repository.")
    parser.add_argument("--repo-path", type=Path, default=DEFAULT_REPO_PATH)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--retriever", choices=[mode.value for mode in RetrievalMode], default=RetrievalMode.KEYWORD.value)
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cases = load_cases(args.cases)
    retriever_mode = RetrievalMode(args.retriever)
    results = evaluate_cases(args.repo_path, cases, retriever_mode=retriever_mode, top_k=args.top_k)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_markdown(results, args.repo_path, args.cases, retriever_mode), encoding="utf-8")

    payload = {
        "summary": summarize(results),
        "results": [asdict(result) for result in results],
        "output": str(args.output),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"{result.verdict} {result.name}: rank={result.best_rank or '-'} risk={result.actual_risk}")
        print(f"wrote {args.output}")

    return 1 if any(result.verdict == "FAIL" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
