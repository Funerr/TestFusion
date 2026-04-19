from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

AssertionLevel = Literal["strong", "weak", "observational"]


class LocatorSpec(BaseModel):
    by: str
    value: str


class PageContractModel(BaseModel):
    must_have: list[LocatorSpec] = Field(default_factory=list)
    one_of: list[LocatorSpec] = Field(default_factory=list)
    must_not_have: list[LocatorSpec] = Field(default_factory=list)


class AssertionSpecModel(BaseModel):
    operator: str
    level: AssertionLevel = "strong"
    description: str
    locator: LocatorSpec | None = None
    expected: Any = None
    timeout: float = 3.0
    contract: PageContractModel | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
