from __future__ import annotations


def test_long_run_suite_collects_reports(runner):
    results = [runner.run_text_case("启动应用并检查首页") for _ in range(2)]

    assert all(item.artifacts.ai_report for item in results)
