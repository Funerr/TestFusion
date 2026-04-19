from __future__ import annotations

from agent.schemas.result_schema import AssertionResultModel
from assertions.dsl.matchers import equals


def evaluate(spec, services, context) -> AssertionResultModel:
    actual = services["observe_executor"].execute("get_current_activity", {})["activity"]
    return AssertionResultModel(
        assertion_type="activity_is",
        level=spec.level,
        description=spec.description,
        expected=spec.expected,
        actual=actual,
        passed=equals(actual, spec.expected),
        evidence={"activity": actual},
    )
