from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from app.adapters.github_issue_adapter import GitHubIssueAdapterError, create_issue_from_packet
from app.schemas.capsule_schema import HandoffTarget
from app.services.capsule_service import generate_capsule_result, summarize_generation_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Context Capsule command line tools.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate = subparsers.add_parser(
        "generate",
        help="Generate a Context Capsule packet from a local repository and task request.",
    )
    generate.add_argument("--repo-path", default=".", help="Local repository path to scan.")
    generate.add_argument("--task", required=True, help="Task request to turn into a handoff packet.")
    generate.add_argument(
        "--forbidden-rule",
        action="append",
        default=[],
        help="Forbidden or caution rule. Repeat this option for multiple rules.",
    )
    generate.add_argument("--rules-file", type=Path, help="Text file with one forbidden/caution rule per line.")
    generate.add_argument("--top-k", type=int, default=8, help="Number of retrieved chunks.")
    generate.add_argument(
        "--target",
        choices=["all", "ai", "teammate", "junior", "self"],
        default="all",
        help="Primary handoff target. all maps to ai_tool while still saving every output file.",
    )
    generate.add_argument("--save", action="store_true", help="Write the generated packet under --output-dir.")
    generate.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Output root for saved packets.")
    generate.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    create_issue = subparsers.add_parser(
        "create-issue",
        help="Create or preview a GitHub issue from a saved Context Capsule packet.",
    )
    create_issue.add_argument("packet_dir", type=Path, help="Path to an outputs/YYYYMMDD_slug packet directory.")
    create_issue.add_argument(
        "--repo",
        help="Target repository in owner/name form. Can also be set via CONTEXT_CAPSULE_GITHUB_REPOSITORY.",
    )
    create_issue.add_argument(
        "--apply",
        action="store_true",
        help="Actually create the GitHub issue. Default is dry-run.",
    )
    create_issue.add_argument(
        "--skip-labels",
        action="store_true",
        help="Do not send labels in the GitHub issue payload.",
    )
    create_issue.add_argument(
        "--json",
        action="store_true",
        help="Print machine-readable JSON output.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate":
        return run_generate(args)

    if args.command == "create-issue":
        return run_create_issue(args)

    parser.error(f"Unknown command: {args.command}")
    return 2


def configure_stdio() -> None:
    """Keep JSON/Markdown previews readable on Windows terminals."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")


def run_generate(args: argparse.Namespace) -> int:
    try:
        rules = collect_forbidden_rules(args.forbidden_rule, args.rules_file)
        result = generate_capsule_result(
            repo_path=args.repo_path,
            task_request=args.task,
            forbidden_rules=rules,
            top_k=args.top_k,
            handoff_target=parse_target(args.target),
            save=args.save,
            output_root=args.output_dir,
        )
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    summary = summarize_generation_result(result)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    print("Context Capsule generated.")
    print(f"Scanned files: {summary['scanned_file_count']}")
    print(f"Handoff target: {summary['handoff_target']}")
    print(f"Risk level: {summary['github_issue']['risk_level']}")
    print(f"Auto-start allowed: {summary['github_issue']['auto_start_allowed']}")
    print(f"Token reduction: {summary['token_budget']['estimated_reduction_percent']:.1f}%")
    if summary["saved_output_dir"]:
        print(f"Saved output: {summary['saved_output_dir']}")
        print("Next dry-run:")
        print(f"  python -m app.cli create-issue {summary['saved_output_dir']} --repo owner/name --json")
    else:
        print("Not saved. Pass --save to write an outputs packet.")
    return 0


def collect_forbidden_rules(inline_rules: list[str], rules_file: Path | None) -> list[str]:
    rules = [rule.strip() for rule in inline_rules if rule.strip()]
    if rules_file:
        rules.extend(line.strip() for line in rules_file.read_text(encoding="utf-8").splitlines() if line.strip())
    return rules


def parse_target(target: str) -> HandoffTarget:
    mapping = {
        "all": HandoffTarget.AI_TOOL,
        "ai": HandoffTarget.AI_TOOL,
        "teammate": HandoffTarget.TEAMMATE,
        "junior": HandoffTarget.JUNIOR_DEVELOPER,
        "self": HandoffTarget.FUTURE_ME,
    }
    return mapping[target]


def run_create_issue(args: argparse.Namespace) -> int:
    try:
        result = create_issue_from_packet(
            args.packet_dir,
            args.repo,
            apply=args.apply,
            include_labels=not args.skip_labels,
        )
    except GitHubIssueAdapterError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
        return 0

    if result.mode == "dry-run":
        print("Dry-run: GitHub issue was not created.")
        print(f"Repository: {result.repository}")
        print(f"Title: {result.title}")
        print(f"Labels: {', '.join(result.labels) if result.labels else '(none)'}")
        print(f"Body characters: {len(result.payload['body'])}")
        print("Run again with --apply to create the issue.")
        return 0

    print("GitHub issue created.")
    print(f"Repository: {result.repository}")
    print(f"Title: {result.title}")
    if result.number is not None:
        print(f"Issue number: {result.number}")
    if result.html_url:
        print(f"URL: {result.html_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
