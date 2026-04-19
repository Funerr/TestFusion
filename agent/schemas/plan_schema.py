from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agent.schemas.assertion_spec_schema import AssertionSpecModel
from agent.schemas.step_schema import PlanStep


class ExecutionPlan(BaseModel):
    case_id: str
    title: str
    steps: list[PlanStep] = Field(default_factory=list)
    selected_skills: list[str] = Field(default_factory=list)
    required_tools: list[str] = Field(default_factory=list)
    assertions: list[AssertionSpecModel] = Field(default_factory=list)
    execution_mode: str = "auto"
    dsl_text: str = ""
    dsl_payload: dict[str, Any] = Field(default_factory=dict)
