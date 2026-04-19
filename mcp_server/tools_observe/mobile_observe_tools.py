from __future__ import annotations

from mcp_server.mobile_toolkit import MobileToolKit


def register(registry, services):
    toolkit = services.setdefault("mobile_toolkit", MobileToolKit(services))

    registry.register(
        "mobile_get_device_state",
        "observe",
        "读取设备状态，例如蓝牙开关、当前页面和连接状态。",
        lambda: toolkit.get_device_state(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    registry.register(
        "mobile_get_system_state",
        "observe",
        "读取系统状态，例如 WLAN、蓝牙、定位、亮度、音量。",
        lambda setting=None: toolkit.get_system_state(setting=setting),
        input_schema={
            "type": "object",
            "properties": {"setting": {"type": "string"}},
            "required": [],
        },
    )
    registry.register(
        "mobile_list_elements",
        "observe",
        "列出当前页可交互元素，优先用它做定位。",
        lambda: toolkit.list_elements(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    registry.register(
        "mobile_find_nearby",
        "observe",
        "查找指定文本附近的元素，适合无文本图片按钮场景。",
        lambda text, direction="right": toolkit.find_nearby(text, direction=direction),
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "direction": {"type": "string", "enum": ["left", "right", "above", "below"]},
            },
            "required": ["text"],
        },
    )
    registry.register(
        "mobile_take_screenshot",
        "observe",
        "截图查看页面布局，可选压缩与裁剪参数。",
        lambda description="", compress=True, crop_x=0, crop_y=0, crop_size=0, case_id=None, path=None: toolkit.take_screenshot(
            description=description,
            compress=compress,
            crop_x=crop_x,
            crop_y=crop_y,
            crop_size=crop_size,
            case_id=case_id,
            path=path,
        ),
        input_schema={
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "compress": {"type": "boolean"},
                "crop_x": {"type": "integer"},
                "crop_y": {"type": "integer"},
                "crop_size": {"type": "integer"},
                "case_id": {"type": "string"},
                "path": {"type": "string"},
            },
            "required": [],
        },
    )
    registry.register(
        "mobile_screenshot_with_som",
        "observe",
        "生成带 SoM 编号的截图，便于对图片按钮做引用。",
        lambda: toolkit.screenshot_with_som(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    registry.register(
        "mobile_get_screen_size",
        "observe",
        "返回屏幕尺寸，兼容旧调用。",
        lambda: toolkit.get_screen_size(),
        input_schema={"type": "object", "properties": {}, "required": []},
        visible=False,
    )
    registry.register(
        "mobile_screenshot_with_grid",
        "observe",
        "生成带网格的截图，兼容旧调用。",
        lambda grid_size=100, show_popup_hints=False: toolkit.screenshot_with_grid(
            grid_size=grid_size,
            show_popup_hints=show_popup_hints,
        ),
        input_schema={
            "type": "object",
            "properties": {
                "grid_size": {"type": "integer"},
                "show_popup_hints": {"type": "boolean"},
            },
            "required": [],
        },
        visible=False,
    )
    registry.register(
        "mobile_list_apps",
        "observe",
        "列出已安装应用，可按关键字过滤。",
        lambda filter=None: toolkit.list_apps(filter_text=filter or ""),
        input_schema={
            "type": "object",
            "properties": {"filter": {"type": "string"}},
            "required": [],
        },
    )
    registry.register(
        "mobile_list_devices",
        "observe",
        "列出当前已连接的移动设备。",
        lambda: toolkit.list_devices(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    registry.register(
        "mobile_check_connection",
        "observe",
        "检查当前设备连接状态与健康度。",
        lambda: toolkit.check_connection(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    registry.register(
        "mobile_find_close_button",
        "observe",
        "查找常见关闭按钮，兼容旧调用。",
        lambda: toolkit.find_close_button(),
        input_schema={"type": "object", "properties": {}, "required": []},
        visible=False,
    )
    registry.register(
        "mobile_get_current_app",
        "observe",
        "获取当前前台应用包名、Activity 与 screen。",
        lambda: toolkit.get_current_app(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    registry.register(
        "mobile_get_clipboard",
        "observe",
        "读取设备剪贴板内容。",
        lambda: toolkit.get_clipboard(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
