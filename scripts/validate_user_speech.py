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

from app.retrievers.persistent_index import build_retrieval_index
from app.scanners.repo_scanner import scan_repo
from app.schemas.capsule_schema import RetrievalMode
from app.services.capsule_service import generate_capsule_result

REPORT_PATH = Path("docs/reports/user_speech_retrieval_qa.md")


@dataclass(frozen=True)
class UserSpeechCase:
    name: str
    task: str
    expected_paths: tuple[str, ...] = ()
    top_limit: int = 5
    min_hits: int = 1
    protected_hints: tuple[str, ...] = ()
    forbidden_paths: tuple[str, ...] = ()
    expect_clarification: bool = False


@dataclass(frozen=True)
class UserSpeechResult:
    name: str
    task: str
    verdict: str
    intent: str
    confidence: str
    protected_hints: list[str]
    retrieval_used_mode: str
    retrieval_fallback_reason: str | None
    baseline_context_scope: str
    top_paths: list[str]
    notes: list[str]


def user_speech_cases() -> list[UserSpeechCase]:
    return [
        UserSpeechCase(
            name="readme_short",
            task="리드미 손보자",
            expected_paths=("README.md",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="readme_portfolio",
            task="README 포폴용으로 다듬자",
            expected_paths=("README.md",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="simple_retriever_colloquial",
            task="심플 리트리버 왜 이럼",
            expected_paths=("app/retrievers/simple_retriever.py",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="simple_retriever_vector",
            task="simple_retriever에 벡터 검색 추가",
            expected_paths=("app/retrievers/simple_retriever.py",),
            top_limit=3,
        ),
        UserSpeechCase(
            name="github_issue_bug",
            task="깃헙 이슈 생성 안됨",
            expected_paths=("app/cli.py", "app/adapters/github_issue_adapter.py"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="local_launcher_bug",
            task="로컬 실행 안돼",
            expected_paths=("run_context_capsule.bat", "scripts/run_dashboard.ps1", "docs/local_app.md"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="token_metric_suspicious",
            task="토큰 계산 뻥튀기 같은데?",
            expected_paths=("app/analyzers/token_analyzer.py", "docs/reports/performance_comparison.md"),
            top_limit=5,
            min_hits=2,
        ),
        UserSpeechCase(
            name="protect_auth_docs_only",
            task="auth는 건드리지 말고 문서만 바꾸자",
            expected_paths=("README.md",),
            top_limit=5,
            protected_hints=("auth",),
            forbidden_paths=("app/auth.py",),
        ),
        UserSpeechCase(
            name="protect_db_output_copy",
            task="DB쪽은 냅두고 출력 문구만 바꾸자",
            expected_paths=("app/generators/capsule_generator.py", "app/generators/output_writer.py", "app/main.py"),
            top_limit=5,
            protected_hints=("db",),
            forbidden_paths=("app/models/user.py",),
        ),
        UserSpeechCase(
            name="ambiguous_this",
            task="이거 왜그래?",
            expect_clarification=True,
        ),
        UserSpeechCase(
            name="ambiguous_previous",
            task="아까 그거 이어서 하자",
            expect_clarification=True,
        ),
    ]


def evaluate_case(repo_path: Path, case: UserSpeechCase) -> UserSpeechResult:
    result = generate_capsule_result(
        repo_path=repo_path,
        task_request=case.task,
        retriever_mode=RetrievalMode.INDEXED,
    )
    capsule = result.capsule
    understanding = capsule.request_understanding
    top_paths = [chunk.path for chunk in capsule.relevant_chunks[: case.top_limit]]
    notes: list[str] = []

    if case.expect_clarification:
        if not understanding.needs_clarification:
            notes.append("expected clarification, but request proceeded")
        if capsule.retrieval_report.used_mode != "clarification_only":
            notes.append(f"expected clarification_only, got {capsule.retrieval_report.used_mode}")
        if capsule.relevant_chunks:
            notes.append("expected no retrieved chunks")
        verdict = "PASS" if not notes else "FAIL"
        return build_result(case, capsule, top_paths, verdict, notes)

    hits = sorted(path for path in case.expected_paths if path in top_paths)
    if len(hits) < case.min_hits:
        notes.append(f"expected at least {case.min_hits} hit(s), got {hits or 'none'}")

    missing_protected = [hint for hint in case.protected_hints if hint not in understanding.protected_hints]
    if missing_protected:
        notes.append(f"missing protected hint(s): {', '.join(missing_protected)}")

    forbidden_hits = [path for path in case.forbidden_paths if path in top_paths]
    if forbidden_hits:
        notes.append(f"forbidden path(s) retrieved: {', '.join(forbidden_hits)}")

    if capsule.retrieval_report.used_mode != "indexed":
        notes.append(f"indexed fallback used: {capsule.retrieval_report.fallback_reason}")

    if capsule.token_budget.baseline_context_scope != "retrieved_file_contents":
        notes.append(f"unexpected baseline scope: {capsule.token_budget.baseline_context_scope}")

    if not notes:
        verdict = "PASS"
    elif hits:
        verdict = "WARN"
    else:
        verdict = "FAIL"
    return build_result(case, capsule, top_paths, verdict, notes)


def build_result(case, capsule, top_paths, verdict: str, notes: list[str]) -> UserSpeechResult:
    understanding = capsule.request_understanding
    return UserSpeechResult(
        name=case.name,
        task=case.task,
        verdict=verdict,
        intent=understanding.intent,
        confidence=understanding.confidence_label,
        protected_hints=understanding.protected_hints,
        retrieval_used_mode=capsule.retrieval_report.used_mode,
        retrieval_fallback_reason=capsule.retrieval_report.fallback_reason,
        baseline_context_scope=capsule.token_budget.baseline_context_scope,
        top_paths=top_paths,
        notes=notes,
    )


def run_validation(repo_path: Path) -> list[UserSpeechResult]:
    files = scan_repo(repo_path)
    build_retrieval_index(files, repo_path)
    return [evaluate_case(repo_path, case) for case in user_speech_cases()]


def build_markdown(results: list[UserSpeechResult], repo_label: str) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    pass_count = sum(1 for result in results if result.verdict == "PASS")
    warn_count = sum(1 for result in results if result.verdict == "WARN")
    fail_count = sum(1 for result in results if result.verdict == "FAIL")
    rows = [
        "| Case | Verdict | Intent | Protected | Retrieval | Baseline | Top Paths | Notes |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for result in results:
        rows.append(
            "| "
            f"{escape_markdown(result.name)} | "
            f"{result.verdict} | "
            f"{escape_markdown(result.intent)} / {escape_markdown(result.confidence)} | "
            f"{escape_markdown(', '.join(result.protected_hints) or 'None')} | "
            f"{escape_markdown(result.retrieval_used_mode)} | "
            f"{escape_markdown(result.baseline_context_scope)} | "
            f"{escape_markdown(', '.join(result.top_paths) or 'None')} | "
            f"{escape_markdown('; '.join(result.notes) or 'OK')} |"
        )

    return f"""# User-Speech Retrieval QA

Generated at: {generated_at}

Repository path: `{repo_label}`

This report validates real Korean colloquial requests against indexed retrieval.

## Summary

- Cases: {len(results)}
- PASS: {pass_count}
- WARN: {warn_count}
- FAIL: {fail_count}

## What Is Checked

- request understanding intent and confidence
- protected hints such as `auth` and `db`
- indexed retrieval usage and visible fallback
- target file appears in top 1-3 or top 1-5 depending on task
- ambiguous requests stop with one clarification question
- token baseline scope is not whole-repo concat

## Results

{chr(10).join(rows)}

## How To Regenerate

```powershell
.\\.venv\\Scripts\\python.exe scripts\\validate_user_speech.py --repo-path .
```
"""


def escape_markdown(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate real user-speech requests against indexed retrieval.")
    parser.add_argument("--repo-path", type=Path, default=Path("."), help="Repository path to scan and index.")
    parser.add_argument("--output", type=Path, default=REPORT_PATH, help="Markdown report output path.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    args = parser.parse_args()

    repo_path = args.repo_path.resolve()
    results = run_validation(repo_path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_markdown(results, str(args.repo_path)), encoding="utf-8")

    if args.json:
        print(json.dumps([asdict(result) for result in results], ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"{result.verdict} {result.name}: {', '.join(result.top_paths) or 'no retrieval'}")
        print(f"wrote {args.output}")

    if any(result.verdict == "FAIL" for result in results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
