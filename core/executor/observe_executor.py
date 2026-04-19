from __future__ import annotations

from pathlib import Path
from typing import Any

from core.device.adb_client import ADBClient
from core.device.device_manager import DeviceManager
from core.device.system_catalog import SYSTEM_TOGGLE_SPECS, SYSTEM_VALUE_SPECS, resolve_toggle_key, resolve_value_key
from core.device.u2_client import U2Client


class ObserveExecutor:
    def __init__(self, device_manager: DeviceManager) -> None:
        self.device_manager = device_manager
        self.adb = ADBClient(device_manager)
        self.u2 = U2Client(device_manager)

    def execute(self, observation: str, params: dict[str, Any]) -> dict[str, Any]:
        if observation == "get_page_source":
            return {"content": self.u2.get_page_source()}
        if observation == "get_current_activity":
            return {"activity": self.u2.get_current_activity()}
        if observation == "get_current_app":
            return {"package_name": self.u2.get_current_app()}
        if observation == "element_exists":
            return {"exists": self.u2.element_exists(params["locator"])}
        if observation == "get_element_text":
            return {"text": self.u2.get_element_text(params["locator"])}
        if observation == "get_element_attrs":
            return {"attrs": self.u2.get_element_attrs(params["locator"])}
        if observation == "take_screenshot":
            return {"path": self.adb.screencap(Path(params["path"]))}
        if observation == "get_logcat":
            return {"content": self.adb.logcat()}
        if observation == "get_device_state":
            if self.device_manager.is_simulation_backend():
                return {"state": self.device_manager.get_device_state()}
            payload = self.device_manager.get_device_state()
            for spec in SYSTEM_TOGGLE_SPECS.values():
                raw = self.adb.setting_get(spec.namespace, spec.settings_key)
                if spec.key == "location":
                    payload[spec.field] = raw not in {"", "0"}
                elif spec.key == "dark_mode":
                    payload[spec.field] = raw in {"2", "yes", "on"}
                else:
                    payload[spec.field] = raw == "1"
            for spec in SYSTEM_VALUE_SPECS.values():
                raw = self.adb.setting_get(spec.namespace, spec.settings_key)
                if raw.strip().isdigit():
                    payload[spec.field] = int(raw.strip())
            return {"state": payload}
        if observation == "get_system_state":
            setting = params["setting"]
            if self.device_manager.is_simulation_backend():
                return {"setting": setting, "value": self.device_manager.get_system_state_value(setting)}
            toggle_key = resolve_toggle_key(setting)
            if toggle_key:
                spec = SYSTEM_TOGGLE_SPECS[toggle_key]
                raw = self.adb.setting_get(spec.namespace, spec.settings_key)
                if spec.key == "location":
                    value = raw not in {"", "0"}
                elif spec.key == "dark_mode":
                    value = raw == "2"
                else:
                    value = raw == "1"
                return {"setting": toggle_key, "value": value}
            value_key = resolve_value_key(setting)
            if value_key:
                spec = SYSTEM_VALUE_SPECS[value_key]
                raw = self.adb.setting_get(spec.namespace, spec.settings_key)
                return {"setting": value_key, "value": int(raw) if raw.strip().isdigit() else raw}
            raise ValueError(f"unsupported system setting: {setting}")
        raise ValueError(f"unknown observation: {observation}")
