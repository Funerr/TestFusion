from __future__ import annotations

from agent.schemas.result_schema import CaseResult, FailureAnalysisModel


class FailureAnalyzer:
    def analyze(self, result: CaseResult) -> FailureAnalysisModel:
        failed_assertion = next((item for item in result.assertion_results if not item.passed), None)
        failed_step = next((item for item in result.step_results if item.action_status != "passed"), None)
        probable_cause = "页面状态与断言不一致"
        suggestion = "检查动作是否执行到位，并结合截图与页面源复核定位。"
        if result.final_status == "NEEDS_REVIEW":
            probable_cause = "用例存在模糊描述或仅满足弱断言"
            suggestion = "结合 DSL、AI 报告和证据包进行人工复核。"
        return FailureAnalysisModel(
            failed_step=failed_step.step_id if failed_step else None,
            failed_assertion=failed_assertion.description if failed_assertion else None,
            probable_cause=probable_cause,
            evidence_summary=result.summary,
            suggestion=suggestion,
        )
