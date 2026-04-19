from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class RawCase(BaseModel):
    case_id: str
    raw_text: str
    source: str = "text"
    metadata: dict[str, Any] = Field(default_factory=dict)
