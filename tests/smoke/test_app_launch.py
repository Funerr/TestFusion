from __future__ import annotations

from agent.schemas.normalized_case_schema import NormalizedCase


def test_app_launch_case_passes(runner):
    case = NormalizedCase(
        case_id="launch_case_001",
        title="启动应用并验证首页",
        preconditions=["应用已安装"],
        steps=["启动应用"],
        expected=["进入首页", "当前activity正确"],
        ambiguities=[],
    )

    result = runner.run_normalized_case(case)

    assert result.final_status == "PASS"
    assert result.step_results[0].action_status == "passed"
    assert result.assertion_results[0].passed is True
