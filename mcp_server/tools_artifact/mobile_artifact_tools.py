from __future__ import annotations

from mcp_server.mobile_toolkit import MobileToolKit


def register(registry, services):
    toolkit = services.setdefault("mobile_toolkit", MobileToolKit(services))

    registry.register(
        "mobile_clear_operation_history",
        "artifact",
        "清空移动操作历史，便于重新录制脚本。",
        lambda: toolkit.clear_operation_history(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    registry.register(
        "mobile_get_operation_history",
        "artifact",
        "读取当前操作历史，兼容旧调用。",
        lambda limit=None: toolkit.get_operation_history(limit=limit),
        input_schema={
            "type": "object",
            "properties": {"limit": {"type": "integer"}},
            "required": [],
        },
        visible=False,
    )
    registry.register(
        "mobile_generate_test_script",
        "artifact",
        "基于已记录操作生成 pytest 脚本。",
        lambda test_name, package_name, filename: toolkit.generate_test_script(
            test_name=test_name,
            package_name=package_name,
            filename=filename,
        ),
        input_schema={
            "type": "object",
            "properties": {
                "test_name": {"type": "string"},
                "package_name": {"type": "string"},
                "filename": {"type": "string"},
            },
            "required": ["test_name", "package_name", "filename"],
        },
    )
    registry.register(
        "mobile_template_add",
        "artifact",
        "记录一个模板截取区域，供后续模板匹配使用。",
        lambda template_name, category="close_buttons", x_percent=None, y_percent=None, size=None, screenshot_path=None, x=None, y=None, width=None, height=None: toolkit.template_add(
            template_name=template_name,
            category=category,
            x_percent=x_percent,
            y_percent=y_percent,
            size=size,
            screenshot_path=screenshot_path,
            x=x,
            y=y,
            width=width,
            height=height,
        ),
        input_schema={
            "type": "object",
            "properties": {
                "template_name": {"type": "string"},
                "category": {"type": "string"},
                "x_percent": {"type": "number"},
                "y_percent": {"type": "number"},
                "size": {"type": "integer"},
                "screenshot_path": {"type": "string"},
                "x": {"type": "integer"},
                "y": {"type": "integer"},
                "width": {"type": "integer"},
                "height": {"type": "integer"},
            },
            "required": ["template_name"],
        },
    )
    registry.register(
        "mobile_template_close",
        "artifact",
        "执行模板方式的关闭弹窗动作，兼容旧调用。",
        lambda click=True, threshold=0.75: toolkit.template_close(click=click, threshold=threshold),
        input_schema={
            "type": "object",
            "properties": {
                "click": {"type": "boolean"},
                "threshold": {"type": "number"},
            },
            "required": [],
        },
        visible=False,
    )
    registry.register(
        "mobile_template_match",
        "artifact",
        "执行模板匹配，兼容旧调用。",
        lambda template_name=None, category=None, threshold=0.75: toolkit.template_match(
            template_name=template_name,
            category=category,
            threshold=threshold,
        ),
        input_schema={
            "type": "object",
            "properties": {
                "template_name": {"type": "string"},
                "category": {"type": "string"},
                "threshold": {"type": "number"},
            },
            "required": [],
        },
        visible=False,
    )
    registry.register(
        "mobile_template_match_and_click",
        "artifact",
        "模板匹配后点击，兼容旧调用。",
        lambda template_name=None, category=None, threshold=0.75: toolkit.template_match_and_click(
            template_name=template_name,
            category=category,
            threshold=threshold,
        ),
        input_schema={
            "type": "object",
            "properties": {
                "template_name": {"type": "string"},
                "category": {"type": "string"},
                "threshold": {"type": "number"},
            },
            "required": [],
        },
        visible=False,
    )
    registry.register(
        "mobile_close_ad",
        "artifact",
        "广告弹窗关闭兼容工具。",
        lambda: toolkit.close_ad(),
        input_schema={"type": "object", "properties": {}, "required": []},
        visible=False,
    )
    registry.register(
        "mobile_set_clipboard",
        "artifact",
        "设置设备剪贴板内容。",
        lambda text: toolkit.set_clipboard(text),
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
    )
    registry.register(
        "mobile_start_screen_record",
        "artifact",
        "开始录制屏幕。",
        lambda: toolkit.start_screen_record(),
        input_schema={"type": "object", "properties": {}, "required": []},
    )
    registry.register(
        "mobile_stop_screen_record",
        "artifact",
        "停止录屏并返回本地视频路径。",
        lambda case_id=None: toolkit.stop_screen_record(case_id=case_id),
        input_schema={
            "type": "object",
            "properties": {"case_id": {"type": "string"}},
            "required": [],
        },
    )
    registry.register(
        "mobile_open_new_chat",
        "artifact",
        "打开新的 Cursor 会话占位工具。",
        lambda message="继续执行移动端测试": toolkit.open_new_chat(message=message),
        input_schema={
            "type": "object",
            "properties": {"message": {"type": "string"}},
            "required": [],
        },
    )
