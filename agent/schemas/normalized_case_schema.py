from __future__ import annotations

from pydantic import BaseModel, Field


class NormalizedCase(BaseModel):
    case_id: str
    title: str
    preconditions: list[str] = Field(default_factory=list)
    steps: list[str] = Field(default_factory=list)
    expected: list[str] = Field(default_factory=list)
    ambiguities: list[str] = Field(default_factory=list)
