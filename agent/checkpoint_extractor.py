from __future__ import annotations

from agent.schemas.normalized_case_schema import NormalizedCase
from core.device.system_catalog import SYSTEM_TOGGLE_SPECS, SYSTEM_VALUE_SPECS
from core.pages.home_page import HomePage


class CheckpointExtractor:
    def extract(self, case: NormalizedCase) -> list[dict[str, object]]:
        checkpoints: list[dict[str, object]] = []
        expected_text = " ".join(case.expected)
        if "首页" in expected_text:
            checkpoints.append({
                "description": "进入首页 activity",
                "operator": "activity_is",
                "level": "strong",
                "expected": HomePage.activity,
            })
            checkpoints.append({
                "description": "首页关键元素存在",
                "operator": "page_signature_match",
                "level": "strong",
                "contract": HomePage.contract().model_dump(),
            })
        if "无异常弹窗" in expected_text or "无崩溃" in expected_text:
            checkpoints.append({
                "description": "错误弹窗不存在",
                "operator": "element_not_exists",
                "level": "strong",
                "locator": {"by": "id", "value": "error_dialog"},
            })
        if "搜索框可交互" in expected_text:
            checkpoints.append({
                "description": "搜索框存在",
                "operator": "element_exists",
                "level": "weak",
                "locator": {"by": "id", "value": "search_box"},
            })
        if "蓝牙已开启" in expected_text:
            checkpoints.append({
                "description": "蓝牙已开启",
                "operator": "device_state_equals",
                "level": "strong",
                "expected": True,
                "metadata": {"field": "bluetooth_enabled"},
            })
        for spec in SYSTEM_TOGGLE_SPECS.values():
            if f"{spec.label}已开启" in expected_text or f"{spec.label}已打开" in expected_text:
                checkpoints.append({
                    "description": f"{spec.label}已开启",
                    "operator": "device_state_equals",
                    "level": "strong",
                    "expected": True,
                    "metadata": {"field": spec.field},
                })
            if f"{spec.label}已关闭" in expected_text:
                checkpoints.append({
                    "description": f"{spec.label}已关闭",
                    "operator": "device_state_equals",
                    "level": "strong",
                    "expected": False,
                    "metadata": {"field": spec.field},
                })
        if "位置权限已允许" in expected_text:
            checkpoints.append({
                "description": "位置权限已允许",
                "operator": "device_state_equals",
                "level": "strong",
                "expected": "granted",
                "metadata": {"field": "permission_grants.location"},
            })
        if "通知权限已允许" in expected_text:
            checkpoints.append({
                "description": "通知权限已允许",
                "operator": "device_state_equals",
                "level": "strong",
                "expected": "granted",
                "metadata": {"field": "permission_grants.notifications"},
            })
        for spec in SYSTEM_VALUE_SPECS.values():
            if spec.label in expected_text and "亮度为" in expected_text and spec.key == "brightness":
                checkpoints.append({
                    "description": "亮度达到预期值",
                    "operator": "device_state_equals",
                    "level": "strong",
                    "expected": self._extract_percent(expected_text),
                    "metadata": {"field": spec.field},
                })
            if spec.label in expected_text and "音量" in spec.label and "35%" in expected_text and spec.key == "media_volume":
                checkpoints.append({
                    "description": "媒体音量达到预期值",
                    "operator": "device_state_equals",
                    "level": "strong",
                    "expected": 35,
                    "metadata": {"field": spec.field},
                })
        if not checkpoints:
            checkpoints.append({
                "description": "可获取当前 activity",
                "operator": "activity_is",
                "level": "weak",
                "expected": HomePage.activity,
            })
        return checkpoints

    def _extract_percent(self, text: str) -> int:
        digits = "".join(ch if ch.isdigit() else " " for ch in text).split()
        if not digits:
            return 0
        return int(digits[0])
