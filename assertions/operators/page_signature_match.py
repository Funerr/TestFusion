from __future__ import annotations

from agent.schemas.result_schema import AssertionResultModel


def evaluate(spec, services, context) -> AssertionResultModel:
    contract = spec.contract
    assert contract is not None
    observe = services["observe_executor"]
    must_have = all(observe.execute("element_exists", {"locator": locator.model_dump()})["exists"] for locator in contract.must_have)
    one_of = True if not contract.one_of else any(
        observe.execute("element_exists", {"locator": locator.model_dump()})["exists"] for locator in contract.one_of
    )
    must_not_have = all(not observe.execute("element_exists", {"locator": locator.model_dump()})["exists"] for locator in contract.must_not_have)
    passed = must_have and one_of and must_not_have
    return AssertionResultModel(
        assertion_type="page_signature_match",
        level=spec.level,
        description=spec.description,
        expected=contract.model_dump(),
        actual={"must_have": must_have, "one_of": one_of, "must_not_have": must_not_have},
        passed=passed,
        evidence={"contract": contract.model_dump()},
    )
