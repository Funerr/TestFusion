from __future__ import annotations

from typing import Any

from core.device.device_manager import DeviceManager

try:  # pragma: no cover - exercised only with real devices
    import uiautomator2 as u2
except Exception:  # pragma: no cover - optional dependency at runtime
    u2 = None


class U2Client:
    def __init__(self, manager: DeviceManager) -> None:
        self.manager = manager
        self._device = None

    def _connect(self) -> Any:
        if self.manager.is_simulation_backend():
            return None
        if u2 is None:
            raise RuntimeError("uiautomator2 is not available")
        if self._device is None:
            self._device = u2.connect(self.manager.serial)
        return self._device

    def click(self, locator: dict[str, str]) -> dict[str, Any]:
        if self.manager.is_simulation_backend():
            return self.manager.click(locator)
        device = self._connect()
        device(**self._selector(locator)).click()
        return {"status": "passed", "locator": locator}

    def swipe(self, direction: str = "up", distance: float = 0.5) -> dict[str, Any]:
        if self.manager.is_simulation_backend():
            return self.manager.swipe(direction, distance)
        device = self._connect()
        if direction == "up":
            device.swipe_ext("up", scale=distance)
        elif direction == "down":
            device.swipe_ext("down", scale=distance)
        return {"status": "passed", "direction": direction, "distance": distance}

    def input_text(self, locator: dict[str, str], text: str) -> dict[str, Any]:
        if self.manager.is_simulation_backend():
            return self.manager.input_text(locator, text)
        device = self._connect()
        device(**self._selector(locator)).set_text(text)
        return {"status": "passed", "locator": locator, "text": text}

    def element_exists(self, locator: dict[str, str]) -> bool:
        if self.manager.is_simulation_backend():
            return self.manager.element_exists(locator)
        device = self._connect()
        return bool(device(**self._selector(locator)).exists)

    def get_element_attrs(self, locator: dict[str, str]) -> dict[str, Any]:
        if self.manager.is_simulation_backend():
            return self.manager.get_element_attrs(locator)
        device = self._connect()
        info = device(**self._selector(locator)).info
        return dict(info)

    def get_element_text(self, locator: dict[str, str]) -> str:
        if self.manager.is_simulation_backend():
            return self.manager.get_element_text(locator)
        device = self._connect()
        return str(device(**self._selector(locator)).get_text())

    def get_page_source(self) -> str:
        if self.manager.is_simulation_backend():
            return self.manager.get_page_source()
        device = self._connect()
        return str(device.dump_hierarchy())

    def get_current_activity(self) -> str:
        if self.manager.is_simulation_backend():
            return self.manager.get_current_activity()
        device = self._connect()
        return str(device.app_current().get("activity", ""))

    def get_current_app(self) -> str:
        if self.manager.is_simulation_backend():
            return self.manager.get_current_app()
        device = self._connect()
        return str(device.app_current().get("package", ""))

    def open_quick_settings(self) -> dict[str, Any]:
        if self.manager.is_simulation_backend():
            return self.manager.open_quick_settings()
        device = self._connect()
        if hasattr(device, "open_quick_settings"):
            device.open_quick_settings()
        elif hasattr(device, "open_notification"):
            device.open_notification()
        return {"status": "passed"}

    def open_notification_center(self) -> dict[str, Any]:
        if self.manager.is_simulation_backend():
            return self.manager.open_notification_center()
        device = self._connect()
        if hasattr(device, "open_notification"):
            device.open_notification()
        return {"status": "passed"}

    def _selector(self, locator: dict[str, str]) -> dict[str, str]:
        by = locator.get("by")
        value = locator.get("value")
        if by == "id":
            return {"resourceId": value}
        if by == "text":
            return {"text": value}
        if by == "xpath":
            return {"xpath": value}
        raise ValueError(f"unsupported locator: {locator}")
