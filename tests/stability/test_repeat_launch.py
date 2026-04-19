from __future__ import annotations


def test_repeat_launch_is_stable(runner):
    statuses = []
    for _ in range(3):
        statuses.append(runner.run_text_case("启动应用并检查首页").final_status)

    assert statuses == ["PASS", "PASS", "PASS"]
