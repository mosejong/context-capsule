from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

from app.adapters.github_issue_adapter import GitHubIssueAdapterError, create_issue_from_packet


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Context Capsule command line tools.")
    subparsers = parser.add_subparsers(dest="command", required=True)

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
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "create-issue":
        return run_create_issue(args)

    parser.error(f"Unknown command: {args.command}")
    return 2


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
