from __future__ import annotations

import argparse
import json
import statistics
import sys
import tempfile
import time
import tracemalloc
from dataclasses import asdict, dataclass
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi.testclient import TestClient

from app.scanners.repo_scanner import DEFAULT_MAX_FILES, scan_repo_with_report
from app.web.server import app


DEFAULT_REPORT_PATH = Path("docs/reports/scale_and_web_audit.md")


@dataclass(frozen=True)
class ScaleAuditResult:
    requested_files: int
    included_files: int
    truncated: bool
    warning_codes: list[str]
    elapsed_seconds: float
    peak_memory_mb: float


@dataclass(frozen=True)
class WebAuditResult:
    health_status: int
    handoff_status: int
    app_web_selected: bool
    api_version: str


def create_synthetic_repo(root: Path, file_count: int) -> Path:
    repo = root / f"synthetic_{file_count}"
    web_dir = repo / "app" / "web"
    web_dir.mkdir(parents=True)
    (web_dir / "server.py").write_text(
        "def health():\n    return {'status': 'ok'}\n",
        encoding="utf-8",
    )
    remaining = max(0, file_count - 1)
    for index in range(remaining):
        directory = repo / "src" / f"group_{index // 500:03d}"
        directory.mkdir(parents=True, exist_ok=True)
        (directory / f"module_{index:05d}.py").write_text(
            f"def value_{index}():\n    return {index}\n",
            encoding="utf-8",
        )
    return repo


def audit_scale(repo: Path, requested_files: int, repeats: int = 1) -> ScaleAuditResult:
    timings: list[float] = []
    peak_bytes = 0
    report = None
    for _ in range(max(1, repeats)):
        tracemalloc.start()
        started = time.perf_counter()
        report = scan_repo_with_report(repo)
        timings.append(time.perf_counter() - started)
        _, current_peak = tracemalloc.get_traced_memory()
        peak_bytes = max(peak_bytes, current_peak)
        tracemalloc.stop()
    assert report is not None
    return ScaleAuditResult(
        requested_files=requested_files,
        included_files=report.included_file_count,
        truncated=report.truncated,
        warning_codes=[warning.code for warning in report.warnings],
        elapsed_seconds=round(statistics.median(timings), 4),
        peak_memory_mb=round(peak_bytes / (1024 * 1024), 2),
    )


def audit_web(repo: Path) -> WebAuditResult:
    client = TestClient(app)
    health = client.get("/api/health")
    handoff = client.post(
        "/api/work-handoff",
        json={
            "repo_path": str(repo),
            "task_request": "app/web health endpoint 검수",
            "top_k": 5,
            "retriever_mode": "keyword",
        },
    )
    payload = handoff.json() if handoff.status_code == 200 else {}
    selected = any(item.get("path") == "app/web/server.py" for item in payload.get("relevant_files", []))
    return WebAuditResult(
        health_status=health.status_code,
        handoff_status=handoff.status_code,
        app_web_selected=selected,
        api_version=health.json().get("version", "unknown") if health.status_code == 200 else "unknown",
    )


def build_markdown(scale_results: list[ScaleAuditResult], web: WebAuditResult) -> str:
    rows = [
        "| Requested | Included | Truncated | Median Seconds | Peak Memory MB | Warnings |",
        "| ---: | ---: | --- | ---: | ---: | --- |",
    ]
    for item in scale_results:
        rows.append(
            f"| {item.requested_files:,} | {item.included_files:,} | {item.truncated} | "
            f"{item.elapsed_seconds:.4f} | {item.peak_memory_mb:.2f} | "
            f"{', '.join(item.warning_codes) or 'none'} |"
        )
    ten_k_note = (
        f"The default scanner cap is {DEFAULT_MAX_FILES:,} included files. "
        "A 10k fixture is expected to stop at that cap and emit `max_files_reached`; "
        "this is a measured safety boundary, not a 10k full-scan claim."
    )
    return f"""# Scale and app/web Audit

This run-scoped audit measures the local scanner on generated repositories and verifies the FastAPI `app/web` handoff path. It is not a cross-machine benchmark.

## Scale Results

{chr(10).join(rows)}

{ten_k_note}

## app/web Contract

- `/api/health`: {web.health_status}
- `/api/work-handoff`: {web.handoff_status}
- `app/web/server.py` selected for an explicit app/web request: {web.app_web_selected}
- API version: {web.api_version}

## Reproduce

```powershell
.\\.venv\\Scripts\\python.exe scripts\\audit_scale_and_web.py
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit scanner scale boundaries and the app/web API contract.")
    parser.add_argument("--file-count", type=int, action="append", dest="file_counts")
    parser.add_argument("--repeats", type=int, default=1)
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT_PATH)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    file_counts = args.file_counts or [1_000, 5_000, 10_000]

    with tempfile.TemporaryDirectory(prefix="context-capsule-audit-") as temp_dir:
        root = Path(temp_dir)
        repos = [(count, create_synthetic_repo(root, count)) for count in file_counts]
        scale_results = [audit_scale(repo, count, args.repeats) for count, repo in repos]
        web = audit_web(repos[0][1])

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build_markdown(scale_results, web), encoding="utf-8")
    payload = {
        "scale": [asdict(item) for item in scale_results],
        "web": asdict(web),
        "output": str(args.output),
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(f"wrote {args.output}")

    web_ok = web.health_status == 200 and web.handoff_status == 200 and web.app_web_selected
    warning_ok = all(
        not item.truncated or "max_files_reached" in item.warning_codes or "max_total_bytes_reached" in item.warning_codes
        for item in scale_results
    )
    return 0 if web_ok and warning_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

