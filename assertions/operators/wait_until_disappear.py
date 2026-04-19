from __future__ import annotations

from agent.schemas.result_schema import AssertionResultModel
from core.utils.waiters import wait_until


def evaluate(spec, services, context) -> AssertionResultModel:
    result = wait_until(
        lambda: not services["observe_executor"].execute("element_exists", {"locator": spec.locator.model_dump()})["exists"],
        timeout=spec.timeout,
    )
    return AssertionResultModel(
        assertion_type="wait_until_disappear",
        level=spec.level,
        description=spec.description,
        expected=True,
        actual=bool(result),
        passed=bool(result),
        evidence={"timeout": spec.timeout, "locator": spec.locator.model_dump()},
    )
