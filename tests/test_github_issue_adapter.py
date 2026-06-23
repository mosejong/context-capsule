import json

from app.adapters.github_issue_adapter import (
    GitHubIssueAdapterError,
    create_issue_from_packet,
    load_issue_draft,
    normalize_repository,
)


def write_packet(tmp_path):
    packet_dir = tmp_path / "20260623_090000_demo"
    packet_dir.mkdir()
    (packet_dir / "GITHUB_ISSUE.md").write_text("# Issue\n\nBody", encoding="utf-8")
    (packet_dir / "metadata.json").write_text(
        json.dumps(
            {
                "task_request": "Fallback title",
                "github_issue": {
                    "title": "Create saved packet issue",
                    "recommended_branch": "task/create-saved-packet-issue",
                    "labels": ["context-capsule", "risk:low"],
                    "risk_level": "LOW",
                    "auto_start_allowed": True,
                    "acceptance_criteria": ["Issue created"],
                },
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return packet_dir


def test_load_issue_draft_from_saved_packet(tmp_path):
    packet_dir = write_packet(tmp_path)

    draft = load_issue_draft(packet_dir)

    assert draft.title == "Create saved packet issue"
    assert draft.body == "# Issue\n\nBody"
    assert draft.labels == ["context-capsule", "risk:low"]
    assert draft.recommended_branch == "task/create-saved-packet-issue"
    assert draft.risk_level == "LOW"
    assert draft.auto_start_allowed is True


def test_create_issue_dry_run_does_not_require_repo_or_token(tmp_path, monkeypatch):
    packet_dir = write_packet(tmp_path)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)

    result = create_issue_from_packet(packet_dir, repository=None, apply=False)

    assert result.mode == "dry-run"
    assert result.repository == "(not provided)"
    assert result.payload["title"] == "Create saved packet issue"
    assert result.payload["labels"] == ["context-capsule", "risk:low"]


def test_create_issue_apply_requires_repository_and_token(tmp_path, monkeypatch):
    packet_dir = write_packet(tmp_path)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.delenv("GH_TOKEN", raising=False)

    try:
        create_issue_from_packet(packet_dir, repository="mosejong/context-capsule", apply=True)
    except GitHubIssueAdapterError as exc:
        assert "GITHUB_TOKEN or GH_TOKEN" in str(exc)
    else:
        raise AssertionError("Expected token error")


def test_create_issue_apply_uses_transport(tmp_path):
    packet_dir = write_packet(tmp_path)
    calls = []

    def fake_transport(url, payload, headers):
        calls.append((url, payload, headers))
        return {"html_url": "https://github.com/mosejong/context-capsule/issues/7", "number": 7}

    result = create_issue_from_packet(
        packet_dir,
        repository="https://github.com/mosejong/context-capsule.git",
        apply=True,
        token="fake-token",
        transport=fake_transport,
    )

    assert result.mode == "apply"
    assert result.repository == "mosejong/context-capsule"
    assert result.html_url == "https://github.com/mosejong/context-capsule/issues/7"
    assert result.number == 7
    url, payload, headers = calls[0]
    assert url == "https://api.github.com/repos/mosejong/context-capsule/issues"
    assert payload["title"] == "Create saved packet issue"
    assert payload["labels"] == ["context-capsule", "risk:low"]
    assert headers["Authorization"] == "Bearer fake-token"


def test_create_issue_can_skip_labels(tmp_path):
    packet_dir = write_packet(tmp_path)

    result = create_issue_from_packet(packet_dir, repository="mosejong/context-capsule", include_labels=False)

    assert "labels" not in result.payload
    assert result.labels == []


def test_normalize_repository_accepts_owner_name_and_github_url():
    assert normalize_repository("mosejong/context-capsule") == "mosejong/context-capsule"
    assert (
        normalize_repository("https://github.com/mosejong/context-capsule.git") == "mosejong/context-capsule"
    )
