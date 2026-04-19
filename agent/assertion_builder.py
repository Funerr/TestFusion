from __future__ import annotations

from agent.schemas.assertion_spec_schema import AssertionSpecModel, LocatorSpec, PageContractModel
from agent.schemas.normalized_case_schema import NormalizedCase


class AssertionBuilder:
    def build(self, case: NormalizedCase, checkpoints: list[dict[str, object]], execution_mode: str) -> list[AssertionSpecModel]:
        specs: list[AssertionSpecModel] = []
        for item in checkpoints:
            locator = LocatorSpec(**item["locator"]) if item.get("locator") else None
            contract = PageContractModel(**item["contract"]) if item.get("contract") else None
            level = item.get("level", "strong")
            if execution_mode != "auto" and level == "strong" and case.ambiguities and item["operator"] == "page_signature_match":
                level = "weak"
            specs.append(
                AssertionSpecModel(
                    operator=str(item["operator"]),
                    level=level,
                    description=str(item["description"]),
                    locator=locator,
                    expected=item.get("expected"),
                    contract=contract,
                    metadata=dict(item.get("metadata", {})),
                )
            )
        return specs
