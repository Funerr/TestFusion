from __future__ import annotations

from core.device.adb_client import ADBClient


def register(registry, services):
    adb = ADBClient(services["device_manager"])

    registry.register(
        "mobile_adb_shell",
        "action",
        "执行 adb shell 命令并返回 stdout。",
        lambda command: {"status": "passed", "command": command, "stdout": adb.shell(command)},
        input_schema={
            "type": "object",
            "properties": {"command": {"type": "string"}},
            "required": ["command"],
        },
    )
    registry.register(
        "mobile_adb_install",
        "action",
        "通过 adb 安装 APK。",
        lambda apk_path: adb.install(apk_path),
        input_schema={
            "type": "object",
            "properties": {"apk_path": {"type": "string"}},
            "required": ["apk_path"],
        },
    )
    registry.register(
        "mobile_adb_uninstall",
        "action",
        "通过 adb 卸载应用。",
        lambda package: adb.uninstall(package),
        input_schema={
            "type": "object",
            "properties": {"package": {"type": "string"}},
            "required": ["package"],
        },
    )
    registry.register(
        "mobile_adb_push",
        "action",
        "通过 adb push 发送文件到设备。",
        lambda local, remote: adb.push(local, remote),
        input_schema={
            "type": "object",
            "properties": {
                "local": {"type": "string"},
                "remote": {"type": "string"},
            },
            "required": ["local", "remote"],
        },
    )
