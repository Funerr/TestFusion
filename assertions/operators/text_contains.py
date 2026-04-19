from __future__ import annotations

from agent.schemas.result_schema import AssertionResultModel
from assertions.dsl.matchers import contains


def evaluate(spec, services, context) -> AssertionResultModel:
    actual = services["observe_executor"].execute("get_element_text", {"locator": spec.locator.model_dump()})["text"]
    return AssertionResultModel(
        assertion_type="text_contains",
        level=spec.level,
        description=spec.description,
        expected=spec.expected,
        actual=actual,
        passed=contains(actual, spec.expected),
        evidence={"locator": spec.locator.model_dump()},
    )
