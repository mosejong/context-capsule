from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.retrievers.persistent_index import build_retrieval_index
from app.scanners.repo_scanner import scan_repo
from scripts.validate_user_speech import evaluate_case, user_speech_cases

DEMO_CASE_NAMES = (
    "readme_short",
    "simple_retriever_colloquial",
    "protect_auth_docs_only",
    "ambiguous_this",
)


def run_user_speech_demo(repo_path: Path) -> list[dict]:
    files = scan_repo(repo_path)
    build_retrieval_index(files, repo_path)
    cases_by_name = {case.name: case for case in user_speech_cases()}
    return [asdict(evaluate_case(repo_path, cases_by_name[name])) for name in DEMO_CASE_NAMES]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Run a short v0.1.8 user-speech demo.")
    parser.add_argument("--repo-path", type=Path, default=Path("."), help="Repository path to scan and index.")
    parser.add_argument("--json", action="store_true", help="Print full JSON result.")
    args = parser.parse_args()

    results = run_user_speech_demo(args.repo_path.resolve())
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return 0

    print("Context Capsule v0.1.8 user-speech demo")
    print("Builds a local index, normalizes rough Korean requests, and shows target files.")
    for result in results:
        top_paths = ", ".join(result["top_paths"][:3]) or "clarification_only"
        protected = ", ".join(result["protected_hints"]) or "none"
        print(
            f"{result['verdict']} | {result['task']} "
            f"-> {top_paths} | intent={result['intent']} | protected={protected}"
        )
    print("No code changes or GitHub writes were performed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
