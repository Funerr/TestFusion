from __future__ import annotations

from pathlib import Path

from core.executor.runner import Runner


ADB_SINGLE_DEVICE = "List of devices attached\nHC10006129200186\tdevice usb:1-1 transport_id:3\n"


def test_runner_auto_selects_single_connected_device_and_has_no_demo_defaults(
    monkeypatch,
    tmp_path: Path,
):
    monkeypatch.setattr(
        "core.device.device_manager.DeviceManager._read_adb_devices_output",
        lambda self: ADB_SINGLE_DEVICE,
    )

    runner = Runner(artifact_root=tmp_path / "artifacts")

    assert runner.device_manager.serial == "HC10006129200186"
    assert runner.device_manager.package is None
    assert runner.device_manager.home_activity is None


def test_mobile_list_apps_reads_from_adb_packages(monkeypatch, tmp_path: Path):
    monkeypatch.setattr(
        "core.device.device_manager.DeviceManager._read_adb_devices_output",
        lambda self: ADB_SINGLE_DEVICE,
    )
    runner = Runner(artifact_root=tmp_path / "artifacts")
    monkeypatch.setattr(
        runner.action_executor.adb,
        "list_packages",
        lambda: [
            "com.android.settings",
            "com.example.alpha",
            "com.huawei.android.launcher",
        ],
        raising=False,
    )

    payload = runner.server.call_tool("mobile_list_apps", filter="settings")

    assert payload["count"] == 1
    assert payload["apps"] == [
        {
            "package_name": "com.android.settings",
            "label": "settings",
        }
    ]


def test_runtime_and_docs_do_not_ship_mock_or_demo_defaults():
    checked_files = [
        Path("core/device/device_manager.py"),
        Path("core/device/device_state.py"),
        Path("core/device/adb_client.py"),
        Path("core/device/u2_client.py"),
        Path("core/executor/runner.py"),
        Path("mcp_server/mobile_toolkit.py"),
        Path("agent/planner.py"),
        Path("core/pages/home_page.py"),
        Path("agent/report_writer.py"),
        Path("configs/framework.yaml"),
        Path(".env.example"),
        Path("README.md"),
        Path("docs/project_guide.md"),
    ]
    forbidden_tokens = {
        "mock-video",
        "com.demo.app",
        "com.demo.MainActivity",
        "emulator-5554",
        "FRAMEWORK_DEVICE_BACKEND",
        'backend: mock',
        'backend = "mock"',
        'backend == "mock"',
    }

    offenders: list[str] = []
    for file_path in checked_files:
        content = file_path.read_text(encoding="utf-8")
        for token in forbidden_tokens:
            if token in content:
                offenders.append(f"{file_path}:{token}")

    assert not offenders, f"real-device-only mode still leaks mock/demo defaults: {offenders}"
