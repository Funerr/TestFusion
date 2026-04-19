from __future__ import annotations

from agent.schemas.result_schema import AssertionResultModel


def evaluate(spec, services, context) -> AssertionResultModel:
    exists = services["observe_executor"].execute("element_exists", {"locator": spec.locator.model_dump()})["exists"]
    return AssertionResultModel(
        assertion_type="element_exists",
        level=spec.level,
        description=spec.description,
        expected=True,
        actual=exists,
        passed=bool(exists),
        evidence={"locator": spec.locator.model_dump()},
    )
