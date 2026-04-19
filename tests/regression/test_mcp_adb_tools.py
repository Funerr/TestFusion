from __future__ import annotations

from core.device.device_manager import DeviceManager
from core.executor.runner import Runner


EXPECTED_VISIBLE_ADB_TOOLS = {
    "mobile_adb_shell",
    "mobile_adb_dumpsys",
    "mobile_adb_install",
    "mobile_adb_uninstall",
    "mobile_adb_push",
    "mobile_adb_pull",
    "mobile_adb_screencap",
    "mobile_adb_logcat",
}


def test_registry_exposes_adb_mcp_tools():
    runner = Runner()
    names = {item["name"] for item in runner.server.registry.list_tools()}
    missing = EXPECTED_VISIBLE_ADB_TOOLS - names
    assert not missing, f"missing adb MCP tools: {sorted(missing)}"


def test_adb_tools_work_in_mock_backend():
    runner = Runner(backend="simulation")
    shell_result = runner.server.call_tool("mobile_adb_shell", command="echo test")
    dumpsys_result = runner.server.call_tool("mobile_adb_dumpsys", service="activity")
    pull_result = runner.server.call_tool("mobile_adb_pull", remote="/sdcard/foo.txt", local="artifacts/logs/foo.txt")

    assert shell_result["command"] == "echo test"
    assert shell_result["stdout"] == "simulation-shell:echo test"
    assert dumpsys_result["service"] == "activity"
    assert "simulation-shell:dumpsys activity" in dumpsys_result["stdout"]
    assert pull_result["status"] == "passed"


def test_device_connection_reports_unauthorized_state(monkeypatch):
    manager = DeviceManager(backend="adb", serial="HC10006129200186")
    monkeypatch.setattr(
        manager,
        "_read_adb_devices_output",
        lambda: "List of devices attached\nHC10006129200186\tunauthorized usb:1-1 transport_id:3\n",
    )

    devices = manager.discover_devices()
    health = manager.check_health()

    assert devices[0]["state"] == "unauthorized"
    assert health["connected"] is False
    assert health["connection_state"] == "unauthorized"
    assert "USB 调试授权" in health["message"]
