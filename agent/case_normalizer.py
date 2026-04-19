from __future__ import annotations

from agent.ambiguity_detector import AmbiguityDetector
from agent.schemas.normalized_case_schema import NormalizedCase
from core.device.system_catalog import SYSTEM_TOGGLE_SPECS, SYSTEM_VALUE_SPECS
from agent.schemas.raw_case_schema import RawCase


class CaseNormalizer:
    def __init__(self) -> None:
        self.detector = AmbiguityDetector()

    def normalize(self, raw_case: RawCase) -> NormalizedCase:
        text = raw_case.raw_text
        _, ambiguities = self.detector.detect(text)
        system_case = self._normalize_system_case(raw_case.case_id, text, ambiguities)
        if system_case is not None:
            return system_case
        if "蓝牙" in text:
            return NormalizedCase(
                case_id=raw_case.case_id,
                title="打开蓝牙后检查开关状态",
                preconditions=["手机已解锁"],
                steps=["打开蓝牙"],
                expected=["蓝牙已开启"],
                ambiguities=ambiguities,
            )
        if "首页" in text or "smoke" in text.lower():
            return NormalizedCase(
                case_id=raw_case.case_id,
                title="启动应用后验证首页可达且关键元素存在",
                preconditions=["应用已安装"],
                steps=["启动应用"],
                expected=["进入首页", "首页关键元素存在", "无异常弹窗"],
                ambiguities=ambiguities,
            )
        if "启动应用" in text and "首页" in text:
            return NormalizedCase(
                case_id=raw_case.case_id,
                title="启动应用并验证首页可达",
                preconditions=["应用已安装"],
                steps=["启动应用"],
                expected=["进入首页", "当前activity正确"],
                ambiguities=ambiguities,
            )
        if "后台" in text:
            return NormalizedCase(
                case_id=raw_case.case_id,
                title="应用切后台再恢复后保持可用",
                preconditions=["应用已安装"],
                steps=["启动应用", "切后台再回来"],
                expected=["恢复后当前activity正确", "无崩溃或异常弹窗"],
                ambiguities=ambiguities,
            )
        if "搜索" in text:
            return NormalizedCase(
                case_id=raw_case.case_id,
                title="进入首页后验证搜索入口可用",
                preconditions=["应用已安装"],
                steps=["启动应用", "点击搜索框"],
                expected=["搜索框可交互", "无异常弹窗"],
                ambiguities=ambiguities,
            )
        return NormalizedCase(
            case_id=raw_case.case_id,
            title="启动应用并采集首页状态",
            preconditions=["应用已安装"],
            steps=["启动应用"],
            expected=["进入首页", "可获取页面状态"],
            ambiguities=ambiguities,
        )

    def _normalize_system_case(self, case_id: str, text: str, ambiguities: list[str]) -> NormalizedCase | None:
        fragments = [item.strip() for item in text.replace("，", ",").replace("；", ",").split(",") if item.strip()]
        system_steps = [item for item in fragments if any(token in item for token in ["WLAN", "Wi-Fi", "wifi", "蓝牙", "定位", "权限", "亮度", "音量", "NFC", "热点", "飞行模式", "深色模式", "自动旋转", "通知中心", "控制中心", "设置"])]
        if not system_steps:
            return None

        expected: list[str] = []
        for step in system_steps:
            if "亮度" in step:
                digits = "".join(ch if ch.isdigit() else " " for ch in step).split()
                if digits:
                    expected.append(f"亮度为{digits[0]}%")
                continue
            if "音量" in step:
                digits = "".join(ch if ch.isdigit() else " " for ch in step).split()
                if digits:
                    expected.append(f"媒体音量为{digits[0]}%")
                continue
            if "权限" in step and any(token in step for token in ["允许", "仅本次允许", "使用时允许"]):
                if "位置" in step:
                    expected.append("位置权限已允许")
                elif "通知" in step:
                    expected.append("通知权限已允许")
                continue
            for spec in SYSTEM_TOGGLE_SPECS.values():
                if any(alias.lower() in step.lower() for alias in spec.aliases):
                    if any(token in step for token in ["打开", "开启", "启用"]):
                        expected.append(f"{spec.label}已开启")
                    elif any(token in step for token in ["关闭", "禁用"]):
                        expected.append(f"{spec.label}已关闭")
                    break
        return NormalizedCase(
            case_id=case_id,
            title=text,
            preconditions=["手机已解锁"],
            steps=system_steps,
            expected=expected,
            ambiguities=ambiguities,
        )
