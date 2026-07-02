from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.retrievers.hybrid_retriever import build_default_embedding_provider
from app.retrievers.persistent_index import build_retrieval_index
from app.scanners.repo_scanner import scan_repo
from app.schemas.capsule_schema import RetrievalMode
from app.services.capsule_service import generate_capsule_result
from scripts.evaluate_external_repo import (
    DEFAULT_CASES_PATH,
    DEFAULT_REPO_PATH,
    RISK_PRIORITY,
    ExternalRepoCase,
    first_rank,
    load_cases,
)

DEFAULT_REPORT_PATH = Path("docs/reports/retrieval_mode_benchmark.md")


@dataclass(frozen=True)
class RetrievalModeBenchmarkResult:
    mode: str
    used_mode: str
    fallback_reason: str | None
    case_name: str
    task: str
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
    elapsed_ms: float
    verdict: str
    notes: list[str]


def prepare_mode(repo_path: Path, mode: RetrievalMode) -> str:
    if mode != RetrievalMode.INDEXED:
        return "not_required"
    files = scan_repo(repo_path)
    provider = build_default_embedding_provider()
    build_retrieval_index(files, repo_path, embedding_provider=provider)
    return provider.name


def evaluate_case(
    repo_path: Path,
    case: ExternalRepoCase,
    mode: RetrievalMode,
    top_k: int,
) -> RetrievalModeBenchmarkResult:
    started = time.perf_counter()
    result = generate_capsule_result(
        repo_path=repo_path,
        task_request=case.task,
        retriever_mode=mode,
        top_k=top_k,
    )
    elapsed_ms = (time.perf_counter() - started) * 1000

    capsule = result.capsule
    top_paths = [chunk.path for chunk in capsule.relevant_chunks[:top_k]]
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
    if capsule.retrieval_report.used_mode != mode.value:
        notes.append(f"used {capsule.retrieval_report.used_mode}: {capsule.retrieval_report.fallback_reason}")

    verdict = classify_verdict(target_included, best_rank, case.max_rank_for_pass, risk_floor_ok)
    return RetrievalModeBenchmarkResult(
        mode=mode.value,
        used_mode=capsule.retrieval_report.used_mode,
        fallback_reason=capsule.retrieval_report.fallback_reason,
        case_name=case.name,
        task=case.task,
        expected_paths=case.expected_paths,
        top_paths=top_paths,
        best_rank=best_rank,
        hit_at_1=hit_at_1,
        hit_at_3=hit_at_3,
        target_included=target_included,
        expected_risk=case.expected_risk,
        actual_risk=actual_risk,
        risk_floor_ok=risk_floor_ok,
        estimated_reduction_percent=capsule.token_budget.estimated_reduction_percent,
        elapsed_ms=round(elapsed_ms, 2),
        verdict=verdict,
        notes=notes,
    )


def classify_verdict(target_included: bool, best_rank: int | None, max_rank_for_pass: int, risk_floor_ok: bool) -> str:
    if not target_included or not risk_floor_ok:
        return "FAIL"
    if best_rank and best_rank <= max_rank_for_pass:
        return "PASS"
    return "WARN"


def evaluate_modes(
    repo_path: Path,
    cases: list[ExternalRepoCase],
    modes: list[RetrievalMode],
    top_k: int,
) -> tuple[list[RetrievalModeBenchmarkResult], dict[str, str]]:
    providers: dict[str, str] = {}
    results: list[RetrievalModeBenchmarkResult] = []
    for mode in modes:
        providers[mode.value] = prepare_mode(repo_path, mode)
        for case in cases:
            results.append(evaluate_case(repo_path, case, mode, top_k))
    return results, providers


def summarize(results: list[RetrievalModeBenchmarkResult]) -> dict[str, dict[str, float | int | str]]:
    by_mode: dict[str, list[RetrievalModeBenchmarkResult]] = {}
    for result in results:
        by_mode.setdefault(result.mode, []).append(result)

    summary: dict[str, dict[str, float | int | str]] = {}
    for mode, items in by_mode.items():
        total = len(items)
        summary[mode] = {
            "cases": total,
            "pass": sum(1 for item in items if item.verdict == "PASS"),
            "warn": sum(1 for item in items if item.verdict == "WARN"),
            "fail": sum(1 for item in items if item.verdict == "FAIL"),
            "hit_at_1": sum(1 for item in items if item.hit_at_1),
            "hit_at_3": sum(1 for item in items if item.hit_at_3),
            "target_included": sum(1 for item in items if item.target_included),
            "risk_floor_ok": sum(1 for item in items if item.risk_floor_ok),
            "avg_elapsed_ms": round(sum(item.elapsed_ms for item in items) / total, 2) if total else 0.0,
            "avg_reduction": round(
                sum(item.estimated_reduction_percent for item in items) / total,
                1,
            )
            if total
            else 0.0,
            "used_modes": ", ".join(sorted({item.used_mode for item in items})),
        }
    return summary


