from __future__ import annotations

from mcp_server.mobile_toolkit import MobileToolKit


def register(registry, services):
    toolkit = services.setdefault("mobile_toolkit", MobileToolKit(services))

    registry.register(
        "mobile_open_quick_settings",
        "action",
        "打开控制中心或快捷开关面板。",
        lambda: toolkit.open_quick_settings(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    registry.register(
        "mobile_open_control_center",
        "action",
        "打开鸿蒙控制中心。",
        lambda: toolkit.open_control_center(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    registry.register(
        "mobile_open_notification_center",
        "action",
        "打开通知中心。",
        lambda: toolkit.open_notification_center(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    registry.register(
        "mobile_open_system_settings",
        "action",
        "打开系统设置首页。",
        lambda: toolkit.open_system_settings(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    registry.register(
        "mobile_open_system_page",
        "action",
        "打开系统设置指定页面，如 wlan、bluetooth、display、sound。",
        lambda page: toolkit.open_system_page(page),
        input_schema={
            "type": "object",
            "properties": {"page": {"type": "string"}},
            "required": ["page"],
        },
    )
    registry.register(
        "mobile_toggle_system_setting",
        "action",
        "切换鸿蒙系统高频开关，如 WLAN、蓝牙、定位、NFC、深色模式；source=auto 会优先控制中心并自动回退设置页。",
        lambda setting, enabled=None, source="auto": toolkit.toggle_system_setting(setting, enabled=enabled, source=source),
        input_schema={
            "type": "object",
            "properties": {
                "setting": {"type": "string"},
                "enabled": {"type": "boolean"},
                "source": {"type": "string"},
            },
            "required": ["setting"],
        },
    )
    registry.register(
        "mobile_handle_permission_dialog",
        "action",
        "处理鸿蒙权限弹窗，支持 allow、allow_once、allow_while_using、deny。",
        lambda decision: toolkit.handle_permission_dialog(decision),
        input_schema={
            "type": "object",
            "properties": {"decision": {"type": "string"}},
            "required": ["decision"],
        },
    )
    registry.register(
        "mobile_set_system_value",
        "action",
        "设置系统数值类状态，如亮度、媒体音量、铃声音量。",
        lambda setting, value: toolkit.set_system_value(setting, value),
        input_schema={
            "type": "object",
            "properties": {
                "setting": {"type": "string"},
                "value": {"type": "integer"},
            },
            "required": ["setting", "value"],
        },
    )
    registry.register(
        "mobile_click_by_som",
        "action",
        "按 SoM 编号点击元素，配合 screenshot_with_som 使用。",
        lambda index: toolkit.click_by_som(index),
        input_schema={
            "type": "object",
            "properties": {"index": {"type": "integer", "description": "SoM 编号，从 1 开始"}},
            "required": ["index"],
        },
    )
    registry.register(
        "mobile_click_at_coords",
        "action",
        "按绝对坐标点击，兼容旧调用。",
        lambda x, y, image_width=0, image_height=0, crop_offset_x=0, crop_offset_y=0, original_img_width=0, original_img_height=0: toolkit.click_at_coords(
            x,
            y,
            image_width=image_width,
            image_height=image_height,
            crop_offset_x=crop_offset_x,
            crop_offset_y=crop_offset_y,
            original_img_width=original_img_width,
            original_img_height=original_img_height,
        ),
        input_schema={
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "image_width": {"type": "integer"},
                "image_height": {"type": "integer"},
                "crop_offset_x": {"type": "integer"},
                "crop_offset_y": {"type": "integer"},
                "original_img_width": {"type": "integer"},
                "original_img_height": {"type": "integer"},
            },
            "required": ["x", "y"],
        },
        visible=False,
    )
    registry.register(
        "mobile_click_by_text",
        "action",
        "按文本点击元素；有重复文案时可带 position，点击后可选 verify。",
        lambda text, position=None, verify=None: toolkit.click_by_text(text, position=position, verify=verify),
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "目标文本"},
                "position": {"type": "string", "description": "位置提示，可选"},
                "verify": {"type": "string", "description": "点击后补充校验文本，可选"},
            },
            "required": ["text"],
        },
    )
    registry.register(
        "mobile_click_by_id",
        "action",
        "按 resource-id 点击元素。",
        lambda resource_id, index=0: toolkit.click_by_id(resource_id, index=index),
        input_schema={
            "type": "object",
            "properties": {
                "resource_id": {"type": "string", "description": "resource-id"},
                "index": {"type": "integer", "description": "同 id 元素序号，默认 0"},
            },
            "required": ["resource_id"],
        },
    )
    registry.register(
        "mobile_click_by_percent",
        "action",
        "按屏幕百分比坐标点击，作为 text/id/SoM 之后的兜底手段。",
        lambda x_percent, y_percent: toolkit.click_by_percent(x_percent, y_percent),
        input_schema={
            "type": "object",
            "properties": {
                "x_percent": {"type": "number", "description": "X 百分比 0-100"},
                "y_percent": {"type": "number", "description": "Y 百分比 0-100"},
            },
            "required": ["x_percent", "y_percent"],
        },
    )
    registry.register(
        "mobile_click_by_bounds",
        "action",
        "按 bounds 中心点点击，适合无 text 的图片按钮。",
        lambda x1=None, y1=None, x2=None, y2=None, bounds_str=None: toolkit.click_by_bounds(
            x1=x1, y1=y1, x2=x2, y2=y2, bounds_str=bounds_str
        ),
        input_schema={
            "type": "object",
            "properties": {
                "x1": {"type": "integer"},
                "y1": {"type": "integer"},
                "x2": {"type": "integer"},
                "y2": {"type": "integer"},
                "bounds_str": {"type": "string", "description": "形如 [x1,y1][x2,y2]"},
            },
            "required": [],
        },
    )
    registry.register(
        "mobile_long_press_by_text",
        "action",
        "按文本长按元素。",
        lambda text, duration=1.0: toolkit.long_press_by_text(text, duration=duration),
        input_schema={
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "duration": {"type": "number", "description": "长按秒数，默认 1.0"},
            },
            "required": ["text"],
        },
    )
    registry.register(
        "mobile_long_press_by_id",
        "action",
        "按 resource-id 长按元素。",
        lambda resource_id, duration=1.0: toolkit.long_press_by_id(resource_id, duration=duration),
        input_schema={
            "type": "object",
            "properties": {
                "resource_id": {"type": "string"},
                "duration": {"type": "number", "description": "长按秒数，默认 1.0"},
            },
            "required": ["resource_id"],
        },
    )
    registry.register(
        "mobile_long_press_by_percent",
        "action",
        "按百分比坐标长按，兼容旧调用。",
        lambda x_percent, y_percent, duration=1.0: toolkit.long_press_by_percent(
            x_percent,
            y_percent,
            duration=duration,
        ),
        input_schema={
            "type": "object",
            "properties": {
                "x_percent": {"type": "number"},
                "y_percent": {"type": "number"},
                "duration": {"type": "number"},
            },
            "required": ["x_percent", "y_percent"],
        },
        visible=False,
    )
    registry.register(
        "mobile_long_press_at_coords",
        "action",
        "按绝对坐标长按，兼容旧调用。",
        lambda x, y, duration=1.0, image_width=0, image_height=0, crop_offset_x=0, crop_offset_y=0, original_img_width=0, original_img_height=0: toolkit.long_press_at_coords(
            x,
            y,
            duration=duration,
            image_width=image_width,
            image_height=image_height,
            crop_offset_x=crop_offset_x,
            crop_offset_y=crop_offset_y,
            original_img_width=original_img_width,
            original_img_height=original_img_height,
        ),
        input_schema={
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "duration": {"type": "number"},
                "image_width": {"type": "integer"},
                "image_height": {"type": "integer"},
                "crop_offset_x": {"type": "integer"},
                "crop_offset_y": {"type": "integer"},
                "original_img_width": {"type": "integer"},
                "original_img_height": {"type": "integer"},
            },
            "required": ["x", "y"],
        },
        visible=False,
    )
    registry.register(
        "mobile_input_text_by_id",
        "action",
        "按 resource-id 向输入框填入文本。",
        lambda resource_id, text: toolkit.input_text_by_id(resource_id, text),
        input_schema={
            "type": "object",
            "properties": {
                "resource_id": {"type": "string"},
                "text": {"type": "string"},
            },
            "required": ["resource_id", "text"],
        },
    )
    registry.register(
        "mobile_input_at_coords",
        "action",
        "按绝对坐标聚焦并输入文本，兼容旧调用。",
        lambda x, y, text: toolkit.input_at_coords(x, y, text),
        input_schema={
            "type": "object",
            "properties": {
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "text": {"type": "string"},
            },
            "required": ["x", "y", "text"],
        },
        visible=False,
    )
    registry.register(
        "mobile_swipe",
        "action",
        "滑动屏幕，方向与距离都可控制。",
        lambda direction, y=None, y_percent=None, distance=None, distance_percent=None: toolkit.swipe(
            direction,
            y=y,
            y_percent=y_percent,
            distance=distance,
            distance_percent=distance_percent,
        ),
        input_schema={
            "type": "object",
            "properties": {
                "direction": {"type": "string", "enum": ["up", "down", "left", "right"]},
                "y": {"type": "integer"},
                "y_percent": {"type": "number"},
                "distance": {"type": "integer"},
                "distance_percent": {"type": "number"},
            },
            "required": ["direction"],
        },
    )
    registry.register(
        "mobile_drag_progress_bar",
        "action",
        "按方向拖动进度条。",
        lambda direction="right", distance_percent=30.0, y_percent=None, y=None: toolkit.drag_progress_bar(
            direction=direction,
            distance_percent=distance_percent,
            y_percent=y_percent,
            y=y,
        ),
        input_schema={
            "type": "object",
            "properties": {
                "direction": {"type": "string", "enum": ["left", "right"]},
                "distance_percent": {"type": "number"},
                "y_percent": {"type": "number"},
                "y": {"type": "integer"},
            },
            "required": [],
        },
    )
    registry.register(
        "mobile_press_key",
        "action",
        "按系统物理键，例如 back、home、enter。",
        lambda key: toolkit.press_key(key),
        input_schema={
            "type": "object",
            "properties": {"key": {"type": "string"}},
            "required": ["key"],
        },
    )
    registry.register(
        "mobile_wait",
        "action",
        "等待指定秒数。",
        lambda seconds=0.2: toolkit.wait(seconds),
        input_schema={
            "type": "object",
            "properties": {"seconds": {"type": "number"}},
            "required": ["seconds"],
        },
    )
    registry.register(
        "mobile_hide_keyboard",
        "action",
        "收起软键盘。",
        lambda: toolkit.hide_keyboard(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    registry.register(
        "mobile_launch_app",
        "action",
        "启动应用；默认使用当前配置包名。",
        lambda package_name=None, package=None, activity=None: toolkit.launch_app(
            package_name=package_name,
            package=package,
            activity=activity,
        ),
        input_schema={
            "type": "object",
            "properties": {
                "package_name": {"type": "string"},
                "package": {"type": "string"},
                "activity": {"type": "string"},
            },
            "required": [],
        },
    )
    registry.register(
        "mobile_terminate_app",
        "action",
        "终止应用；默认使用当前配置包名。",
        lambda package_name=None, package=None: toolkit.terminate_app(package_name=package_name, package=package),
        input_schema={
            "type": "object",
            "properties": {
                "package_name": {"type": "string"},
                "package": {"type": "string"},
            },
            "required": [],
        },
    )
    registry.register(
        "mobile_close_popup",
        "action",
        "检测并关闭当前弹窗；无弹窗时安全返回。",
        lambda popup_detected=None, popup_bounds=None: toolkit.close_popup(
            popup_detected=popup_detected,
            popup_bounds=popup_bounds,
        ),
        input_schema={
            "type": "object",
            "properties": {
                "popup_detected": {"type": "boolean"},
                "popup_bounds": {"type": "array", "items": {"type": "number"}},
            },
            "required": [],
        },
    )
    registry.register(
        "mobile_open_deep_link",
        "action",
        "通过深链或 URL 直接跳转目标页面。",
        lambda url: toolkit.open_deep_link(url),
        input_schema={
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
        },
    )
