from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


DSLActionKind = Literal["precondition", "action", "expectation"]


class DSLAction(BaseModel):
    name: str
    kind: DSLActionKind
    abstract: bool = False
    target: str | None = None
    value: str | None = None
    skill_hint: str | None = None
    note: str | None = None


class CaseDSL(BaseModel):
    case_id: str
    title: str
    preconditions: list[str] = Field(default_factory=list)
    actions: list[DSLAction] = Field(default_factory=list)
    expectations: list[str] = Field(default_factory=list)
    rendered_text: str = ""
