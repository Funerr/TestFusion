from __future__ import annotations

import base64
import subprocess
from pathlib import Path
from typing import Any

from core.device.device_state import DeviceState, UIElement
from core.device.system_catalog import (
    SYSTEM_PAGE_ALIASES,
    SYSTEM_TOGGLE_SPECS,
    SYSTEM_VALUE_SPECS,
    resolve_page_key,
    resolve_toggle_key,
    resolve_value_key,
)

_TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAusB9W8oS3gAAAAASUVORK5CYII="
)


class DeviceManager:
    def __init__(
        self,
        backend: str = "simulation",
        serial: str | None = None,
        package: str | None = None,
        home_activity: str | None = None,
        artifact_root: str | Path = "artifacts",
    ) -> None:
        self.backend = backend
        self.serial = serial or "auto"
        self.package = package
        self.home_activity = home_activity
        self.artifact_root = Path(artifact_root)
        self.device_state = DeviceState(serial=self.serial, backend=backend)
        self._last_adb_error = ""
        self.release()
        if not self.is_simulation_backend() and self.serial in {"", "auto"}:
            self._auto_select_single_device()

    def is_simulation_backend(self) -> bool:
        return self.backend in {"simulation", "mock", "local"}

    def discover_devices(self) -> list[dict[str, str]]:
        adb_devices = self._adb_devices()
        if adb_devices:
            return adb_devices
        if self.is_simulation_backend():
            return [{"serial": self.serial, "backend": self.backend, "platform": "android", "state": "simulation"}]
        return []

    def reserve(self) -> dict[str, str]:
        self.device_state.occupied = True
        return {"serial": self.serial, "status": "reserved"}

    def release(self) -> dict[str, str]:
        self.device_state.occupied = False
        return {"serial": self.serial, "status": "released"}

    def prepare(self) -> dict[str, str]:
        self.reserve()
        if self.is_simulation_backend() and self.device_state.current_screen == "stopped":
            self.reset_to_home()
        return {"serial": self.serial, "backend": self.backend, "status": "ready"}

    def check_health(self) -> dict[str, Any]:
        adb_devices = self._adb_devices()
        connection = self._connection_snapshot(adb_devices)
        return {
            "serial": self.serial,
            "backend": self.backend,
            "occupied": self.device_state.occupied,
            "current_activity": self.device_state.current_activity,
            "crashed": self.device_state.crashed,
            "connected": connection["connected"],
            "connection_state": connection["connection_state"],
            "message": connection["message"],
            "adb_devices": adb_devices,
        }

    def reset_to_home(self) -> None:
        self.device_state.package = self.package
        self.device_state.current_activity = self.home_activity
        self.device_state.current_screen = "home"
        self.device_state.backgrounded = False
        self.device_state.crashed = False
        self.device_state.screen_locked = False
        self.device_state.screen_on = True
        self.device_state.elements = self._build_home_elements()
        self._log("app positioned at home screen")

    def launch_app(self) -> dict[str, Any]:
        self.reset_to_home()
        return {"status": "passed", "package": self.package, "activity": self.home_activity}

    def stop_app(self) -> dict[str, Any]:
        self.device_state.package = None
        self.device_state.current_activity = None
        self.device_state.current_screen = "stopped"
        self.device_state.elements = {}
        self._log("app stopped")
        return {"status": "passed", "package": self.package}

    def background_and_resume(self) -> dict[str, Any]:
        self.device_state.backgrounded = True
        self._log("app sent to background")
        self.device_state.backgrounded = False
        if self.device_state.crashed:
            self.reset_to_home()
            return {"status": "passed", "activity": self.home_activity, "recovered": True}
        self._log("app resumed from background")
        return {"status": "passed", "activity": self.device_state.current_activity, "recovered": False}

    def open_quick_settings(self) -> dict[str, Any]:
        return self.open_control_center()

    def open_control_center(self) -> dict[str, Any]:
        self._set_screen("control_center")
        self._log("control center opened")
        return {"status": "passed", "screen": self.device_state.current_screen}

    def open_notification_center(self) -> dict[str, Any]:
        self._set_screen("notification_center")
        self._log("notification center opened")
        return {"status": "passed", "screen": self.device_state.current_screen}

    def open_system_settings(self) -> dict[str, Any]:
        self._set_screen("settings_home")
        self._log("system settings opened")
        return {"status": "passed", "screen": self.device_state.current_screen}

    def open_system_page(self, page: str) -> dict[str, Any]:
        page_key = resolve_page_key(page) or page
        self._set_screen(f"settings_{page_key}")
        self._log(f"system page opened: {page_key}")
        return {"status": "passed", "screen": self.device_state.current_screen, "page": page_key}

    def show_permission_dialog(self, permission_name: str) -> dict[str, Any]:
        self.device_state.permission_dialog_visible = True
        self.device_state.permission_dialog_name = permission_name
        self._set_overlay_elements()
        self._log(f"permission dialog shown: {permission_name}")
        return {"status": "passed", "permission": permission_name}

    def handle_permission_dialog(self, decision: str) -> dict[str, Any]:
        normalized = decision.strip().lower()
        if normalized in {"allow", "allow_once", "allow_while_using"}:
            grant = "granted"
        elif normalized in {"deny", "reject"}:
            grant = "denied"
        else:
            grant = normalized
        if self.device_state.permission_dialog_name:
            permission_key = self._permission_key(self.device_state.permission_dialog_name)
            self.device_state.permission_grants[permission_key] = grant
        self.device_state.permission_dialog_visible = False
        self.device_state.permission_dialog_name = ""
        self._set_overlay_elements()
        self._log(f"permission decision: {normalized}")
        return {"status": "passed", "decision": normalized}

    def toggle_system_setting(self, setting: str, enabled: bool | None = None) -> dict[str, Any]:
        key = resolve_toggle_key(setting) or setting
        spec = SYSTEM_TOGGLE_SPECS[key]
        current = bool(getattr(self.device_state, spec.field))
        target = (not current) if enabled is None else bool(enabled)
        setattr(self.device_state, spec.field, target)
        if key == "airplane_mode" and target:
            self.device_state.mobile_data_enabled = False
            self.device_state.hotspot_enabled = False
        if key == "hotspot" and target:
            self.device_state.wlan_enabled = False
        self._rebuild_elements_for_screen()
        self._log(f"{key} -> {target}")
        return {"status": "passed", "setting": key, "value": target}

    def set_system_value(self, setting: str, value: int) -> dict[str, Any]:
        key = resolve_value_key(setting) or setting
        spec = SYSTEM_VALUE_SPECS[key]
        clamped = max(spec.min_value, min(spec.max_value, int(value)))
        setattr(self.device_state, spec.field, clamped)
        self._rebuild_elements_for_screen()
        self._log(f"{key} -> {clamped}")
        return {"status": "passed", "setting": key, "value": clamped}

    def get_system_state_value(self, setting: str) -> Any:
        toggle_key = resolve_toggle_key(setting)
        if toggle_key:
            return getattr(self.device_state, SYSTEM_TOGGLE_SPECS[toggle_key].field)
        value_key = resolve_value_key(setting)
        if value_key:
            return getattr(self.device_state, SYSTEM_VALUE_SPECS[value_key].field)
        if setting == "permission_dialog_visible":
            return self.device_state.permission_dialog_visible
        if setting.startswith("permissions."):
            permission_key = setting.split(".", 1)[1]
            return self.device_state.permission_grants.get(permission_key)
        raise KeyError(f"unsupported system state: {setting}")

    def lock_screen(self) -> dict[str, Any]:
        self.device_state.screen_locked = True
        self.device_state.screen_on = False
        self._set_screen("locked")
        self._log("screen locked")
        return {"status": "passed"}

    def wake_screen(self) -> dict[str, Any]:
        self.device_state.screen_on = True
        self.device_state.screen_locked = False
        self.reset_to_home()
        self._log("screen woke up")
        return {"status": "passed"}

    def input_text(self, locator: dict[str, str], text: str) -> dict[str, Any]:
        element = self._find_element(locator)
        element.text = text
        self.device_state.inputs[element.resource_id] = text
        self._log(f"input {element.resource_id}={text}")
        return {"status": "passed", "locator": locator, "text": text}

    def click(self, locator: dict[str, str]) -> dict[str, Any]:
        element = self._find_element(locator)
        resource_id = element.resource_id
        if resource_id == "search_box":
            self.device_state.elements["search_box"].text = self.device_state.elements["search_box"].text or "搜索"
            self._log("search box focused")
        elif resource_id == "back_button":
            self._set_screen("home")
        elif resource_id.startswith("qs_"):
            setting = resource_id.removeprefix("qs_")
            self.toggle_system_setting(setting)
        elif resource_id.startswith("settings_entry_"):
            self.open_system_page(resource_id.removeprefix("settings_entry_"))
        elif resource_id.startswith("settings_toggle_"):
            setting = resource_id.removeprefix("settings_toggle_")
            self.toggle_system_setting(setting)
        elif resource_id.startswith("permission_"):
            decision = resource_id.removeprefix("permission_")
            self.handle_permission_dialog(decision)
        return {"status": "passed", "locator": locator, "screen": self.device_state.current_screen}

    def swipe(self, direction: str = "up", distance: float = 0.5) -> dict[str, Any]:
        self._log(f"swipe direction={direction} distance={distance}")
        return {"status": "passed", "direction": direction, "distance": distance}

    def back(self) -> dict[str, Any]:
        self._set_screen("home")
        self._log("back pressed")
        return {"status": "passed", "activity": self.device_state.current_activity}

    def wait(self, seconds: float) -> dict[str, Any]:
        self._log(f"wait {seconds}s")
        return {"status": "passed", "seconds": seconds}

    def get_page_source(self) -> str:
        elements = self._current_elements()
        body = "".join(
            f'<node resource-id="{item.resource_id}" text="{item.text}" content-desc="{item.attrs.get("content_desc", "")}" />'
            for item in elements.values()
        )
        return f"<hierarchy activity=\"{self.device_state.current_activity}\">{body}</hierarchy>"

    def get_current_activity(self) -> str:
        return self.device_state.current_activity or ""

    def get_current_app(self) -> str:
        return self.device_state.package or ""

    def element_exists(self, locator: dict[str, str]) -> bool:
        try:
            self._find_element(locator)
            return True
        except KeyError:
            return False

    def get_element_text(self, locator: dict[str, str]) -> str:
        return self._find_element(locator).text

    def get_element_attrs(self, locator: dict[str, str]) -> dict[str, Any]:
        element = self._find_element(locator)
        return {"resource_id": element.resource_id, "text": element.text, **element.attrs}

    def take_screenshot(self, output_path: str | Path) -> str:
        target = Path(output_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(_TINY_PNG)
        self._log(f"screenshot {target.name}")
        return str(target)

    def get_logcat(self) -> str:
        return "\n".join(self.device_state.logs)

    def get_device_state(self) -> dict[str, Any]:
        return self.device_state.model_dump()

    def shell(self, command: str) -> str:
        if "dumpsys activity activities" in command or "mCurrentFocus" in command:
            return self.device_state.current_activity or ""
        if command.startswith("logcat"):
            return self.get_logcat()
        if command.startswith("settings get "):
            parts = command.split()
            if len(parts) >= 4:
                _, _, namespace, key = parts[:4]
                return self._simulate_settings_get(namespace, key)
        return f"simulation-shell:{command}"

    def install(self, apk_path: str) -> dict[str, str]:
        self._log(f"install {apk_path}")
        return {"status": "passed", "apk": apk_path}

    def uninstall(self, package: str) -> dict[str, str]:
        self._log(f"uninstall {package}")
        return {"status": "passed", "package": package}

    def pull(self, remote: str, local: str) -> dict[str, str]:
        self._log(f"pull {remote} -> {local}")
        return {"status": "passed", "remote": remote, "local": local}

    def push(self, local: str, remote: str) -> dict[str, str]:
        self._log(f"push {local} -> {remote}")
        return {"status": "passed", "local": local, "remote": remote}

    def screencap(self, output_path: str | Path) -> str:
        return self.take_screenshot(output_path)

    def _build_home_elements(self) -> dict[str, UIElement]:
        return {
            "home_tab": UIElement(resource_id="home_tab", text="首页"),
            "search_box": UIElement(resource_id="search_box", text=""),
            "welcome_banner": UIElement(resource_id="welcome_banner", text="欢迎回来"),
        }

    def _build_control_center_elements(self) -> dict[str, UIElement]:
        elements: dict[str, UIElement] = {}
        for key, spec in SYSTEM_TOGGLE_SPECS.items():
            selected = bool(getattr(self.device_state, spec.field))
            elements[f"qs_{key}"] = UIElement(
                resource_id=f"qs_{key}",
                text=spec.label,
                attrs={"state_text": "已开" if selected else "已关", "selected": selected},
            )
        elements["back_button"] = UIElement(resource_id="back_button", text="返回")
        return elements

    def _build_notification_center_elements(self) -> dict[str, UIElement]:
        return {
            "notification_item": UIElement(resource_id="notification_item", text="系统通知"),
            "clear_notification": UIElement(resource_id="clear_notification", text="清除"),
            "back_button": UIElement(resource_id="back_button", text="返回"),
        }

    def _build_settings_home_elements(self) -> dict[str, UIElement]:
        return {
            f"settings_entry_{key}": UIElement(resource_id=f"settings_entry_{key}", text=aliases[0])
            for key, aliases in SYSTEM_PAGE_ALIASES.items()
            if key != "settings"
        } | {"back_button": UIElement(resource_id="back_button", text="返回")}

    def _build_settings_page_elements(self, page_key: str) -> dict[str, UIElement]:
        elements: dict[str, UIElement] = {
            "page_title": UIElement(resource_id="page_title", text=page_key),
            "back_button": UIElement(resource_id="back_button", text="返回"),
        }
        toggle_key = resolve_toggle_key(page_key)
        if toggle_key:
            spec = SYSTEM_TOGGLE_SPECS[toggle_key]
            selected = bool(getattr(self.device_state, spec.field))
            elements[f"settings_toggle_{toggle_key}"] = UIElement(
                resource_id=f"settings_toggle_{toggle_key}",
                text=spec.label,
                attrs={"selected": selected},
            )
        value_key = resolve_value_key(page_key)
        if value_key:
            spec = SYSTEM_VALUE_SPECS[value_key]
            elements[f"settings_value_{value_key}"] = UIElement(
                resource_id=f"settings_value_{value_key}",
                text=spec.label,
                attrs={"value": getattr(self.device_state, spec.field)},
            )
        if page_key == "display":
            elements["settings_toggle_dark_mode"] = UIElement(
                resource_id="settings_toggle_dark_mode",
                text="深色模式",
                attrs={"selected": self.device_state.dark_mode_enabled},
            )
            elements["settings_toggle_auto_rotate"] = UIElement(
                resource_id="settings_toggle_auto_rotate",
                text="自动旋转",
                attrs={"selected": self.device_state.auto_rotate_enabled},
            )
            elements["settings_value_brightness"] = UIElement(
                resource_id="settings_value_brightness",
                text="亮度",
                attrs={"value": self.device_state.brightness_percent},
            )
        if page_key == "sound":
            elements["settings_value_media_volume"] = UIElement(
                resource_id="settings_value_media_volume",
                text="媒体音量",
                attrs={"value": self.device_state.media_volume_percent},
            )
            elements["settings_value_ring_volume"] = UIElement(
                resource_id="settings_value_ring_volume",
                text="铃声音量",
                attrs={"value": self.device_state.ring_volume_percent},
            )
        return elements

    def _build_permission_dialog_elements(self) -> dict[str, UIElement]:
        if not self.device_state.permission_dialog_visible:
            return {}
        return {
            "permission_title": UIElement(resource_id="permission_title", text=self.device_state.permission_dialog_name or "权限请求"),
            "permission_allow": UIElement(resource_id="permission_allow", text="允许"),
            "permission_allow_once": UIElement(resource_id="permission_allow_once", text="仅本次允许"),
            "permission_allow_while_using": UIElement(resource_id="permission_allow_while_using", text="使用时允许"),
            "permission_deny": UIElement(resource_id="permission_deny", text="不允许"),
        }

    def _set_screen(self, screen: str) -> None:
        if screen == "home":
            self.device_state.current_activity = self.home_activity
            self.device_state.current_screen = "home"
            self.device_state.package = self.package
            self.device_state.elements = self._build_home_elements()
        elif screen == "control_center":
            self.device_state.current_activity = "com.huawei.android.launcher/.controlcenter"
            self.device_state.current_screen = "control_center"
            self.device_state.package = "com.android.systemui"
            self.device_state.elements = self._build_control_center_elements()
        elif screen == "notification_center":
            self.device_state.current_activity = "com.android.systemui/.NotificationCenter"
            self.device_state.current_screen = "notification_center"
            self.device_state.package = "com.android.systemui"
            self.device_state.elements = self._build_notification_center_elements()
        elif screen == "settings_home":
            self.device_state.current_activity = "com.android.settings/.Settings"
            self.device_state.current_screen = "settings_home"
            self.device_state.package = "com.android.settings"
            self.device_state.elements = self._build_settings_home_elements()
        elif screen.startswith("settings_"):
            page_key = screen.removeprefix("settings_")
            self.device_state.current_activity = f"com.android.settings/.{page_key.title()}Settings"
            self.device_state.current_screen = screen
            self.device_state.package = "com.android.settings"
            self.device_state.elements = self._build_settings_page_elements(page_key)
        elif screen == "locked":
            self.device_state.current_activity = "system/locked"
            self.device_state.current_screen = "locked"
            self.device_state.package = "com.android.systemui"
            self.device_state.elements = {}
        self._set_overlay_elements()
        self._log(f"screen -> {screen}")

    def _rebuild_elements_for_screen(self) -> None:
        current = self.device_state.current_screen
        if current == "control_center":
            self.device_state.elements = self._build_control_center_elements()
        elif current == "notification_center":
            self.device_state.elements = self._build_notification_center_elements()
        elif current == "settings_home":
            self.device_state.elements = self._build_settings_home_elements()
        elif current.startswith("settings_"):
            self.device_state.elements = self._build_settings_page_elements(current.removeprefix("settings_"))
        elif current == "home":
            self.device_state.elements = self._build_home_elements()
        self._set_overlay_elements()

    def _set_overlay_elements(self) -> None:
        for key in list(self.device_state.elements):
            if key.startswith("permission_"):
                self.device_state.elements.pop(key, None)
        self.device_state.elements.update(self._build_permission_dialog_elements())

    def _current_elements(self) -> dict[str, UIElement]:
        return self.device_state.elements

    def _find_element(self, locator: dict[str, str]) -> UIElement:
        by = locator.get("by")
        value = locator.get("value")
        if by == "id" and value in self.device_state.elements:
            return self.device_state.elements[value]
        if by == "text":
            for element in self.device_state.elements.values():
                if element.text == value:
                    return element
        raise KeyError(f"element not found: {locator}")

    def _simulate_settings_get(self, namespace: str, key: str) -> str:
        for spec in SYSTEM_TOGGLE_SPECS.values():
            if spec.namespace == namespace and spec.settings_key == key:
                value = bool(getattr(self.device_state, spec.field))
                if spec.key == "location":
                    return "3" if value else "0"
                if spec.key == "dark_mode":
                    return "2" if value else "1"
                return "1" if value else "0"
        for spec in SYSTEM_VALUE_SPECS.values():
            if spec.namespace == namespace and spec.settings_key == key:
                return str(getattr(self.device_state, spec.field))
        return ""

    def _permission_key(self, raw_name: str) -> str:
        lowered = raw_name.lower()
        if "位置" in raw_name or "location" in lowered:
            return "location"
        if "通知" in raw_name or "notification" in lowered:
            return "notifications"
        if "相机" in raw_name or "camera" in lowered:
            return "camera"
        return lowered or "generic"

    def _log(self, message: str) -> None:
        self.device_state.logs.append(message)

    def _auto_select_single_device(self) -> None:
        devices = self._adb_devices()
        if len(devices) == 1:
            self.serial = devices[0]["serial"]
            self.device_state.serial = self.serial

    def _read_adb_devices_output(self) -> str:
        result = subprocess.run(["adb", "devices", "-l"], capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "adb devices failed")
        return result.stdout

    def _adb_devices(self) -> list[dict[str, str]]:
        try:
            devices = self._parse_adb_devices(self._read_adb_devices_output())
            self._last_adb_error = ""
            return devices
        except Exception as exc:
            self._last_adb_error = str(exc)
            return []

    def _parse_adb_devices(self, output: str) -> list[dict[str, str]]:
        devices: list[dict[str, str]] = []
        for raw_line in output.splitlines()[1:]:
            line = raw_line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            serial, state = parts[0], parts[1]
            payload = {
                "serial": serial,
                "state": state,
                "backend": "adb",
                "platform": "android",
            }
            for token in parts[2:]:
                if ":" not in token:
                    continue
                key, value = token.split(":", 1)
                payload[key] = value
            devices.append(payload)
        return devices

    def _connection_snapshot(self, adb_devices: list[dict[str, str]]) -> dict[str, Any]:
        if self.is_simulation_backend():
            return {
                "connected": True,
                "connection_state": "simulation",
                "message": "simulation backend active",
            }

        target = next((item for item in adb_devices if item["serial"] == self.serial), None)
        if target is None:
            if self._last_adb_error:
                return {
                    "connected": False,
                    "connection_state": "adb_error",
                    "message": f"adb 查询失败: {self._last_adb_error}",
                }
            if adb_devices:
                states = ", ".join(f'{item["serial"]}:{item["state"]}' for item in adb_devices)
                return {
                    "connected": False,
                    "connection_state": "not_selected",
                    "message": f"未找到目标设备 {self.serial}，当前 adb 设备: {states}",
                }
            return {
                "connected": False,
                "connection_state": "not_found",
                "message": "adb 未发现可用设备",
            }
        state = target["state"]
        if state == "device":
            return {
                "connected": True,
                "connection_state": "device",
                "message": f"设备 {self.serial} 已连接",
            }
        if state == "unauthorized":
            return {
                "connected": False,
                "connection_state": "unauthorized",
                "message": f"设备 {self.serial} 未授权，请在手机上允许 USB 调试授权",
            }
        if state == "offline":
            return {
                "connected": False,
                "connection_state": "offline",
                "message": f"设备 {self.serial} 当前离线，请重新连接 adb",
            }
        return {
            "connected": False,
            "connection_state": state,
            "message": f"设备 {self.serial} 当前状态为 {state}",
        }
