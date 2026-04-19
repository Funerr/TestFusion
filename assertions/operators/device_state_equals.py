from __future__ import annotations

from agent.schemas.result_schema import AssertionResultModel
from assertions.dsl.matchers import equals


def evaluate(spec, services, context) -> AssertionResultModel:
    state = services["observe_executor"].execute("get_device_state", {})["state"]
    field = spec.metadata.get("field", "")
    actual = state
    for token in str(field).split("."):
        if isinstance(actual, dict):
            actual = actual.get(token)
        else:
            actual = None
            break
    return AssertionResultModel(
        assertion_type="device_state_equals",
        level=spec.level,
        description=spec.description,
        expected=spec.expected,
        actual=actual,
        passed=equals(actual, spec.expected),
        evidence={"field": field, "state": state},
    )
