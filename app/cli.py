from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

from app.adapters.github_issue_adapter import GitHubIssueAdapterError, create_issue_from_packet
from app.analyzers.meeting_analyzer import analyze_project_health, analyze_project_kickoff, analyze_scrum_notes
from app.generators.feedback_template_generator import build_feedback_template
from app.generators.output_writer import slugify
from app.retrievers.persistent_index import build_retrieval_index, default_index_path
from app.scanners.repo_scanner import scan_repo
from app.schemas.capsule_schema import BetaFeedback, HandoffTarget, RetrievalMode
from app.services.capsule_service import generate_capsule_result, summarize_generation_result
from app.services.doctor_service import build_doctor_report
from app.services.feedback_service import review_feedback, save_beta_feedback, save_feedback_review


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
        help=(
            "Retrieval mode. keyword is the default No-AI fallback; "
            "hybrid adds local vector ranking; indexed reuses a local persistent index."
        ),
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

    index = subparsers.add_parser(
        "index",
        help="Build a local persistent retrieval index for --retriever indexed.",
    )
    index.add_argument("--repo-path", default=".", help="Local repository path to scan.")
    index.add_argument("--index-path", type=Path, help="Optional path for retrieval_index.json.")
    index.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    doctor = subparsers.add_parser(
        "doctor",
        help="Check local install, repository scan, safety defaults, and release readiness.",
    )
    doctor.add_argument("--repo-path", default=".", help="Local repository path to check.")
    doctor.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    feedback = subparsers.add_parser(
        "feedback-template",
        help="Generate a KDT beta tester feedback template.",
    )
    feedback.add_argument("--project-name", default="", help="Project or repository being tested.")
    feedback.add_argument("--tester-name", default="", help="Optional tester name or nickname.")
    feedback.add_argument("--save", action="store_true", help="Save KDT_FEEDBACK_TEMPLATE.md under --output-dir.")
    feedback.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Output root for saved template.")
    feedback.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    feedback_save = subparsers.add_parser(
        "feedback-save",
        help="Save one beta tester feedback packet under outputs/feedback.",
    )
    feedback_save.add_argument("--version", default="0.2.6", help="Context Capsule version under test.")
    feedback_save.add_argument("--mode", default="work", help="Mode being tested: work, scrum, kickoff, health, etc.")
    feedback_save.add_argument("--project-name", default="", help="Project or repository being tested.")
    feedback_save.add_argument("--repo-path", default="", help="Local repository path, if available.")
    feedback_save.add_argument("--repo-type", default="", help="Repository type or short description.")
    feedback_save.add_argument("--request", default="", help="Tester input request.")
    feedback_save.add_argument("--expected-file", action="append", default=[], help="Expected target file. Repeatable.")
    feedback_save.add_argument("--actual-file", action="append", default=[], help="Actual top file. Repeatable.")
    feedback_save.add_argument("--risk-result", default="", help="Risk result shown to tester.")
    feedback_save.add_argument("--token-evidence", default="", help="Token evidence shown to tester.")
    feedback_save.add_argument("--result-order-feedback", default="", help="Whether the tester understood which result tab to read first.")
    feedback_save.add_argument("--workflow-trace-feedback", default="", help="Tester feedback about the Work Handoff workflow trace tab.")
    feedback_save.add_argument("--confusing-part", default="", help="What confused the tester.")
    feedback_save.add_argument("--reuse-willingness", default="", help="Tester willingness to use again.")
    feedback_save.add_argument("--notes", default="", help="Additional tester notes.")
    feedback_save.add_argument("--screenshot-note", default="", help="Screenshot description or external note.")
    feedback_save.add_argument("--output-dir", type=Path, default=Path("outputs") / "feedback", help="Feedback output root.")
    feedback_save.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    feedback_review = subparsers.add_parser(
        "feedback-review",
        help="Review saved beta feedback and suggest next patch priorities.",
    )
    feedback_review.add_argument("--feedback-root", type=Path, default=Path("outputs") / "feedback", help="Feedback root.")
    feedback_review.add_argument("--save", action="store_true", help="Save FEEDBACK_REVIEW.md under --output-dir.")
    feedback_review.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Review output root.")
    feedback_review.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

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

    health = subparsers.add_parser(
        "health",
        help="Estimate MVP/prototype readiness and missing meeting items from project status text.",
    )
    health.add_argument("--text", help="Project status, scrum notes, or meeting notes.")
    health.add_argument("--text-file", type=Path, help="File containing project status text.")
    health.add_argument("--project-context", default="", help="Optional project context.")
    health.add_argument("--deadline", default="", help="Optional deadline or next review point.")
    health.add_argument("--my-scope", default="", help="Your folder/function/file scope for ownership checking.")
    health.add_argument("--save", action="store_true", help="Save PROJECT_HEALTH.md under --output-dir.")
    health.add_argument("--output-dir", type=Path, default=Path("outputs"), help="Output root for saved packet.")
    health.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    configure_stdio()
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "generate":
        return run_generate(args)

    if args.command == "index":
        return run_index(args)

    if args.command == "doctor":
        return run_doctor(args)

    if args.command == "feedback-template":
        return run_feedback_template(args)

    if args.command == "feedback-save":
        return run_feedback_save(args)

    if args.command == "feedback-review":
        return run_feedback_review(args)

    if args.command == "create-issue":
        return run_create_issue(args)

    if args.command == "scrum-notes":
        return run_scrum_notes(args)

    if args.command == "kickoff":
        return run_kickoff(args)

    if args.command == "health":
        return run_health(args)

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


