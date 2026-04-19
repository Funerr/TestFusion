from __future__ import annotations

from typing import Any

from core.device.adb_client import ADBClient
from core.device.device_manager import DeviceManager
from core.device.u2_client import U2Client


class ActionExecutor:
    def __init__(self, device_manager: DeviceManager) -> None:
        self.device_manager = device_manager
        self.adb = ADBClient(device_manager)
        self.u2 = U2Client(device_manager)

    def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            if action == "click":
                return self.u2.click(params["locator"])
            if action == "swipe":
                return self.u2.swipe(params.get("direction", "up"), params.get("distance", 0.5))
            if action == "input_text":
                return self.u2.input_text(params["locator"], params["text"])
            if action == "open_quick_settings":
                return self.u2.open_quick_settings()
            if action == "open_notification_center":
                return self.u2.open_notification_center()
            if action == "back":
                return self.device_manager.back()
            if action == "launch_app":
                return self.adb.start_app(params.get("package", self.device_manager.package), params.get("activity"))
            if action == "stop_app":
                return self.adb.stop_app(params.get("package", self.device_manager.package))
            if action == "wait":
                return self.device_manager.wait(float(params.get("seconds", 0.2)))
        except Exception as exc:  # pragma: no cover - exercised in failure paths
            return {"status": "failed", "error": str(exc), "action": action}
        return {"status": "failed", "error": f"unknown action: {action}"}
