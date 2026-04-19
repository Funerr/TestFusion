from __future__ import annotations

from pathlib import Path


LEGACY_SINGLE_TOOL_FILES = {
    "mcp_server/tools_action/back_tool.py",
    "mcp_server/tools_action/click_tool.py",
    "mcp_server/tools_action/input_tool.py",
    "mcp_server/tools_action/launch_app_tool.py",
    "mcp_server/tools_action/stop_app_tool.py",
    "mcp_server/tools_action/swipe_tool.py",
    "mcp_server/tools_action/wait_tool.py",
    "mcp_server/tools_observe/element_exists_tool.py",
    "mcp_server/tools_observe/get_current_activity_tool.py",
    "mcp_server/tools_observe/get_device_state_tool.py",
    "mcp_server/tools_observe/get_element_attrs_tool.py",
    "mcp_server/tools_observe/get_element_text_tool.py",
    "mcp_server/tools_observe/get_logcat_tool.py",
    "mcp_server/tools_observe/get_page_source_tool.py",
    "mcp_server/tools_observe/take_screenshot_tool.py",
    "mcp_server/tools_assert/page_contract_assert_tool.py",
    "mcp_server/tools_assert/run_assertions_tool.py",
    "mcp_server/tools_assert/state_assert_tool.py",
    "mcp_server/tools_assert/text_assert_tool.py",
    "mcp_server/tools_artifact/bundle_evidence_tool.py",
    "mcp_server/tools_artifact/collect_artifacts_tool.py",
    "mcp_server/tools_artifact/export_report_tool.py",
    "mcp_server/tools_artifact/screenrecord_tool.py",
}


def test_legacy_single_tool_modules_are_removed():
    root = Path.cwd()
    leftovers = sorted(str(root / item) for item in LEGACY_SINGLE_TOOL_FILES if (root / item).exists())
    assert not leftovers, f"legacy single-tool modules should be removed: {leftovers}"


def test_four_layer_tool_directories_remain():
    root = Path.cwd()
    for path in [
        root / "mcp_server/tools_action",
        root / "mcp_server/tools_observe",
        root / "mcp_server/tools_assert",
        root / "mcp_server/tools_artifact",
    ]:
        assert path.exists()
        assert path.is_dir()