def run_index(args: argparse.Namespace) -> int:
    try:
        repo_path = Path(args.repo_path)
        files = scan_repo(repo_path)
        result = build_retrieval_index(files, repo_path=repo_path, index_path=args.index_path)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    data = {
        "index_path": str(result.index_path),
        "default_index_path": str(default_index_path(args.repo_path)),
        "provider": result.provider_name,
        "file_count": result.file_count,
        "chunk_count": result.chunk_count,
    }
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("Context Capsule retrieval index built.")
        print(f"Index path: {data['index_path']}")
        print(f"Provider: {data['provider']}")
        print(f"Files: {data['file_count']}")
        print(f"Chunks: {data['chunk_count']}")
        print("Use: python -m app.cli generate --repo-path . --task \"...\" --retriever indexed")
    return 0


def run_doctor(args: argparse.Namespace) -> int:
    report = build_doctor_report(args.repo_path)
    data = report.to_dict()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print("Context Capsule doctor")
        print(f"Status: {report.status}")
        print(f"Repo: {report.repo_path}")
        print(f"Python: {report.python_version}")
        print(f"Scanned files: {report.scanned_file_count}")
        for check in report.checks:
            print(f"[{check.status}] {check.name}: {check.detail}")
            if check.hint:
                print(f"  hint: {check.hint}")
    return 1 if report.status == "FAIL" else 0


def run_feedback_template(args: argparse.Namespace) -> int:
    template = build_feedback_template(
        project_name=args.project_name,
        tester_name=args.tester_name,
    )
    saved_output_dir = save_single_markdown_packet(
        args.output_dir,
        "kdt-feedback-template",
        "KDT_FEEDBACK_TEMPLATE.md",
        template.markdown,
    ) if args.save else None

    data = template.to_dict()
    data["saved_output_dir"] = str(saved_output_dir) if saved_output_dir else None
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    print(template.markdown)
    if saved_output_dir:
        print()
        print(f"Saved output: {saved_output_dir}")
    return 0


def run_feedback_save(args: argparse.Namespace) -> int:
    try:
        feedback = BetaFeedback(
            version=args.version,
            mode=args.mode,
            project_name=args.project_name,
            repo_path=args.repo_path,
            repo_type=args.repo_type,
            request_text=args.request,
            expected_files=args.expected_file,
            actual_top_files=args.actual_file,
            risk_result=args.risk_result,
            token_evidence=args.token_evidence,
            result_order_feedback=args.result_order_feedback,
            workflow_trace_feedback=args.workflow_trace_feedback,
            confusing_part=args.confusing_part,
            reuse_willingness=args.reuse_willingness,
            notes=args.notes,
            screenshot_note=args.screenshot_note,
        )
        result = save_beta_feedback(feedback, output_root=args.output_dir)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    data = result.model_dump(mode="json")
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    print("Beta feedback saved.")
    print(f"Output: {result.output_dir}")
    print(f"Markdown: {result.markdown_path}")
    print(f"JSON: {result.json_path}")
    if result.redacted_secret_count or result.redacted_prompt_injection_count:
        print(
            "Redacted: "
            f"{result.redacted_secret_count} secret(s), "
            f"{result.redacted_prompt_injection_count} prompt-injection line(s)"
        )
    return 0


def run_feedback_review(args: argparse.Namespace) -> int:
    try:
        output = review_feedback(args.feedback_root)
        saved_output_dir = save_feedback_review(output, args.output_dir) if args.save else None
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


def run_health(args: argparse.Namespace) -> int:
    try:
        status_text = read_text_input(args.text, args.text_file, "health")
        output = analyze_project_health(
            status_text=status_text,
            project_context=args.project_context,
            deadline=args.deadline,
            my_scope=args.my_scope,
        )
        saved_output_dir = save_single_markdown_packet(
            args.output_dir,
            "project-health",
            "PROJECT_HEALTH.md",
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
