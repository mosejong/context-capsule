from pathlib import Path

from scripts.generate_performance_report import build_markdown, build_svg, collect_results


def test_performance_report_contains_all_scenarios():
    results = collect_results()
    markdown = build_markdown(results, Path("docs/assets/performance_comparison.svg"))
    svg = build_svg(results)

    for result in results:
        assert result.name in markdown
        assert result.name in svg

    assert "Performance Comparison" in markdown
    assert "<svg" in svg
    assert "token" in svg.lower()
