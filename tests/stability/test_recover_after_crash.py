from __future__ import annotations


def test_recover_after_crash_uses_recover_flow(runner):
    runner.device_manager.device_state.crashed = True
    result = runner.run_text_case("切后台再回来没问题")

    assert result.final_status in {"PASS", "NEEDS_REVIEW"}
    assert any("设备恢复" in step.skill for step in result.plan.steps)
