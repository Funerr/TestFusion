from __future__ import annotations

import re

from agent.schemas.normalized_case_schema import NormalizedCase
from core.device.system_catalog import SYSTEM_TOGGLE_SPECS, resolve_page_key, resolve_toggle_key, resolve_value_key
from dsl.models import CaseDSL, DSLAction


class DSLCompiler:
    def compile(self, case: NormalizedCase) -> CaseDSL:
        actions = [self._compile_action(step) for step in case.steps]
        rendered = self._render(case, actions)
        return CaseDSL(
            case_id=case.case_id,
            title=case.title,
            preconditions=list(case.preconditions),
            actions=actions,
            expectations=list(case.expected),
            rendered_text=rendered,
        )

    def _compile_action(self, step: str) -> DSLAction:
        compact = step.strip()
        lowered = compact.lower()
        permission_action = self._permission_action(compact)
        if permission_action:
            return permission_action
        value_action = self._value_action(compact)
        if value_action:
            return value_action
        page_action = self._page_action(compact)
        if page_action:
            return page_action
        toggle_action = self._toggle_action(compact)
        if toggle_action:
            return toggle_action
        if "打开蓝牙" in compact or "开启蓝牙" in compact:
            return DSLAction(
                name="打开蓝牙",
                kind="action",
                abstract=True,
                target="system.bluetooth",
                value="on",
                skill_hint="技能.打开蓝牙",
                note="优先使用控制中心，必要时退回系统设置页。",
            )
        if "切后台" in compact:
            return DSLAction(
                name="切后台再恢复",
                kind="action",
                abstract=True,
                target="app.lifecycle",
                skill_hint="技能.设备恢复",
            )
        if "搜索" in compact and "点击" in compact:
            return DSLAction(
                name="点击搜索框",
                kind="action",
                abstract=False,
                target="search_box",
                skill_hint="技能.首页观察",
            )
        if "启动应用" in compact:
            return DSLAction(
                name="启动应用",
                kind="action",
                abstract=False,
                target="app.launch",
                skill_hint="规则.首页冒烟",
            )
        return DSLAction(name=compact, kind="action", abstract=True, skill_hint="规则.用例编译")

    def _toggle_action(self, step: str) -> DSLAction | None:
        enabled = None
        if any(token in step for token in ["打开", "开启", "打开并检查", "启用"]):
            enabled = "on"
        elif any(token in step for token in ["关闭", "禁用"]):
            enabled = "off"
        if enabled is None:
            return None
        for key, spec in SYSTEM_TOGGLE_SPECS.items():
            if any(alias.lower() in step.lower() for alias in spec.aliases):
                action_name = f"{'打开' if enabled == 'on' else '关闭'}{spec.label}"
                return DSLAction(
                    name=action_name,
                    kind="action",
                    abstract=True,
                    target=f"system.toggle.{key}",
                    value=enabled,
                    skill_hint=self._skill_for_toggle(key, enabled),
                    note=f"优先使用控制中心处理 {spec.label}。",
                )
        return None

    def _page_action(self, step: str) -> DSLAction | None:
        if "控制中心" in step:
            return DSLAction(name="打开控制中心", kind="action", abstract=False, target="system.control_center", skill_hint="技能.打开控制中心")
        if "通知中心" in step:
            return DSLAction(name="打开通知中心", kind="action", abstract=False, target="system.notification_center", skill_hint="技能.打开通知中心")
        if "系统设置" in step or step.strip() == "打开设置":
            return DSLAction(name="打开系统设置", kind="action", abstract=False, target="system.settings_home", skill_hint="技能.打开系统设置")
        if any(token in step for token in ["设置页", "设置页面", "设置"]) and "权限" not in step:
            for raw in ["wlan", "wifi", "蓝牙", "定位", "显示", "声音", "通知", "权限", "热点", "nfc", "移动网络"]:
                if raw.lower() in step.lower() or raw in step:
                    page_key = resolve_page_key(raw)
                    if page_key:
                        return DSLAction(
                            name="打开系统页面",
                            kind="action",
                            abstract=False,
                            target=f"system.page.{page_key}",
                            value=page_key,
                            skill_hint="技能.打开系统设置页",
                        )
        return None

    def _permission_action(self, step: str) -> DSLAction | None:
        decision = None
        if "仅本次允许" in step:
            decision = "allow_once"
        elif "使用时允许" in step:
            decision = "allow_while_using"
        elif "允许" in step and "权限" in step:
            decision = "allow"
        elif any(token in step for token in ["拒绝", "不允许"]) and "权限" in step:
            decision = "deny"
        if decision is None:
            return None
        return DSLAction(
            name="处理权限弹窗",
            kind="action",
            abstract=True,
            target="system.permission",
            value=decision,
            skill_hint="技能.处理权限弹窗",
        )

    def _value_action(self, step: str) -> DSLAction | None:
        match = re.search(r"(\d+)\s*%", step)
        if not match:
            return None
        percent = match.group(1)
        if "亮度" in step:
            return DSLAction(
                name="调整系统数值",
                kind="action",
                abstract=True,
                target="system.value.brightness",
                value=percent,
                skill_hint="技能.调整亮度",
            )
        if "媒体音量" in step or "音量" in step:
            return DSLAction(
                name="调整系统数值",
                kind="action",
                abstract=True,
                target="system.value.media_volume",
                value=percent,
                skill_hint="技能.调整音量",
            )
        return None

    def _skill_for_toggle(self, key: str, enabled: str) -> str:
        skill_map = {
            "wlan": "技能.打开WLAN" if enabled == "on" else "技能.关闭WLAN",
            "bluetooth": "技能.打开蓝牙" if enabled == "on" else "技能.关闭蓝牙",
            "location": "技能.打开定位" if enabled == "on" else "技能.关闭定位",
            "mobile_data": "技能.打开移动数据" if enabled == "on" else "技能.关闭移动数据",
            "airplane_mode": "技能.打开飞行模式" if enabled == "on" else "技能.关闭飞行模式",
            "nfc": "技能.打开NFC" if enabled == "on" else "技能.关闭NFC",
            "hotspot": "技能.打开个人热点" if enabled == "on" else "技能.关闭个人热点",
            "dark_mode": "技能.深色模式",
            "auto_rotate": "技能.自动旋转",
        }
        return skill_map.get(key, "规则.鸿蒙系统开关")

    def _render(self, case: NormalizedCase, actions: list[DSLAction]) -> str:
        lines = [f"用例: {case.title}", "前置条件:"]
        if case.preconditions:
            lines.extend(f"- {item}" for item in case.preconditions)
        else:
            lines.append("- 无")
        lines.append("操作步骤:")
        for action in actions:
            abstract_suffix = " [abstract]" if action.abstract else ""
            skill_suffix = f" -> {action.skill_hint}" if action.skill_hint else ""
            lines.append(f"- ACTION {action.name}{abstract_suffix}{skill_suffix}")
        lines.append("预期结果:")
        if case.expected:
            lines.extend(f"- {item}" for item in case.expected)
        else:
            lines.append("- 无")
        return "\n".join(lines)
