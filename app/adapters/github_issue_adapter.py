from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

GITHUB_API_URL = "https://api.github.com"
GITHUB_API_VERSION = "2022-11-28"

Transport = Callable[[str, dict[str, Any], dict[str, str]], dict[str, Any]]


class GitHubIssueAdapterError(RuntimeError):
    """Raised when a saved packet cannot be converted into a GitHub issue."""


@dataclass(frozen=True)
class GitHubIssueDraft:
    packet_dir: Path
    title: str
    body: str
    labels: list[str]
    recommended_branch: str | None
    risk_level: str | None
    auto_start_allowed: bool | None

    def payload(self, include_labels: bool = True) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "title": self.title,
            "body": self.body,
        }
        if include_labels and self.labels:
            payload["labels"] = self.labels
        return payload


@dataclass(frozen=True)
class GitHubIssueResult:
    mode: str
    repository: str
    title: str
    labels: list[str]
    payload: dict[str, Any]
    html_url: str | None = None
    number: int | None = None


def load_issue_draft(packet_dir: Path | str) -> GitHubIssueDraft:
    packet_dir = Path(packet_dir)
    metadata_path = packet_dir / "metadata.json"
    issue_path = packet_dir / "GITHUB_ISSUE.md"

    if not packet_dir.exists():
        raise GitHubIssueAdapterError(f"Output packet directory does not exist: {packet_dir}")
    if not metadata_path.exists():
        raise GitHubIssueAdapterError(f"Missing metadata.json in output packet: {packet_dir}")
    if not issue_path.exists():
        raise GitHubIssueAdapterError(f"Missing GITHUB_ISSUE.md in output packet: {packet_dir}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    github_issue = metadata.get("github_issue") or {}
    title = str(github_issue.get("title") or metadata.get("task_request") or "").strip()
    body = issue_path.read_text(encoding="utf-8").strip()
    if not title:
        raise GitHubIssueAdapterError("Saved packet metadata does not contain a GitHub issue title.")
    if not body:
        raise GitHubIssueAdapterError("GITHUB_ISSUE.md is empty.")

    labels = github_issue.get("labels") or []
    if not isinstance(labels, list):
        raise GitHubIssueAdapterError("metadata.json github_issue.labels must be a list.")

    return GitHubIssueDraft(
        packet_dir=packet_dir,
        title=title,
        body=body,
        labels=[str(label) for label in labels],
        recommended_branch=github_issue.get("recommended_branch"),
        risk_level=github_issue.get("risk_level"),
        auto_start_allowed=github_issue.get("auto_start_allowed"),
    )


def create_issue_from_packet(
    packet_dir: Path | str,
    repository: str | None,
    *,
    apply: bool = False,
    include_labels: bool = True,
    token: str | None = None,
    api_url: str = GITHUB_API_URL,
    transport: Transport | None = None,
) -> GitHubIssueResult:
    draft = load_issue_draft(packet_dir)
    normalized_repo = normalize_repository(repository or os.getenv("CONTEXT_CAPSULE_GITHUB_REPOSITORY"))
    payload = draft.payload(include_labels=include_labels)

    if not apply:
        return GitHubIssueResult(
            mode="dry-run",
            repository=normalized_repo or "(not provided)",
            title=draft.title,
            labels=payload.get("labels", []),
            payload=payload,
        )

    if not normalized_repo:
        raise GitHubIssueAdapterError("--repo owner/name or CONTEXT_CAPSULE_GITHUB_REPOSITORY is required with --apply.")

    token = token or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    if not token:
        raise GitHubIssueAdapterError("GITHUB_TOKEN or GH_TOKEN is required with --apply.")

    url = f"{api_url.rstrip('/')}/repos/{normalized_repo}/issues"
    headers = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
        "User-Agent": "context-capsule",
    }
    response = (transport or github_post_json)(url, payload, headers)

    return GitHubIssueResult(
        mode="apply",
        repository=normalized_repo,
        title=draft.title,
        labels=payload.get("labels", []),
        payload=payload,
        html_url=response.get("html_url"),
        number=response.get("number"),
    )


def normalize_repository(repository: str | None) -> str | None:
    if not repository:
        return None
    repository = repository.strip()
    repository = repository.removesuffix(".git")

    github_match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/]+)$", repository)
    if github_match:
        return f"{github_match.group('owner')}/{github_match.group('repo')}"

    if re.fullmatch(r"[^/\s]+/[^/\s]+", repository):
        return repository

    raise GitHubIssueAdapterError("Repository must be in owner/name form or a GitHub repository URL.")


def github_post_json(url: str, payload: dict[str, Any], headers: dict[str, str]) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise GitHubIssueAdapterError(f"GitHub issue creation failed with HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise GitHubIssueAdapterError(f"GitHub issue creation failed: {exc.reason}") from exc
