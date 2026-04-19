from __future__ import annotations

from agent.assertion_builder import AssertionBuilder
from agent.schemas.normalized_case_schema import NormalizedCase
from agent.schemas.plan_schema import ExecutionPlan
from agent.skill_router import SkillRouter
from dsl.compiler import DSLCompiler
from skills.action_registry import CursorActionRegistry


class Planner:
    def __init__(self, package: str | None = None, home_activity: str | None = None) -> None:
        self.router = SkillRouter()
        self.assertion_builder = AssertionBuilder()
        self.compiler = DSLCompiler()
        self.registry = CursorActionRegistry()
        self.package = package
        self.home_activity = home_activity

    def build_plan(self, case: NormalizedCase, execution_mode: str, checkpoints: list[dict[str, object]]) -> ExecutionPlan:
        dsl_case = self.compiler.compile(case)
        expansion = self.registry.build_steps(
            dsl_case,
            package=self.package,
            home_activity=self.home_activity,
        )
        selected_skills = list(dict.fromkeys([*self.router.select_skills(case), *expansion.selected_skills]))
        steps = expansion.steps
        assertions = self.assertion_builder.build(case, checkpoints, execution_mode)
        required_tools = sorted(
            {
                *[step.action for step in steps],
                "collect_artifacts",
                "get_logcat",
                "run_assertions",
            }
        )
        return ExecutionPlan(
            case_id=case.case_id,
            title=case.title,
            steps=steps,
            selected_skills=selected_skills,
            required_tools=required_tools,
            assertions=assertions,
            execution_mode=execution_mode,
            dsl_text=dsl_case.rendered_text,
            dsl_payload=dsl_case.model_dump(mode="json"),
        )
