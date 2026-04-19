from __future__ import annotations

from typing import Any

from agent.schemas.result_schema import AssertionResultModel
from assertions.operators import activity_is, device_state_equals, element_exists, element_not_exists, page_signature_match, text_contains, text_equals, wait_until_disappear, wait_until_exists


class AssertionEngine:
    def __init__(self, observe_executor) -> None:
        self.observe_executor = observe_executor
        self._operators = {
            "activity_is": activity_is.evaluate,
            "device_state_equals": device_state_equals.evaluate,
            "element_exists": element_exists.evaluate,
            "element_not_exists": element_not_exists.evaluate,
            "text_equals": text_equals.evaluate,
            "text_contains": text_contains.evaluate,
            "wait_until_exists": wait_until_exists.evaluate,
            "wait_until_disappear": wait_until_disappear.evaluate,
            "page_signature_match": page_signature_match.evaluate,
        }

    def evaluate_one(self, spec, context: dict[str, Any]) -> AssertionResultModel:
        operator = self._operators[spec.operator]
        return operator(spec, {"observe_executor": self.observe_executor}, context)

    def run(self, specs, context: dict[str, Any]) -> tuple[list[AssertionResultModel], str, list[str]]:
        results = [self.evaluate_one(spec, context) for spec in specs]
        strong_results = [result for result in results if result.level == "strong"]
        if any(not result.passed for result in strong_results):
            review_reasons = [f"强断言失败: {result.description}" for result in strong_results if not result.passed]
            return results, "FAIL", review_reasons

        review_reasons: list[str] = []
        if context.get("execution_mode") != "auto":
            review_reasons.append("执行模式不是 auto，保留人工复核")
        ambiguities = context.get("ambiguities", [])
        review_reasons.extend(ambiguities)
        if any(result.level != "strong" for result in results):
            review_reasons.append("包含弱断言或观察型结果，自动裁判降级")

        if review_reasons:
            return results, "NEEDS_REVIEW", review_reasons
        return results, "PASS", []
