from __future__ import annotations

from agent.schemas.assertion_spec_schema import LocatorSpec, PageContractModel


class BasePage:
    name = "base"
    activity = ""
    must_have: list[LocatorSpec] = []
    must_not_have: list[LocatorSpec] = []

    @classmethod
    def contract(cls) -> PageContractModel:
        return PageContractModel(must_have=cls.must_have, must_not_have=cls.must_not_have)
