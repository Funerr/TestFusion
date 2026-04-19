from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from core.device.adb_client import ADBClient
from core.device.device_manager import DeviceManager
from core.executor.runner import Runner
from agent.schemas.step_schema import PlanStep


REAL_UI_XML = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
<hierarchy rotation="0">
  <node index="0" text="" resource-id="com.android.systemui:id/status_bar_container" class="android.widget.FrameLayout" package="com.android.systemui" clickable="false" bounds="[0,0][1080,110]" />
  <node index="0" text="" resource-id="" class="android.widget.FrameLayout" package="com.real.app" clickable="false" bounds="[0,0][1080,2400]">
    <node index="0" text="设置" resource-id="com.real.app:id/settings_entry" class="android.widget.TextView" package="com.real.app" clickable="true" bounds="[10,20][260,120]" content-desc="" />
    <node index="1" text="" resource-id="com.real.app:id/avatar" class="android.widget.ImageView" package="com.real.app" clickable="true" bounds="[20,160][180,320]" content-desc="头像" />
  </node>
</hierarchy>
"""


def test_prepare_does_not_fake_home_state_for_real_backend():
    manager = DeviceManager(backend="adb", serial="HC10006129200186")

    manager.prepare()

    assert manager.device_state.current_screen == "stopped"
    assert manager.device_state.current_activity is None
    assert manager.device_state.elements == {}


def test_mobile_list_elements_uses_real_page_source_for_adb_backend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    runner = Runner(artifact_root=tmp_path / "artifacts", backend="adb")
    runner.device_manager.device_state.elements = runner.device_manager._build_home_elements()

    def fake_execute(observation: str, params: dict):
        if observation == "get_page_source":
            return {"content": REAL_UI_XML}
        if observation == "get_current_activity":
            return {"activity": "com.real.app/.SettingsActivity"}
        if observation == "get_current_app":
            return {"package_name": "com.real.app"}
        raise AssertionError(f"unexpected observation: {observation}")

    monkeypatch.setattr(runner.observe_executor, "execute", fake_execute)

    payload = runner.server.call_tool("mobile_list_elements")

    assert payload["activity"] == "com.real.app/.SettingsActivity"
    assert payload["count"] == 2
    assert [item["resource_id"] for item in payload["elements"]] == [
        "com.real.app:id/settings_entry",
        "com.real.app:id/avatar",
    ]
    assert [item["text"] for item in payload["elements"]] == ["设置", ""]
    assert payload["elements"][1]["hint"] == "头像"


def test_mobile_get_current_app_uses_observed_foreground_app(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    runner = Runner(artifact_root=tmp_path / "artifacts", backend="adb")
    runner.device_manager.device_state.package = "com.fake.cached"
    runner.device_manager.device_state.current_activity = "com.fake.CachedActivity"

    def fake_execute(observation: str, params: dict):
        if observation == "get_current_activity":
            return {"activity": "com.real.app/.HomeActivity"}
        if observation == "get_current_app":
            return {"package_name": "com.real.app"}
        raise AssertionError(f"unexpected observation: {observation}")

    monkeypatch.setattr(runner.observe_executor, "execute", fake_execute)

    payload = runner.server.call_tool("mobile_get_current_app")

    assert payload["package_name"] == "com.real.app"
    assert payload["activity"] == "com.real.app/.HomeActivity"


def test_mobile_close_popup_uses_real_ui_tree_for_adb_backend(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    runner = Runner(artifact_root=tmp_path / "artifacts", backend="adb")

    popup_xml = """<?xml version='1.0' encoding='UTF-8' standalone='yes' ?>
    <hierarchy rotation="0">
      <node index="0" text="" resource-id="" class="android.widget.FrameLayout" package="com.real.app" clickable="false" bounds="[0,0][1080,2400]">
        <node index="0" text="关闭" resource-id="com.real.app:id/close" class="android.widget.ImageView" package="com.real.app" clickable="true" bounds="[920,40][1040,160]" content-desc="" />
      </node>
    </hierarchy>
    """

    def fake_execute(observation: str, params: dict):
        if observation == "get_page_source":
            return {"content": popup_xml}
        if observation == "get_current_activity":
            return {"activity": "com.real.app/.DialogActivity"}
        if observation == "get_current_app":
            return {"package_name": "com.real.app"}
        raise AssertionError(f"unexpected observation: {observation}")

    clicked: list[tuple[str, dict]] = []

    monkeypatch.setattr(runner.observe_executor, "execute", fake_execute)
    monkeypatch.setattr(
        runner.action_executor,
        "execute",
        lambda action, params: clicked.append((action, params)) or {"status": "passed", "locator": params["locator"]},
    )

    payload = runner.server.call_tool("mobile_close_popup")

    assert payload["closed"] is True
    assert clicked == [("click", {"locator": {"by": "id", "value": "com.real.app:id/close"}})]


def test_adb_start_app_raises_when_am_start_reports_missing_activity(monkeypatch: pytest.MonkeyPatch):
    manager = DeviceManager(backend="adb", serial="HC10006129200186")
    client = ADBClient(manager)

    monkeypatch.setattr(
        "core.device.adb_client.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout="Starting: Intent { cmp=com.demo.app/com.demo.MainActivity }\nError type 3\n",
            stderr="Error: Activity class {com.demo.app/com.demo.MainActivity} does not exist.\n",
        ),
    )

    with pytest.raises(RuntimeError, match="does not exist"):
        client.start_app("com.demo.app", "com.demo.MainActivity")


def test_adb_start_app_raises_when_am_start_reports_error_in_stderr(monkeypatch: pytest.MonkeyPatch):
    manager = DeviceManager(backend="adb", serial="HC10006129200186")
    client = ADBClient(manager)

    monkeypatch.setattr(
        "core.device.adb_client.subprocess.run",
        lambda *args, **kwargs: SimpleNamespace(
            returncode=0,
            stdout="",
            stderr="Error type 3\nError: Activity class {com.demo.app/com.demo.MainActivity} does not exist.\n",
        ),
    )

    with pytest.raises(RuntimeError, match="does not exist"):
        client.start_app("com.demo.app", "com.demo.MainActivity")


def test_launch_step_summary_reports_launch_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    runner = Runner(artifact_root=tmp_path / "artifacts", backend="adb")
    step = PlanStep(
        step_id="step_1",
        action="mobile_launch_app",
        description="启动应用",
        skill="runtime.launch_app",
        params={"package": "com.demo.app", "activity": "com.demo.MainActivity"},
    )

    def fake_call_tool(name: str, **kwargs):
        if name == "mobile_launch_app":
            return {"status": "failed", "error": "Activity class does not exist"}
        if name == "mobile_wait":
            raise AssertionError("wait should not run after launch failure")
        raise AssertionError(f"unexpected tool call: {name}")

    monkeypatch.setattr(runner.server, "call_tool", fake_call_tool)

    outcome = runner.flow_executor._launch_app(step, {})

    assert outcome["status"] == "failed"
    assert "does not exist" in outcome["summary"]
