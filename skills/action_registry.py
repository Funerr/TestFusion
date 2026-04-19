from __future__ import annotations

from dataclasses import dataclass

from agent.schemas.plan_schema import ExecutionPlan
from agent.schemas.step_schema import PlanStep
from core.device.system_catalog import resolve_toggle_key, resolve_value_key
from dsl.models import CaseDSL, DSLAction


@dataclass
class ExpansionBundle:
    selected_skills: list[str]
    steps: list[PlanStep]


class CursorActionRegistry:
    def build_steps(
        self,
        dsl_case: CaseDSL,
        *,
        package: str | None = None,
        home_activity: str | None = None,
    ) -> ExpansionBundle:
        selected_skills: list[str] = ["规则.用例编译"]
        steps: list[PlanStep] = []
        step_counter = 1

        if any("首页" in expected for expected in dsl_case.expectations):
            selected_skills.append("规则.首页冒烟")

        for action in dsl_case.actions:
            action_skills, action_steps = self._expand_action(
                action,
                step_counter=step_counter,
                package=package,
                home_activity=home_activity,
            )
            selected_skills.extend(action_skills)
            steps.extend(action_steps)
            step_counter += len(action_steps)

        return ExpansionBundle(
            selected_skills=list(dict.fromkeys(selected_skills)),
            steps=steps,
        )

    def _expand_action(
        self,
        action: DSLAction,
        *,
        step_counter: int,
        package: str | None,
        home_activity: str | None,
    ) -> tuple[list[str], list[PlanStep]]:
        if action.name == "启动应用":
            return (
                ["规则.首页冒烟"],
                [
                    PlanStep(
                        step_id=f"step_{step_counter}",
                        action="mobile_launch_app",
                        description="启动目标应用",
                        skill="规则.首页冒烟",
                        params={"package": package, "activity": home_activity},
                    )
                ],
            )

        if action.name == "点击搜索框":
            return (
                ["技能.首页观察"],
                [
                    PlanStep(
                        step_id=f"step_{step_counter}",
                        action="mobile_click_by_id",
                        description="点击搜索框",
                        skill="技能.首页观察",
                        params={"resource_id": "search_box"},
                    )
                ],
            )

        if action.name == "切后台再恢复":
            return (
                ["技能.设备恢复", "规则.设备恢复"],
                [
                    PlanStep(
                        step_id=f"step_{step_counter}",
                        action="mobile_press_key",
                        description="按 Home 让应用进入后台",
                        skill="技能.设备恢复",
                        params={"key": "home"},
                    ),
                    PlanStep(
                        step_id=f"step_{step_counter + 1}",
                        action="mobile_launch_app",
                        description="重新拉起应用",
                        skill="技能.设备恢复",
                        params={"package": package, "activity": home_activity},
                    ),
                ],
            )

        if action.name == "打开蓝牙":
            return (
                ["技能.打开蓝牙", "规则.系统蓝牙"],
                [
                    PlanStep(
                        step_id=f"step_{step_counter}",
                        action="mobile_toggle_system_setting",
                        description="设置蓝牙为开启（优先控制中心，必要时回退设置页）",
                        skill="技能.打开蓝牙",
                        params={"setting": "bluetooth", "enabled": True, "source": "auto"},
                    ),
                ],
            )

        if action.target == "system.control_center":
            return (
                [action.skill_hint or "技能.打开控制中心", "规则.鸿蒙系统面板"],
                [
                    PlanStep(
                        step_id=f"step_{step_counter}",
                        action="mobile_open_control_center",
                        description="打开控制中心",
                        skill=action.skill_hint or "技能.打开控制中心",
                        params={},
                    )
                ],
            )

        if action.target == "system.notification_center":
            return (
                [action.skill_hint or "技能.打开通知中心", "规则.鸿蒙系统面板"],
                [
                    PlanStep(
                        step_id=f"step_{step_counter}",
                        action="mobile_open_notification_center",
                        description="打开通知中心",
                        skill=action.skill_hint or "技能.打开通知中心",
                        params={},
                    )
                ],
            )

        if action.target == "system.settings_home":
            return (
                [action.skill_hint or "技能.打开系统设置", "规则.鸿蒙系统设置"],
                [
                    PlanStep(
                        step_id=f"step_{step_counter}",
                        action="mobile_open_system_settings",
                        description="打开系统设置",
                        skill=action.skill_hint or "技能.打开系统设置",
                        params={},
                    )
                ],
            )

        if action.target and action.target.startswith("system.page."):
            page = action.target.removeprefix("system.page.")
            return (
                [action.skill_hint or "技能.打开系统设置页", "规则.鸿蒙系统设置"],
                [
                    PlanStep(
                        step_id=f"step_{step_counter}",
                        action="mobile_open_system_page",
                        description=f"打开系统设置页：{page}",
                        skill=action.skill_hint or "技能.打开系统设置页",
                        params={"page": page},
                    )
                ],
            )

        if action.target and action.target.startswith("system.toggle."):
            setting = action.target.removeprefix("system.toggle.")
            enabled = action.value == "on"
            return (
                [action.skill_hint or "规则.鸿蒙系统开关", "规则.鸿蒙系统开关"],
                [
                    PlanStep(
                        step_id=f"step_{step_counter}",
                        action="mobile_toggle_system_setting",
                        description=f"设置系统开关：{setting}",
                        skill=action.skill_hint or "规则.鸿蒙系统开关",
                        params={"setting": resolve_toggle_key(setting) or setting, "enabled": enabled},
                    )
                ],
            )

        if action.target == "system.permission":
            return (
                [action.skill_hint or "技能.处理权限弹窗", "规则.鸿蒙权限弹窗"],
                [
                    PlanStep(
                        step_id=f"step_{step_counter}",
                        action="mobile_handle_permission_dialog",
                        description="处理权限弹窗",
                        skill=action.skill_hint or "技能.处理权限弹窗",
                        params={"decision": action.value or "allow"},
                    )
                ],
            )

        if action.target and action.target.startswith("system.value."):
            setting = action.target.removeprefix("system.value.")
            return (
                [action.skill_hint or "规则.鸿蒙显示声音", "规则.鸿蒙显示声音"],
                [
                    PlanStep(
                        step_id=f"step_{step_counter}",
                        action="mobile_set_system_value",
                        description=f"设置系统数值：{setting}",
                        skill=action.skill_hint or "规则.鸿蒙显示声音",
                        params={"setting": resolve_value_key(setting) or setting, "value": int(action.value or 0)},
                    )
                ],
            )

        return (
            [action.skill_hint or "规则.用例编译"],
            [
                PlanStep(
                    step_id=f"step_{step_counter}",
                    action="mobile_take_screenshot",
                    description=f"记录未识别动作：{action.name}",
                    skill=action.skill_hint or "规则.用例编译",
                    params={"description": action.name},
                )
            ],
        )
