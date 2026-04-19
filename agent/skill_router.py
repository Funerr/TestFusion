from __future__ import annotations

from agent.schemas.normalized_case_schema import NormalizedCase
from dsl.compiler import DSLCompiler


class SkillRouter:
    def select_skills(self, case: NormalizedCase) -> list[str]:
        compiler = DSLCompiler()
        dsl_case = compiler.compile(case)
        skills = ["规则.用例编译"]
        if any("首页" in item for item in case.expected):
            skills.append("规则.首页冒烟")
        for action in dsl_case.actions:
            if action.skill_hint:
                skills.append(action.skill_hint)
        if case.ambiguities:
            skills.append("规则.失败诊断")
        return list(dict.fromkeys(skills))
