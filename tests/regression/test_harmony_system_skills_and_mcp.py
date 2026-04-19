from __future__ import annotations

from agent.schemas.normalized_case_schema import NormalizedCase
from core.executor.runner import Runner


def test_harmony_system_actions_expand_to_chinese_skills_and_system_mcp(tmp_path):
    runner = Runner(artifact_root=tmp_path / "artifacts", backend="simulation")
    case = NormalizedCase(
        case_id="hm_system_001",
        title="鸿蒙系统开关与显示能力",
        preconditions=["手机已解锁"],
        steps=["打开WLAN", "打开定位", "允许位置权限", "调节亮度到80%", "打开深色模式"],
        expected=["WLAN已开启", "定位已开启", "位置权限已允许", "亮度为80%", "深色模式已开启"],
        ambiguities=[],
    )

    result = runner.run_normalized_case(case)

    assert result.plan is not None
    assert {
        "技能.打开WLAN",
        "技能.打开定位",
        "技能.处理权限弹窗",
        "技能.调整亮度",
        "技能.深色模式",
    }.issubset(set(result.plan.selected_skills))
    assert [step.action for step in result.plan.steps] == [
        "mobile_toggle_system_setting",
        "mobile_toggle_system_setting",
        "mobile_handle_permission_dialog",
        "mobile_set_system_value",
        "mobile_toggle_system_setting",
    ]


def test_harmony_system_mcp_toggles_and_asserts_common_states(tmp_path):
    runner = Runner(artifact_root=tmp_path / "artifacts", backend="simulation")

    runner.server.call_tool("mobile_toggle_system_setting", setting="wlan", enabled=True)
    runner.server.call_tool("mobile_toggle_system_setting", setting="location", enabled=True)
    runner.server.call_tool("mobile_toggle_system_setting", setting="nfc", enabled=True)

    wlan_state = runner.server.call_tool("mobile_get_system_state", setting="wlan")
    location_state = runner.server.call_tool("mobile_get_system_state", setting="location")
    nfc_state = runner.server.call_tool("mobile_get_system_state", setting="nfc")
    wlan_assert = runner.server.call_tool("mobile_assert_system_state", setting="wlan", expected=True)

    assert wlan_state["value"] is True
    assert location_state["value"] is True
    assert nfc_state["value"] is True
    assert wlan_assert["passed"] is True


def test_harmony_system_mcp_opens_panels_and_pages(tmp_path):
    runner = Runner(artifact_root=tmp_path / "artifacts", backend="simulation")

    control_center = runner.server.call_tool("mobile_open_control_center")
    notification_center = runner.server.call_tool("mobile_open_notification_center")
    settings_page = runner.server.call_tool("mobile_open_system_page", page="display")

    assert control_center["success"] is True
    assert notification_center["success"] is True
    assert settings_page["page"] == "display"
    assert runner.device_manager.device_state.current_screen == "settings_display"


def test_harmony_permission_brightness_and_volume_tools(tmp_path):
    runner = Runner(artifact_root=tmp_path / "artifacts", backend="simulation")
    runner.device_manager.show_permission_dialog("位置信息")

    permission = runner.server.call_tool("mobile_handle_permission_dialog", decision="allow_once")
    brightness = runner.server.call_tool("mobile_set_system_value", setting="brightness", value=80)
    media_volume = runner.server.call_tool("mobile_set_system_value", setting="media_volume", value=35)
    permission_assert = runner.server.call_tool("mobile_assert_permission_dialog", expected_visible=False)
    brightness_state = runner.server.call_tool("mobile_get_system_state", setting="brightness")
    volume_state = runner.server.call_tool("mobile_get_system_state", setting="media_volume")

    assert permission["decision"] == "allow_once"
    assert brightness["value"] == 80
    assert media_volume["value"] == 35
    assert permission_assert["passed"] is True
    assert brightness_state["value"] == 80
    assert volume_state["value"] == 35
