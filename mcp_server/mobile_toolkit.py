from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from uuid import uuid4
import xml.etree.ElementTree as ET

from agent.schemas.assertion_spec_schema import AssertionSpecModel, LocatorSpec, PageContractModel
from core.device.system_catalog import (
    SYSTEM_PAGE_INTENTS,
    SYSTEM_TOGGLE_SPECS,
    SYSTEM_VALUE_SPECS,
    resolve_page_key,
    resolve_toggle_key,
    resolve_value_key,
)
from core.utils.json_util import write_json


class MobileToolKit:
    def __init__(self, services: dict[str, Any]) -> None:
        self.services = services
        self.operation_history: list[dict[str, Any]] = []
        self.som_elements: list[dict[str, Any]] = []
        self.clipboard_text = ""
        self.toast_watch_enabled = False
        self.last_toast = ""
        self.screen_record_active = False
        self.screen_record_path: str | None = None
        self.templates_dir = self.report_writer.root / "templates"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

    @property
    def action_executor(self):
        return self.services["action_executor"]

    @property
    def observe_executor(self):
        return self.services["observe_executor"]

    @property
    def assertion_engine(self):
        return self.services["assertion_engine"]

    @property
    def device_manager(self):
        return self.services["device_manager"]

    @property
    def report_writer(self):
        return self.services["report_writer"]

    def list_elements(self) -> dict[str, Any]:
        elements = self._element_rows()
        return {
            "success": True,
            "platform": "android",
            "activity": self._current_activity(),
            "elements": elements,
            "count": len(elements),
        }

    def find_nearby(self, text: str, direction: str = "right") -> dict[str, Any]:
        elements = self._element_rows()
        anchor_index = next((index for index, item in enumerate(elements) if item["text"] == text), None)
        if anchor_index is None:
            return {"success": False, "error": f"text not found: {text}", "direction": direction}
        if direction in {"right", "below"}:
            candidate_index = min(anchor_index + 1, len(elements) - 1)
        else:
            candidate_index = max(anchor_index - 1, 0)
        return {
            "success": True,
            "direction": direction,
            "anchor": elements[anchor_index],
            "nearby_element": elements[candidate_index],
        }

    def take_screenshot(
        self,
        description: str = "",
        compress: bool = True,
        crop_x: int = 0,
        crop_y: int = 0,
        crop_size: int = 0,
        case_id: str | None = None,
        path: str | None = None,
    ) -> dict[str, Any]:
        target = Path(path or self.report_writer.screenshots_dir / f"{case_id or 'adhoc'}_{uuid4().hex[:8]}.png")
        result = self.observe_executor.execute("take_screenshot", {"path": str(target)})
        payload = {
            "success": True,
            "status": "passed",
            "path": result["path"],
            "description": description,
            "compress": compress,
        }
        if crop_size:
            payload["crop"] = {"x": crop_x, "y": crop_y, "size": crop_size}
        self._record("mobile_take_screenshot", description=description, path=result["path"])
        return payload

    def screenshot_with_som(self) -> dict[str, Any]:
        screenshot = self.take_screenshot(description="screenshot_with_som")
        self.som_elements = self._element_rows()
        return {
            **screenshot,
            "elements": [{"index": index, **item} for index, item in enumerate(self.som_elements, start=1)],
        }

    def get_screen_size(self) -> dict[str, Any]:
        return {"success": True, "width": 360, "height": 800}

    def screenshot_with_grid(self, grid_size: int = 100, show_popup_hints: bool = False) -> dict[str, Any]:
        payload = self.take_screenshot(description="screenshot_with_grid")
        payload["grid_size"] = grid_size
        payload["show_popup_hints"] = show_popup_hints
        return payload

    def click_by_som(self, index: int) -> dict[str, Any]:
        if not self.som_elements:
            self.som_elements = self._element_rows()
        if index < 1 or index > len(self.som_elements):
            return {"success": False, "status": "failed", "error": f"som index out of range: {index}"}
        target = self.som_elements[index - 1]
        result = self._click_element(target)
        self._record("mobile_click_by_som", index=index)
        return {**result, "element": target}

    def click_by_text(self, text: str, position: str | None = None, verify: str | None = None) -> dict[str, Any]:
        result = self.action_executor.execute("click", {"locator": {"by": "text", "value": text}})
        payload = self._success_payload(result, text=text, position=position)
        if verify:
            payload["verify"] = self.assert_text(verify)
        self._record("mobile_click_by_text", text=text, position=position, verify=verify)
        return payload

    def click_by_id(self, resource_id: str, index: int = 0) -> dict[str, Any]:
        result = self.action_executor.execute("click", {"locator": {"by": "id", "value": resource_id}})
        self._record("mobile_click_by_id", resource_id=resource_id, index=index)
        return self._success_payload(result, resource_id=resource_id, index=index)

    def click_by_percent(self, x_percent: float, y_percent: float) -> dict[str, Any]:
        target = self._element_from_percent(x_percent, y_percent)
        if target is not None:
            result = self._click_element(target)
        else:
            self.device_manager._log(f"percent click ({x_percent},{y_percent})")
            result = {"status": "passed", "x_percent": x_percent, "y_percent": y_percent}
        self._record("mobile_click_by_percent", x_percent=x_percent, y_percent=y_percent)
        return self._success_payload(result, x_percent=x_percent, y_percent=y_percent)

    def click_at_coords(self, x: int, y: int, **_: Any) -> dict[str, Any]:
        return self.click_by_percent((x / 360.0) * 100.0, (y / 800.0) * 100.0)

    def click_by_bounds(
        self,
        x1: int | None = None,
        y1: int | None = None,
        x2: int | None = None,
        y2: int | None = None,
        bounds_str: str | None = None,
    ) -> dict[str, Any]:
        bounds = self._parse_bounds(bounds_str) if bounds_str else (x1, y1, x2, y2)
        target = self._element_from_bounds(bounds)
        if target is not None:
            result = self._click_element(target)
        else:
            self.device_manager._log(f"bounds click {bounds}")
            result = {"status": "passed", "bounds": bounds}
        self._record("mobile_click_by_bounds", bounds=bounds)
        return self._success_payload(result, bounds=bounds)

    def long_press_by_text(self, text: str, duration: float = 1.0) -> dict[str, Any]:
        result = self.action_executor.execute("click", {"locator": {"by": "text", "value": text}})
        self._record("mobile_long_press_by_text", text=text, duration=duration)
        return self._success_payload(result, text=text, duration=duration)

    def long_press_by_id(self, resource_id: str, duration: float = 1.0) -> dict[str, Any]:
        result = self.action_executor.execute("click", {"locator": {"by": "id", "value": resource_id}})
        self._record("mobile_long_press_by_id", resource_id=resource_id, duration=duration)
        return self._success_payload(result, resource_id=resource_id, duration=duration)

    def long_press_by_percent(self, x_percent: float, y_percent: float, duration: float = 1.0) -> dict[str, Any]:
        result = self.click_by_percent(x_percent, y_percent)
        result["duration"] = duration
        self._record("mobile_long_press_by_percent", x_percent=x_percent, y_percent=y_percent, duration=duration)
        return result

    def long_press_at_coords(self, x: int, y: int, duration: float = 1.0, **_: Any) -> dict[str, Any]:
        result = self.click_at_coords(x, y)
        result["duration"] = duration
        self._record("mobile_long_press_at_coords", x=x, y=y, duration=duration)
        return result

    def input_text_by_id(self, resource_id: str, text: str) -> dict[str, Any]:
        result = self.action_executor.execute(
            "input_text",
            {"locator": {"by": "id", "value": resource_id}, "text": text},
        )
        self._record("mobile_input_text_by_id", resource_id=resource_id, text=text)
        return self._success_payload(result, resource_id=resource_id, text=text)

    def input_at_coords(self, x: int, y: int, text: str) -> dict[str, Any]:
        target = self._element_from_percent((x / 360.0) * 100.0, (y / 800.0) * 100.0)
        if target is not None and target["resource_id"]:
            result = self.input_text_by_id(target["resource_id"], text)
        else:
            self.device_manager._log(f"input at coords ({x},{y}) text={text}")
            result = {"success": True, "status": "passed", "x": x, "y": y, "text": text}
        self._record("mobile_input_at_coords", x=x, y=y, text=text)
        return result

    def swipe(
        self,
        direction: str,
        y: int | None = None,
        y_percent: float | None = None,
        distance: int | None = None,
        distance_percent: float | None = None,
    ) -> dict[str, Any]:
        normalized_distance = 0.5
        if distance_percent is not None:
            normalized_distance = max(0.05, min(distance_percent / 100.0, 1.0))
        elif distance is not None:
            normalized_distance = max(0.05, min(distance / 1000.0, 1.0))
        result = self.action_executor.execute("swipe", {"direction": direction, "distance": normalized_distance})
        self._record(
            "mobile_swipe",
            direction=direction,
            y=y,
            y_percent=y_percent,
            distance=distance,
            distance_percent=distance_percent,
        )
        return self._success_payload(result, direction=direction)

    def drag_progress_bar(
        self,
        direction: str = "right",
        distance_percent: float = 30.0,
        y_percent: float | None = None,
        y: int | None = None,
    ) -> dict[str, Any]:
        self.device_manager._log(
            f"drag progress direction={direction} distance_percent={distance_percent} y_percent={y_percent} y={y}"
        )
        self._record(
            "mobile_drag_progress_bar",
            direction=direction,
            distance_percent=distance_percent,
            y_percent=y_percent,
            y=y,
        )
        return {
            "success": True,
            "status": "passed",
            "direction": direction,
            "distance_percent": distance_percent,
            "y_percent": y_percent,
            "y": y,
        }

    def press_key(self, key: str) -> dict[str, Any]:
        lowered = key.lower()
        if lowered == "back":
            result = self.device_manager.back()
        elif lowered == "home":
            self.device_manager.device_state.backgrounded = True
            self.device_manager._log("home pressed")
            result = {"status": "passed", "key": lowered}
        else:
            self.device_manager._log(f"key pressed: {lowered}")
            result = {"status": "passed", "key": lowered}
        self._record("mobile_press_key", key=lowered)
        return self._success_payload(result, key=lowered)

    def wait(self, seconds: float) -> dict[str, Any]:
        result = self.action_executor.execute("wait", {"seconds": seconds})
        self._record("mobile_wait", seconds=seconds)
        return self._success_payload(result, seconds=seconds)

    def hide_keyboard(self) -> dict[str, Any]:
        self.device_manager._log("keyboard hidden")
        self._record("mobile_hide_keyboard")
        return {"success": True, "status": "passed"}

    def open_quick_settings(self) -> dict[str, Any]:
        result = self.action_executor.execute("open_quick_settings", {})
        self._record("mobile_open_quick_settings")
        return self._success_payload(result)

    def open_control_center(self) -> dict[str, Any]:
        result = self.action_executor.execute("open_quick_settings", {})
        self._record("mobile_open_control_center")
        return self._success_payload(result)

    def open_notification_center(self) -> dict[str, Any]:
        result = self.action_executor.execute("open_notification_center", {})
        self._record("mobile_open_notification_center")
        return self._success_payload(result)

    def open_system_settings(self) -> dict[str, Any]:
        if self.device_manager.is_simulation_backend():
            result = self.device_manager.open_system_settings()
        else:
            result = self.action_executor.adb.start_intent(SYSTEM_PAGE_INTENTS["settings"])
        self._record("mobile_open_system_settings")
        return self._success_payload(result)

    def open_system_page(self, page: str) -> dict[str, Any]:
        page_key = resolve_page_key(page) or page
        if self.device_manager.is_simulation_backend():
            result = self.device_manager.open_system_page(page_key)
        else:
            result = self.action_executor.adb.start_intent(SYSTEM_PAGE_INTENTS.get(page_key, SYSTEM_PAGE_INTENTS["settings"]))
        self._record("mobile_open_system_page", page=page_key)
        return self._success_payload(result, page=page_key)

    def toggle_system_setting(self, setting: str, enabled: bool | None = None, source: str = "auto") -> dict[str, Any]:
        setting_key = resolve_toggle_key(setting) or setting
        spec = SYSTEM_TOGGLE_SPECS[setting_key]

        def _toggle_via(target_source: str) -> dict[str, Any]:
            if target_source in {"control_center", "quick_settings", "auto"}:
                self.open_control_center()
                return self.click_by_text(spec.label)
            self.open_system_page(spec.page)
            return self.click_by_text(spec.label)

        if self.device_manager.is_simulation_backend():
            if source in {"control_center", "quick_settings", "auto"}:
                self.device_manager.open_control_center()
            elif source == "settings":
                self.device_manager.open_system_page(spec.page)
            result = self.device_manager.toggle_system_setting(setting_key, enabled=enabled)
            used_source = source
        else:
            before_value = self.get_system_state(setting_key)["value"]
            if enabled is not None and before_value == bool(enabled):
                result = {"status": "passed", "setting": setting_key, "value": before_value, "noop": True}
                used_source = source
            else:
                primary_source = "control_center" if source == "auto" else source
                result = _toggle_via(primary_source)
                used_source = primary_source
                if source == "auto" and not result.get("success"):
                    result = _toggle_via("settings")
                    used_source = "settings"
                if enabled is not None:
                    after_value = self.get_system_state(setting_key)["value"]
                    if after_value != bool(enabled) and result.get("success"):
                        retry_source = "settings" if used_source in {"control_center", "quick_settings"} else "control_center"
                        retry = _toggle_via(retry_source)
                        if retry.get("success"):
                            result = retry
                            used_source = retry_source
        self._record("mobile_toggle_system_setting", setting=setting_key, enabled=enabled, source=used_source)
        payload = self.get_system_state(setting_key)
        return self._success_payload(result, setting=setting_key, value=payload["value"], source=used_source)

    def handle_permission_dialog(self, decision: str) -> dict[str, Any]:
        if self.device_manager.is_simulation_backend():
            result = self.device_manager.handle_permission_dialog(decision)
        else:
            text_map = {
                "allow": "允许",
                "allow_once": "仅本次允许",
                "allow_while_using": "使用时允许",
                "deny": "不允许",
            }
            result = self.click_by_text(text_map.get(decision, decision))
            result["decision"] = decision
        self._record("mobile_handle_permission_dialog", decision=decision)
        return self._success_payload(result, decision=decision)

    def set_system_value(self, setting: str, value: int) -> dict[str, Any]:
        setting_key = resolve_value_key(setting) or setting
        if self.device_manager.is_simulation_backend():
            result = self.device_manager.set_system_value(setting_key, value)
        else:
            spec = SYSTEM_VALUE_SPECS[setting_key]
            if setting_key == "brightness":
                scaled = int(max(0, min(255, round(int(value) * 255 / 100))))
                self.action_executor.adb.shell(f"settings put {spec.namespace} {spec.settings_key} {scaled}")
                result = {"status": "passed", "setting": setting_key, "value": int(value)}
            else:
                result = {"status": "passed", "setting": setting_key, "value": int(value)}
        self._record("mobile_set_system_value", setting=setting_key, value=value)
        return self._success_payload(result, setting=setting_key, value=int(value))

    def launch_app(self, package_name: str | None = None, package: str | None = None, activity: str | None = None) -> dict[str, Any]:
        target_package = package_name or package or self.device_manager.package
        if not target_package:
            return {"success": False, "status": "failed", "error": "missing package name"}
        result = self.action_executor.execute("launch_app", {"package": target_package, "activity": activity})
        self._record("mobile_launch_app", package_name=target_package, activity=activity)
        if result.get("status") == "passed":
            self._update_toast("应用已启动")
        return self._success_payload(result, package_name=target_package, activity=activity)

    def terminate_app(self, package_name: str | None = None, package: str | None = None) -> dict[str, Any]:
        target_package = package_name or package or self.device_manager.package
        result = self.action_executor.execute("stop_app", {"package": target_package})
        self._record("mobile_terminate_app", package_name=target_package)
        return self._success_payload(result, package_name=target_package)

    def list_apps(self, filter_text: str = "") -> dict[str, Any]:
        packages = self.action_executor.adb.list_packages()
        apps = [
            {
                "package_name": package_name,
                "label": package_name.rsplit(".", 1)[-1].lower(),
            }
            for package_name in packages
        ]
        if filter_text:
            needle = filter_text.lower()
            apps = [item for item in apps if needle in item["package_name"].lower() or needle in item["label"].lower()]
        return {"success": True, "apps": apps, "count": len(apps)}

    def list_devices(self) -> dict[str, Any]:
        devices = self.device_manager.discover_devices()
        return {"success": bool(devices), "devices": devices, "count": len(devices)}

    def check_connection(self) -> dict[str, Any]:
        device = self.device_manager.check_health()
        connected = bool(device.get("connected")) and not device.get("crashed", False)
        return {
            "success": connected,
            "connected": connected,
            "device": device,
            "message": device.get("message", ""),
        }

    def close_popup(self, popup_detected: bool | None = None, popup_bounds: list[int] | tuple[int, int, int, int] | None = None) -> dict[str, Any]:
        if not self.device_manager.is_simulation_backend():
            button = self.find_close_button()
            element = button.get("element")
            if element:
                self._click_element(element)
            self._record("mobile_close_popup", popup_detected=popup_detected, popup_bounds=popup_bounds)
            return {"success": True, "status": "passed", "closed": element is not None, "closed_elements": [element] if element else []}

        popups = [
            key
            for key, element in list(self.device_manager.device_state.elements.items())
            if element.attrs.get("type") == "dialog" or "dialog" in key or "popup" in key
        ]
        for key in popups:
            self.device_manager.device_state.elements.pop(key, None)
        closed = bool(popups)
        if popup_detected and not closed:
            self.device_manager._log(f"popup reported but not found bounds={popup_bounds}")
        self._record("mobile_close_popup", popup_detected=popup_detected, popup_bounds=popup_bounds)
        return {"success": True, "status": "passed", "closed": closed, "closed_elements": popups}

    def find_close_button(self) -> dict[str, Any]:
        element = next(
            (
                item
                for item in self._element_rows()
                if any(token in (item["text"] or item["resource_id"]).lower() for token in ["关闭", "close", "skip", "跳过", "x"])
            ),
            None,
        )
        return {"success": element is not None, "element": element}

    def assert_text(self, text: str) -> dict[str, Any]:
        matched = [item for item in self._element_rows() if text in item["text"]]
        if not matched and text in self.device_manager.get_page_source():
            matched = [{"text": text}]
        success = bool(matched)
        return {"success": success, "status": "passed" if success else "failed", "text": text, "matched": matched}

    def start_toast_watch(self) -> dict[str, Any]:
        self.toast_watch_enabled = True
        self.last_toast = ""
        return {"success": True, "status": "passed", "watching": True}

    def get_toast(self, timeout: float = 5.0, reset_first: bool = False) -> dict[str, Any]:
        if reset_first:
            self.last_toast = ""
        return {"success": bool(self.last_toast), "text": self.last_toast, "timeout": timeout}

    def assert_toast(self, expected_text: str, timeout: float = 5.0, contains: bool = True) -> dict[str, Any]:
        actual = self.last_toast or (self.device_manager.device_state.logs[-1] if self.device_manager.device_state.logs else "")
        matched = expected_text in actual if contains else actual == expected_text
        return {
            "success": matched,
            "status": "passed" if matched else "failed",
            "expected_text": expected_text,
            "actual_text": actual,
            "timeout": timeout,
            "contains": contains,
        }

    def clear_operation_history(self) -> dict[str, Any]:
        self.operation_history.clear()
        return {"success": True, "status": "passed"}

    def get_operation_history(self, limit: int | None = None) -> dict[str, Any]:
        items = self.operation_history[-limit:] if limit else list(self.operation_history)
        return {"success": True, "operations": items, "count": len(items)}

    def generate_test_script(self, test_name: str, package_name: str, filename: str) -> dict[str, Any]:
        target = self.report_writer.root / "generated_tests" / f"{filename}.py"
        target.parent.mkdir(parents=True, exist_ok=True)
        safe_name = re.sub(r"[^0-9a-zA-Z_]+", "_", test_name).strip("_") or "generated_mobile_case"
        lines = [
            "from core.executor.runner import Runner",
            "",
            "",
            f"def test_{safe_name}():",
            "    runner = Runner()",
        ]
        for item in self.operation_history:
            lines.append(f"    runner.server.call_tool({item['tool']!r}, **{item['arguments']!r})")
        lines.extend(
            [
                "    current = runner.server.call_tool('mobile_get_current_app')",
                f"    assert current['package_name'] == {package_name!r}",
            ]
        )
        target.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return {"success": True, "status": "passed", "path": str(target), "operation_count": len(self.operation_history)}

    def template_add(
        self,
        template_name: str,
        category: str = "close_buttons",
        x_percent: float | None = None,
        y_percent: float | None = None,
        size: int | None = None,
        screenshot_path: str | None = None,
        x: int | None = None,
        y: int | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> dict[str, Any]:
        target = self.templates_dir / category / f"{template_name}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "template_name": template_name,
            "category": category,
            "x_percent": x_percent,
            "y_percent": y_percent,
            "size": size,
            "screenshot_path": screenshot_path,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
        }
        write_json(target, payload)
        return {"success": True, "status": "passed", "path": str(target)}

    def template_close(self, click: bool = True, threshold: float = 0.75) -> dict[str, Any]:
        button = self.find_close_button()
        if click and button.get("element"):
            self._click_element(button["element"])
        return {"success": button.get("element") is not None, "clicked": click and button.get("element") is not None, "threshold": threshold}

    def template_match(self, template_name: str | None = None, category: str | None = None, threshold: float = 0.75) -> dict[str, Any]:
        base = self.templates_dir / (category or "")
        matches = sorted(str(path) for path in base.rglob("*.json") if not template_name or path.stem == template_name)
        return {"success": bool(matches), "matches": matches, "threshold": threshold}

    def template_match_and_click(self, template_name: str | None = None, category: str | None = None, threshold: float = 0.75) -> dict[str, Any]:
        match = self.template_match(template_name=template_name, category=category, threshold=threshold)
        if match["success"]:
            self.device_manager._log(f"template clicked {template_name or category or 'default'}")
        return {"success": match["success"], "clicked": match["success"], "matches": match["matches"], "threshold": threshold}

    def close_ad(self) -> dict[str, Any]:
        result = self.close_popup()
        result["auto_learn"] = True
        return result

    def get_current_app(self) -> dict[str, Any]:
        if self.device_manager.is_simulation_backend():
            package_name = self.device_manager.get_current_app()
            activity = self.device_manager.get_current_activity()
            screen = self.device_manager.device_state.current_screen
        else:
            package_name = self.observe_executor.execute("get_current_app", {}).get("package_name", "")
            activity = self.observe_executor.execute("get_current_activity", {}).get("activity", "")
            screen = activity or package_name or "unknown"
        return {
            "success": True,
            "package_name": package_name,
            "activity": activity,
            "screen": screen,
        }

    def open_deep_link(self, url: str) -> dict[str, Any]:
        lowered = url.lower()
        if "home" in lowered:
            self.device_manager._set_screen("home")
        elif self.device_manager.device_state.current_screen == "stopped":
            self.device_manager.launch_app()
        self._record("mobile_open_deep_link", url=url)
        return {"success": True, "status": "passed", "url": url, "activity": self.device_manager.get_current_activity()}

    def get_clipboard(self) -> dict[str, Any]:
        return {"success": True, "text": self.clipboard_text}

    def set_clipboard(self, text: str) -> dict[str, Any]:
        self.clipboard_text = text
        return {"success": True, "status": "passed", "text": text}

    def start_screen_record(self) -> dict[str, Any]:
        self.screen_record_active = True
        self.screen_record_path = str(self.report_writer.videos_dir / f"{uuid4().hex[:8]}_recording.mp4")
        return {"success": True, "status": "passed", "path": self.screen_record_path}

    def stop_screen_record(self, case_id: str | None = None) -> dict[str, Any]:
        target = Path(self.screen_record_path or self.report_writer.videos_dir / f"{case_id or 'adhoc_recording'}.mp4")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"sim-video")
        self.screen_record_active = False
        self.screen_record_path = str(target)
        return {"success": True, "status": "passed", "path": str(target)}

    def open_new_chat(self, message: str = "继续执行移动端测试") -> dict[str, Any]:
        return {"success": True, "status": "passed", "message": message}

    def get_page_source(self, case_id: str | None = None, save: bool = False, path: str | None = None) -> dict[str, Any]:
        result = self.observe_executor.execute("get_page_source", {})
        if save:
            target = Path(path or self.report_writer.page_sources_dir / f"{case_id or 'adhoc'}_page_source.xml")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(result["content"], encoding="utf-8")
            result["path"] = str(target)
        return result

    def get_current_activity(self) -> dict[str, Any]:
        return self.observe_executor.execute("get_current_activity", {})

    def element_exists(self, locator: dict[str, str]) -> dict[str, Any]:
        return self.observe_executor.execute("element_exists", {"locator": locator})

    def get_element_text(self, locator: dict[str, str]) -> dict[str, Any]:
        return self.observe_executor.execute("get_element_text", {"locator": locator})

    def get_element_attrs(self, locator: dict[str, str]) -> dict[str, Any]:
        return self.observe_executor.execute("get_element_attrs", {"locator": locator})

    def get_logcat(self, case_id: str | None = None, save: bool = False, path: str | None = None) -> dict[str, Any]:
        result = self.observe_executor.execute("get_logcat", {})
        if save:
            target = Path(path or self.report_writer.logs_dir / f"{case_id or 'adhoc'}_logcat.txt")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(result["content"], encoding="utf-8")
            result["path"] = str(target)
        return result

    def get_device_state(self) -> dict[str, Any]:
        return self.observe_executor.execute("get_device_state", {})

    def get_system_state(self, setting: str | None = None) -> dict[str, Any]:
        if setting is None:
            return {"success": True, "state": self.get_device_state().get("state", {})}
        payload = self.observe_executor.execute("get_system_state", {"setting": setting})
        return {"success": True, **payload}

    def assert_device_state(self, field: str, expected: Any, description: str = "设备状态断言", level: str = "strong") -> dict[str, Any]:
        spec = AssertionSpecModel(
            operator="device_state_equals",
            level=level,
            description=description,
            expected=expected,
            metadata={"field": field},
        )
        return self.assertion_engine.evaluate_one(spec, {}).model_dump(mode="json")

    def assert_system_state(self, setting: str, expected: Any, description: str = "系统状态断言", level: str = "strong") -> dict[str, Any]:
        setting_key = resolve_toggle_key(setting) or resolve_value_key(setting) or setting
        field = setting_key
        if setting_key in SYSTEM_TOGGLE_SPECS:
            field = SYSTEM_TOGGLE_SPECS[setting_key].field
        elif setting_key in SYSTEM_VALUE_SPECS:
            field = SYSTEM_VALUE_SPECS[setting_key].field
        spec = AssertionSpecModel(
            operator="device_state_equals",
            level=level,
            description=description,
            expected=expected,
            metadata={"field": field},
        )
        return self.assertion_engine.evaluate_one(spec, {}).model_dump(mode="json")

    def assert_permission_dialog(self, expected_visible: bool = True, description: str = "权限弹窗可见性断言", level: str = "strong") -> dict[str, Any]:
        spec = AssertionSpecModel(
            operator="device_state_equals",
            level=level,
            description=description,
            expected=expected_visible,
            metadata={"field": "permission_dialog_visible"},
        )
        return self.assertion_engine.evaluate_one(spec, {}).model_dump(mode="json")

    def run_assertions(self, assertions: list[dict[str, Any]], context: dict[str, Any] | None = None) -> dict[str, Any]:
        specs = [item if isinstance(item, AssertionSpecModel) else AssertionSpecModel(**item) for item in assertions]
        results, verdict, review_reasons = self.assertion_engine.run(specs, context or {})
        return {
            "results": [item.model_dump(mode="json") for item in results],
            "verdict": verdict,
            "review_reasons": review_reasons,
        }

    def assert_page_contract(self, contract: dict[str, Any], description: str = "Page contract assertion", level: str = "strong") -> dict[str, Any]:
        spec = AssertionSpecModel(
            operator="page_signature_match",
            level=level,
            description=description,
            contract=PageContractModel(**contract),
        )
        return self.assertion_engine.evaluate_one(spec, {}).model_dump(mode="json")

    def assert_state(self, expected_activity: str, description: str = "State assertion", level: str = "strong") -> dict[str, Any]:
        spec = AssertionSpecModel(
            operator="activity_is",
            level=level,
            description=description,
            expected=expected_activity,
        )
        return self.assertion_engine.evaluate_one(spec, {}).model_dump(mode="json")

    def assert_text_spec(
        self,
        locator: dict[str, Any],
        expected: str,
        operator: str = "text_equals",
        description: str = "Text assertion",
        level: str = "strong",
    ) -> dict[str, Any]:
        spec = AssertionSpecModel(
            operator=operator,
            level=level,
            description=description,
            locator=LocatorSpec(**locator),
            expected=expected,
        )
        return self.assertion_engine.evaluate_one(spec, {}).model_dump(mode="json")

    def collect_artifacts(self, case_id: str) -> dict[str, Any]:
        return self.report_writer.collect_runtime_artifacts(self.services["server"], case_id).model_dump(mode="json")

    def export_report(self, destination: str = "artifacts/logs/export_summary.json") -> dict[str, Any]:
        return {"path": self.report_writer.export_report(destination)}

    def bundle_evidence(self, case_id: str, artifacts: dict[str, Any], summary: str = "") -> dict[str, Any]:
        target = Path(self.report_writer.logs_dir / f"{case_id}_bundle.json")
        path = write_json(target, {"case_id": case_id, "artifacts": artifacts, "summary": summary})
        return {"path": path}

    def _record(self, tool: str, **arguments: Any) -> None:
        self.operation_history.append({"tool": tool, "arguments": arguments})

    def _update_toast(self, text: str) -> None:
        if self.toast_watch_enabled:
            self.last_toast = text

    def _success_payload(self, result: dict[str, Any], **extra: Any) -> dict[str, Any]:
        status = result.get("status", "passed")
        return {"success": status == "passed", **result, **extra}

    def _element_rows(self) -> list[dict[str, Any]]:
        if not self.device_manager.is_simulation_backend():
            return self._element_rows_from_page_source()
        rows: list[dict[str, Any]] = []
        for index, (resource_id, element) in enumerate(self.device_manager.device_state.elements.items(), start=1):
            bounds = self._bounds_for_index(index)
            rows.append(
                {
                    "resource_id": resource_id,
                    "text": element.text,
                    "bounds": self._format_bounds(bounds),
                    "clickable": not resource_id.endswith("_title"),
                    "hint": element.attrs.get("hint", element.text or resource_id),
                }
            )
        return rows

    def _element_rows_from_page_source(self) -> list[dict[str, Any]]:
        content = self.observe_executor.execute("get_page_source", {}).get("content", "")
        if not content.strip():
            return []
        current_package = self.observe_executor.execute("get_current_app", {}).get("package_name", "")
        try:
            root = ET.fromstring(content)
        except ET.ParseError:
            return []

        rows: list[dict[str, Any]] = []
        for node in root.iter("node"):
            resource_id = (node.attrib.get("resource-id") or "").strip()
            text = (node.attrib.get("text") or "").strip()
            content_desc = (node.attrib.get("content-desc") or "").strip()
            bounds = (node.attrib.get("bounds") or "").strip()
            clickable = (node.attrib.get("clickable") or "").lower() == "true"
            package_name = (node.attrib.get("package") or "").strip()

            if not any([resource_id, text, content_desc]):
                continue
            if not bounds:
                continue
            if current_package and package_name and package_name != current_package:
                continue
            if not (clickable or text or content_desc):
                continue

            rows.append(
                {
                    "resource_id": resource_id,
                    "text": text,
                    "bounds": bounds,
                    "clickable": clickable,
                    "hint": content_desc or text or resource_id,
                }
            )
        return rows

    def _current_activity(self) -> str:
        if self.device_manager.is_simulation_backend():
            return self.device_manager.get_current_activity()
        return self.observe_executor.execute("get_current_activity", {}).get("activity", "")

    def _bounds_for_index(self, index: int) -> tuple[int, int, int, int]:
        column = (index - 1) % 2
        row = (index - 1) // 2
        x1 = 24 + column * 170
        y1 = 120 + row * 88
        x2 = x1 + 152
        y2 = y1 + 60
        return x1, y1, x2, y2

    def _format_bounds(self, bounds: tuple[int, int, int, int]) -> str:
        x1, y1, x2, y2 = bounds
        return f"[{x1},{y1}][{x2},{y2}]"

    def _parse_bounds(self, bounds_str: str | None) -> tuple[int, int, int, int] | None:
        if not bounds_str:
            return None
        matches = [int(item) for item in re.findall(r"\d+", bounds_str)]
        if len(matches) != 4:
            return None
        return tuple(matches)  # type: ignore[return-value]

    def _element_from_bounds(self, bounds: tuple[int | None, int | None, int | None, int | None] | None) -> dict[str, Any] | None:
        if not bounds or any(value is None for value in bounds):
            return None
        normalized = tuple(int(value) for value in bounds)
        for element in self._element_rows():
            if self._parse_bounds(element["bounds"]) == normalized:
                return element
        return None

    def _element_from_percent(self, x_percent: float, y_percent: float) -> dict[str, Any] | None:
        x = 360 * (x_percent / 100.0)
        y = 800 * (y_percent / 100.0)
        for element in self._element_rows():
            bounds = self._parse_bounds(element["bounds"])
            if bounds is None:
                continue
            x1, y1, x2, y2 = bounds
            if x1 <= x <= x2 and y1 <= y <= y2:
                return element
        return None

    def _click_element(self, element: dict[str, Any]) -> dict[str, Any]:
        if element["resource_id"]:
            return self.action_executor.execute("click", {"locator": {"by": "id", "value": element["resource_id"]}})
        if element["text"]:
            return self.action_executor.execute("click", {"locator": {"by": "text", "value": element["text"]}})
        self.device_manager._log(f"generic click {json.dumps(element, ensure_ascii=False)}")
        return {"status": "passed"}
