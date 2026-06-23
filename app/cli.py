from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from app.adapters.github_issue_adapter import GitHubIssueAdapterError, create_issue_from_packet
from app.analyzers.meeting_analyzer import analyze_project_kickoff, analyze_scrum_notes
from app.generators.output_writer import slugify
from app.schemas.capsule_schema import HandoffTarget, RetrievalMode
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
        "--retriever",
        choices=[item.value for item in RetrievalMode],
        default=RetrievalMode.KEYWORD.value,
        help="Retrieval mode. keyword is the default No-AI fallback; hybrid adds local vector ranking.",
    )
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

    scrum = subparsers.add_parser(
        "scrum-notes",
        help="Generate scrum notes, decisions, next actions, and issue drafts from meeting text.",
    )
    scrum.add_argument("--text", help="Scrum or meeting text.")
    scrum.add_argument("--text-file", type=Path, help="File containing scrum or meeting text.")
    scrum.add_argument("--project-context", default="", help="Optional project context to include in the summary.")
    scrum.add_argument("--feedback", default="", help="Instructor or team-lead feedback to include.")
    scrum.add_argument("--save", action="store_true", help="Save SCRUM_NOTES.md under --output-dir.")
    scrum.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Output root for saved notes.")
    scrum.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    kickoff = subparsers.add_parser(
        "kickoff",
        help="Generate MVP scope, workstreams, issue drafts, and submission checklist from project kickoff text.",
    )
    kickoff.add_argument("--topic", required=True, help="Project or contest topic.")
    kickoff.add_argument("--notes", help="Idea meeting notes.")
    kickoff.add_argument("--notes-file", type=Path, help="File containing idea meeting notes.")
    kickoff.add_argument("--deadline", default="", help="Optional deadline or presentation date.")
    kickoff.add_argument("--constraints", default="", help="Scope, safety, or technical constraints.")
    kickoff.add_argument("--team-context", default="", help="Self-reported team capacity/preferences, not ratings.")
    kickoff.add_argument("--save", action="store_true", help="Save PROJECT_KICKOFF.md under --output-dir.")
    kickoff.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Output root for saved packet.")
    kickoff.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate":
        return run_generate(args)

    if args.command == "create-issue":
        return run_create_issue(args)

    if args.command == "scrum-notes":
        return run_scrum_notes(args)

    if args.command == "kickoff":
        return run_kickoff(args)

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
            retriever_mode=RetrievalMode(args.retriever),
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


def run_scrum_notes(args: argparse.Namespace) -> int:
    try:
        meeting_text = read_text_input(args.text, args.text_file, "scrum-notes")
        output = analyze_scrum_notes(
            meeting_text,
            project_context=args.project_context,
            instructor_feedback=args.feedback,
        )
        saved_output_dir = save_single_markdown_packet(
            args.output_dir,
            "scrum-notes",
            "SCRUM_NOTES.md",
            output.markdown,
        ) if args.save else None
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        data = output.model_dump(mode="json")
        data["saved_output_dir"] = str(saved_output_dir) if saved_output_dir else None
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    print(output.markdown)
    if saved_output_dir:
        print()
        print(f"Saved output: {saved_output_dir}")
    return 0


def run_kickoff(args: argparse.Namespace) -> int:
    try:
        notes = read_text_input(args.notes, args.notes_file, "kickoff")
        output = analyze_project_kickoff(
            topic=args.topic,
            idea_notes=notes,
            deadline=args.deadline,
            constraints=args.constraints,
            team_context=args.team_context,
        )
        saved_output_dir = save_single_markdown_packet(
            args.output_dir,
            "project-kickoff",
            "PROJECT_KICKOFF.md",
            output.markdown,
        ) if args.save else None
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.json:
        data = output.model_dump(mode="json")
        data["saved_output_dir"] = str(saved_output_dir) if saved_output_dir else None
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    print(output.markdown)
    if saved_output_dir:
        print()
        print(f"Saved output: {saved_output_dir}")
    return 0


def read_text_input(inline_text: str | None, text_file: Path | None, command_name: str) -> str:
    if inline_text and text_file:
        raise ValueError(f"{command_name}: pass either inline text or a text file, not both.")
    if text_file:
        return text_file.read_text(encoding="utf-8")
    if inline_text:
        return inline_text
    raise ValueError(f"{command_name}: provide --text/--notes or --text-file/--notes-file.")


def save_single_markdown_packet(output_root: Path, title: str, filename: str, markdown: str) -> Path:
    generated_at = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = output_root / f"{generated_at}_{slugify(title)}"
    suffix = 2
    while output_dir.exists():
        output_dir = output_root / f"{generated_at}_{slugify(title)}_{suffix}"
        suffix += 1
    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / filename).write_text(markdown, encoding="utf-8")
    return output_dir


if __name__ == "__main__":
    raise SystemExit(main())
