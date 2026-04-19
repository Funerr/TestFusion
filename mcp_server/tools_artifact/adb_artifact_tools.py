from __future__ import annotations

from core.device.adb_client import ADBClient


def register(registry, services):
    adb = ADBClient(services["device_manager"])

    registry.register(
        "mobile_adb_pull",
        "artifact",
        "通过 adb pull 拉取设备文件到本地。",
        lambda remote, local: adb.pull(remote, local),
        input_schema={
            "type": "object",
            "properties": {
                "remote": {"type": "string"},
                "local": {"type": "string"},
            },
            "required": ["remote", "local"],
        },
    )
