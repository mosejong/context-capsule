from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.validate_mvp import ScenarioResult, evaluate_scenario, scenarios

REPORT_PATH = Path("docs/reports/performance_comparison.md")
SVG_PATH = Path("docs/assets/performance_comparison.svg")


def collect_results() -> list[ScenarioResult]:
    return [evaluate_scenario(scenario) for scenario in scenarios()]


def build_markdown(results: list[ScenarioResult], svg_path: Path) -> str:
    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = [
        "| Scenario | Auto Start | Candidate Tokens | Capsule Tokens | Reduction | Relevant File Hit | Unrelated Files | Success Proxy | Scope Escape |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | --- | --- |",
    ]
    for result in results:
        rows.append(
            "| "
            f"{result.name} | "
            f"{'allowed' if result.auto_start_allowed else 'blocked'} | "
            f"{result.raw_context_tokens:,} | "
            f"{result.handoff_prompt_tokens:,} | "
            f"{result.reduction_percent:.1f}% | "
            f"{result.relevant_file_hit_rate:.1f}% | "
            f"{result.unrelated_file_count} | "
            f"{'pass' if result.success_proxy else 'fail'} | "
            f"{'yes' if result.scope_escape else 'no'} |"
        )

    best = max(results, key=lambda item: item.reduction_percent)
    blocked = [result.name for result in results if not result.auto_start_allowed]
    avg_reduction = sum(result.reduction_percent for result in results) / len(results)
    avg_hit_rate = sum(result.relevant_file_hit_rate for result in results) / len(results)
    success_count = sum(1 for result in results if result.success_proxy)
    scope_escape_count = sum(1 for result in results if result.scope_escape)
    relative_svg = "../assets/performance_comparison.svg"

    return f"""# Performance Comparison v2

Generated at: {generated_at}

This report is generated from the MVP validation scenarios.

![Performance comparison]({relative_svg})

## Summary

- Scenarios validated: {len(results)}
- Best token reduction: {best.name} ({best.reduction_percent:.1f}%)
- Average token reduction: {avg_reduction:.1f}%
- Average relevant file hit rate: {avg_hit_rate:.1f}%
- Success proxy pass rate: {success_count}/{len(results)}
- Scope escape count: {scope_escape_count}
- Auto-start blocked scenarios: {', '.join(blocked) if blocked else 'none'}

## What Is Compared

- Candidate context: sending the full contents of retrieved candidate files without compression.
- Capsule tokens: sending the generated handoff packet instead.
- Relevant file hit: whether expected files for the task were retrieved.
- Success proxy: validation assertions passed for the scenario.
- Scope escape: validation detected retrieval outside the expected task scope.

## Metrics

{chr(10).join(rows)}

## How To Regenerate

```powershell
.\\.venv\\Scripts\\python.exe scripts\\generate_performance_report.py
```
"""


def build_svg(results: list[ScenarioResult]) -> str:
    width = 980
    row_height = 72
    top = 92
    left = 290
    chart_width = 560
    height = top + (len(results) * row_height) + 70
    max_reduction = 100

    rows = []
    for index, result in enumerate(results):
        y = top + index * row_height
        bar_width = int(chart_width * result.reduction_percent / max_reduction)
        status_color = "#16a34a" if result.auto_start_allowed else "#dc2626"
        status_label = "allowed" if result.auto_start_allowed else "blocked"
        rows.append(
            f"""
  <text x="32" y="{y + 27}" class="scenario">{escape_xml(result.name)}</text>
  <rect x="{left}" y="{y}" width="{chart_width}" height="28" rx="6" class="track" />
  <rect x="{left}" y="{y}" width="{bar_width}" height="28" rx="6" class="bar" />
  <text x="{left + chart_width + 16}" y="{y + 20}" class="metric">{result.reduction_percent:.1f}%</text>
  <text x="{left}" y="{y + 52}" class="detail">raw {result.raw_context_tokens:,} -> capsule {result.handoff_prompt_tokens:,} tokens | hit {result.relevant_file_hit_rate:.1f}% | scope escape {'yes' if result.scope_escape else 'no'}</text>
  <circle cx="{width - 128}" cy="{y + 48}" r="6" fill="{status_color}" />
  <text x="{width - 114}" y="{y + 53}" class="status">{status_label}</text>
"""
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">Context Capsule Performance Comparison v2</title>
  <desc id="desc">Token reduction, relevant-file hit rate, success proxy, and auto-start gate results for MVP validation scenarios.</desc>
  <style>
    .bg {{ fill: #f8fafc; }}
    .title {{ font: 700 26px Arial, sans-serif; fill: #0f172a; }}
    .subtitle {{ font: 14px Arial, sans-serif; fill: #475569; }}
    .scenario {{ font: 700 15px Arial, sans-serif; fill: #0f172a; }}
    .detail {{ font: 12px Arial, sans-serif; fill: #64748b; }}
    .metric {{ font: 700 15px Arial, sans-serif; fill: #0f172a; }}
    .status {{ font: 700 12px Arial, sans-serif; fill: #334155; }}
    .track {{ fill: #e2e8f0; }}
    .bar {{ fill: #2563eb; }}
  </style>
  <rect width="{width}" height="{height}" rx="18" class="bg" />
  <text x="32" y="42" class="title">Context Capsule Performance Comparison v2</text>
  <text x="32" y="68" class="subtitle">Token reduction, relevant-file hit rate, success proxy, and auto-start gate.</text>
  {''.join(rows)}
</svg>
"""


def escape_xml(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def write_report() -> tuple[Path, Path]:
    results = collect_results()
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SVG_PATH.parent.mkdir(parents=True, exist_ok=True)
    SVG_PATH.write_text(build_svg(results), encoding="utf-8")
    REPORT_PATH.write_text(build_markdown(results, SVG_PATH), encoding="utf-8")
    return REPORT_PATH, SVG_PATH


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Context Capsule performance comparison report.")
    parser.parse_args()
    report_path, svg_path = write_report()
    print(f"wrote {report_path}")
    print(f"wrote {svg_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
