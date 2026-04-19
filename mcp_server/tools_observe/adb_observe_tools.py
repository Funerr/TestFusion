from __future__ import annotations

from pathlib import Path

from core.device.adb_client import ADBClient


def register(registry, services):
    adb = ADBClient(services["device_manager"])

    registry.register(
        "mobile_adb_dumpsys",
        "observe",
        "执行 adb shell dumpsys <service> 并返回输出。",
        lambda service: {"status": "passed", "service": service, "stdout": adb.dumpsys(service)},
        input_schema={
            "type": "object",
            "properties": {"service": {"type": "string"}},
            "required": ["service"],
        },
    )
    registry.register(
        "mobile_adb_logcat",
        "observe",
        "抓取 adb logcat 输出。",
        lambda lines=200: {"status": "passed", "lines": lines, "stdout": adb.logcat(lines=lines)},
        input_schema={
            "type": "object",
            "properties": {"lines": {"type": "integer"}},
            "required": [],
        },
    )
    registry.register(
        "mobile_adb_screencap",
        "observe",
        "通过 adb screencap 直接截图到本地路径。",
        lambda path: {"status": "passed", "path": adb.screencap(Path(path))},
        input_schema={
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
        },
    )
