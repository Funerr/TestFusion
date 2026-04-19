from __future__ import annotations

from mcp_server.mobile_toolkit import MobileToolKit


def register(registry, services):
    toolkit = services.setdefault("mobile_toolkit", MobileToolKit(services))

    registry.register(
        "mobile_assert_device_state",
        "assert",
        "断言设备状态字段等于预期值。",
        lambda field, expected: toolkit.assert_device_state(field, expected, description=f"{field} 状态校验"),
        input_schema={
            "type": "object",
            "properties": {
                "field": {"type": "string"},
                "expected": {},
            },
            "required": ["field", "expected"],
        },
    )
    registry.register(
        "mobile_assert_system_state",
        "assert",
        "断言系统状态等于预期值，例如 WLAN、亮度、深色模式。",
        lambda setting, expected: toolkit.assert_system_state(setting, expected, description=f"{setting} 状态校验"),
        input_schema={
            "type": "object",
            "properties": {
                "setting": {"type": "string"},
                "expected": {},
            },
            "required": ["setting", "expected"],
        },
    )
    registry.register(
        "mobile_assert_permission_dialog",
        "assert",
        "断言权限弹窗当前是否可见。",
        lambda expected_visible=True: toolkit.assert_permission_dialog(expected_visible=expected_visible),
        input_schema={
            "type": "object",
            "properties": {"expected_visible": {"type": "boolean"}},
            "required": [],
        },
    )
    registry.register(
        "mobile_assert_text",
        "assert",
        "断言当前页面包含指定文本。",
        lambda text: toolkit.assert_text(text),
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    )
    registry.register(
        "mobile_start_toast_watch",
        "assert",
        "开始监听 Toast 文本。",
        lambda: toolkit.start_toast_watch(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    registry.register(
        "mobile_get_toast",
        "assert",
        "获取最近一次 Toast 文本，兼容旧调用。",
        lambda timeout=5.0, reset_first=False: toolkit.get_toast(timeout=timeout, reset_first=reset_first),
        input_schema={
            "type": "object",
            "properties": {
                "timeout": {"type": "number"},
                "reset_first": {"type": "boolean"},
            },
            "required": [],
        },
        visible=False,
    )
    registry.register(
        "mobile_assert_toast",
        "assert",
        "断言最近一次 Toast 内容。",
        lambda expected_text, timeout=5.0, contains=True: toolkit.assert_toast(
            expected_text,
            timeout=timeout,
            contains=contains,
        ),
        input_schema={
            "type": "object",
            "properties": {
                "expected_text": {"type": "string"},
                "timeout": {"type": "number"},
                "contains": {"type": "boolean"},
            },
            "required": ["expected_text"],
        },
    )
