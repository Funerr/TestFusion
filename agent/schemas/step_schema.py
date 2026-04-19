from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class PlanStep(BaseModel):
    step_id: str
    action: str
    description: str
    skill: str
    params: dict[str, Any] = Field(default_factory=dict)


class StepResultModel(BaseModel):
    step_id: str
    action_status: str
    observation_summary: str = ""
    assertion_status: str = "not_run"
    artifacts: list[str] = Field(default_factory=list)
