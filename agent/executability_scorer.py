from __future__ import annotations

from agent.schemas.normalized_case_schema import NormalizedCase
from agent.schemas.result_schema import ExecutabilityScoreModel


class ExecutabilityScorer:
    def score(self, case: NormalizedCase) -> ExecutabilityScoreModel:
        step_factor = min(1.0, 0.6 + 0.1 * len(case.steps))
        expected_factor = min(1.0, 0.55 + 0.15 * len(case.expected))
        expectation_text = "".join(case.expected)
        structured_keywords = ["activity", "元素", "弹窗", "标题", "蓝牙", "设备状态", "开关"]
        observability = 0.9 if any(keyword in expectation_text for keyword in structured_keywords) else 0.65
        ambiguity_penalty = min(0.35, 0.08 * len(case.ambiguities))
        action_clarity = round(max(0.2, step_factor - ambiguity_penalty / 2), 2)
        expectation_clarity = round(max(0.2, expected_factor - ambiguity_penalty), 2)
        assertability = round(max(0.2, (action_clarity + expectation_clarity + observability) / 3 - ambiguity_penalty / 2), 2)
        overall = round((action_clarity + expectation_clarity + observability + assertability) / 4, 2)
        if not case.ambiguities and any(keyword in expectation_text for keyword in structured_keywords):
            mode = "auto"
        elif not case.ambiguities and overall >= 0.8:
            mode = "auto"
        elif overall >= 0.55:
            mode = "semi_auto"
        else:
            mode = "manual_review"
        reasons = []
        if case.ambiguities:
            reasons.append("存在模糊描述，已降低自动执行等级")
        if overall < 0.8:
            reasons.append("观测和断言信息不够完整")
        return ExecutabilityScoreModel(
            action_clarity=action_clarity,
            expectation_clarity=expectation_clarity,
            observability=round(observability, 2),
            assertability=assertability,
            overall_score=overall,
            recommended_mode=mode,
            reasons=reasons,
        )
