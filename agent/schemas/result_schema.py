from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from agent.schemas.normalized_case_schema import NormalizedCase
from agent.schemas.plan_schema import ExecutionPlan
from agent.schemas.step_schema import StepResultModel


class ExecutabilityScoreModel(BaseModel):
    action_clarity: float
    expectation_clarity: float
    observability: float
    assertability: float
    overall_score: float
    recommended_mode: str
    reasons: list[str] = Field(default_factory=list)


class AssertionResultModel(BaseModel):
    assertion_type: str
    level: str
    description: str
    expected: Any = None
    actual: Any = None
    passed: bool = False
    evidence: dict[str, Any] = Field(default_factory=dict)


class ArtifactBundle(BaseModel):
    screenshots: list[str] = Field(default_factory=list)
    page_sources: list[str] = Field(default_factory=list)
    logs: list[str] = Field(default_factory=list)
    videos: list[str] = Field(default_factory=list)
    result_json: str | None = None
    ai_report: str | None = None
    review_report: str | None = None
    allure_result: str | None = None
    evidence_bundle: str | None = None


class FailureAnalysisModel(BaseModel):
    failed_step: str | None = None
    failed_assertion: str | None = None
    probable_cause: str
    evidence_summary: str
    suggestion: str


class CaseResult(BaseModel):
    case_id: str
    raw_case: str
    normalized_case: NormalizedCase
    ambiguities: list[str] = Field(default_factory=list)
    executability_score: ExecutabilityScoreModel
    execution_mode: str
    final_status: str
    step_results: list[StepResultModel] = Field(default_factory=list)
    assertion_results: list[AssertionResultModel] = Field(default_factory=list)
    review_reasons: list[str] = Field(default_factory=list)
    artifacts: ArtifactBundle = Field(default_factory=ArtifactBundle)
    summary: str = ""
    plan: ExecutionPlan | None = None
    checkpoints: list[dict[str, Any]] = Field(default_factory=list)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    failure_analysis: FailureAnalysisModel | None = None