def build_markdown(
    results: list[RetrievalModeBenchmarkResult],
    providers: dict[str, str],
    repo_path: Path,
    cases_path: Path,
) -> str:
    summary = summarize(results)
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    embedding_model = os.getenv("CONTEXT_CAPSULE_EMBEDDING_MODEL") or "hash_local_v1"

    summary_rows = [
        "| Mode | Cases | PASS | WARN | FAIL | hit@1 | hit@3 | Included | Risk OK | Avg ms | Avg reduction | Used modes |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |",
    ]
    for mode, item in summary.items():
        summary_rows.append(
            "| "
            f"{mode} | {item['cases']} | {item['pass']} | {item['warn']} | {item['fail']} | "
            f"{item['hit_at_1']} | {item['hit_at_3']} | {item['target_included']} | "
            f"{item['risk_floor_ok']} | {item['avg_elapsed_ms']} | {item['avg_reduction']}% | "
            f"{escape(str(item['used_modes']))} |"
        )

    detail_rows = [
        "| Mode | Case | Verdict | Best Rank | Expected | Top Paths | Risk | ms | Notes |",
        "| --- | --- | --- | ---: | --- | --- | --- | ---: | --- |",
    ]
    for result in results:
        detail_rows.append(
            "| "
            f"{result.mode} | {escape(result.case_name)} | {result.verdict} | {result.best_rank or '-'} | "
            f"{escape(', '.join(result.expected_paths))} | {escape(', '.join(result.top_paths[:5]))} | "
            f"{result.actual_risk} (expected >= {result.expected_risk}) | {result.elapsed_ms:.2f} | "
            f"{escape('; '.join(result.notes) or 'OK')} |"
        )

    provider_rows = ["| Mode | Provider / preparation |", "| --- | --- |"]
    for mode, provider in providers.items():
        provider_rows.append(f"| {mode} | {escape(provider)} |")

    return f"""# Retrieval Mode Benchmark

Generated at: {generated_at}

Repository fixture: `{repo_path}`
Case file: `{cases_path}`
Embedding model setting: `{embedding_model}`

This report compares retrieval modes on the same external-style fixture. It is a local quality gate for choosing Korean/multilingual embedding candidates, not a broad benchmark claim.

## Provider Setup

{chr(10).join(provider_rows)}

## Summary

{chr(10).join(summary_rows)}

## Results

{chr(10).join(detail_rows)}

## How To Regenerate

```powershell
.\\.venv\\Scripts\\python.exe scripts\\benchmark_retrieval_modes.py --modes keyword hybrid indexed
```

To test a local multilingual model:

```powershell
$env:CONTEXT_CAPSULE_EMBEDDING_MODEL = "BAAI/bge-m3"
.\\.venv\\Scripts\\python.exe scripts\\benchmark_retrieval_modes.py --modes hybrid indexed
```
"""


def escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark retrieval modes on the external-style fixture.")
    parser.add_argument("--repo-path", type=Path, default=DEFAULT_REPO_PATH)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES_PATH)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument(
        "--modes",
        nargs="+",
        choices=[mode.value for mode in RetrievalMode],
        default=[RetrievalMode.KEYWORD.value, RetrievalMode.HYBRID.value, RetrievalMode.INDEXED.value],
    )
    parser.add_argument("--top-k", type=int, default=8)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    cases = load_cases(args.cases)
    modes = [RetrievalMode(mode) for mode in args.modes]
    results, providers = evaluate_modes(args.repo_path, cases, modes, args.top_k)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_markdown(results, providers, args.repo_path, args.cases), encoding="utf-8")

    payload = {
        "summary": summarize(results),
        "providers": providers,
        "results": [asdict(result) for result in results],
        "output": str(args.output),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for mode, item in payload["summary"].items():
            print(
                f"{mode}: PASS={item['pass']} WARN={item['warn']} FAIL={item['fail']} "
                f"hit@1={item['hit_at_1']}/{item['cases']} hit@3={item['hit_at_3']}/{item['cases']}"
            )
        print(f"wrote {args.output}")

    return 1 if any(result.verdict == "FAIL" for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
