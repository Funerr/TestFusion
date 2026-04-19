from __future__ import annotations

from agent.schemas.assertion_spec_schema import LocatorSpec


class Locator(LocatorSpec):
    def as_dict(self) -> dict[str, str]:
        return {"by": self.by, "value": self.value}
