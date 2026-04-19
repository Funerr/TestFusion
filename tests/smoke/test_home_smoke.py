from __future__ import annotations


def test_home_structured_case_passes(runner):
    result = runner.run_case_file("testcases/parsed_cases/smoke_cases.json", case_index=0)

    assert result.final_status == "PASS"
    assert result.execution_mode == "auto"
    assert result.review_reasons == []
    assert any(item.operator == "activity_is" for item in result.plan.assertions)
