from __future__ import annotations

AMBIGUOUS_TERMS = {
    "正常": "“正常”缺乏明确可执行定义，已降级为页面可达、关键元素存在、无异常弹窗等可观察条件",
    "没问题": "“没问题”属于口语化判断，需要人工确认是否覆盖完整风险",
    "看看": "“看看”不构成可执行断言，需要补充观察点",
    "试试": "“试试”属于探索性表达，自动执行后仍建议复核",
    "稳定": "“稳定”需要次数、时长或错误阈值，当前信息不足",
    "正确": "“正确”缺少页面合同或文本标准，需降级处理",
    "合理": "“合理”是主观判断，不能直接强断言",
    "流畅": "“流畅”需要性能指标，当前只能保留观察型结果",
    "多次": "“多次”未给出次数范围，无法强判定",
    "明显异常": "“明显异常”主观性强，只能收集辅助证据",
    "偶现": "“偶现”需要统计与重试策略支撑，当前无法一次强判定",
}


class AmbiguityDetector:
    def detect(self, text: str) -> tuple[bool, list[str]]:
        reasons = [f"发现模糊词“{term}”：{reason}" for term, reason in AMBIGUOUS_TERMS.items() if term in text]
        return bool(reasons), reasons
