from __future__ import annotations

from core.executor.runner import Runner


EXPECTED_MOBILE_TOOL_NAMES = {
    'mobile_open_quick_settings',
    'mobile_open_control_center',
    'mobile_open_notification_center',
    'mobile_open_system_settings',
    'mobile_open_system_page',
    'mobile_toggle_system_setting',
    'mobile_handle_permission_dialog',
    'mobile_set_system_value',
    'mobile_get_device_state',
    'mobile_get_system_state',
    'mobile_assert_device_state',
    'mobile_assert_system_state',
    'mobile_assert_permission_dialog',
    'mobile_list_elements',
    'mobile_find_nearby',
    'mobile_take_screenshot',
    'mobile_screenshot_with_som',
    'mobile_click_by_som',
    'mobile_click_by_text',
    'mobile_click_by_id',
    'mobile_click_by_percent',
    'mobile_click_by_bounds',
    'mobile_long_press_by_text',
    'mobile_long_press_by_id',
    'mobile_input_text_by_id',
    'mobile_swipe',
    'mobile_drag_progress_bar',
    'mobile_press_key',
    'mobile_wait',
    'mobile_hide_keyboard',
    'mobile_launch_app',
    'mobile_terminate_app',
    'mobile_list_apps',
    'mobile_list_devices',
    'mobile_check_connection',
    'mobile_close_popup',
    'mobile_assert_text',
    'mobile_clear_operation_history',
    'mobile_generate_test_script',
    'mobile_template_add',
    'mobile_get_current_app',
    'mobile_open_deep_link',
    'mobile_get_clipboard',
    'mobile_set_clipboard',
    'mobile_start_screen_record',
    'mobile_stop_screen_record',
}

HIDDEN_COMPAT_MOBILE_TOOL_NAMES = {
    'mobile_get_screen_size',
    'mobile_screenshot_with_grid',
    'mobile_click_at_coords',
    'mobile_long_press_by_percent',
    'mobile_long_press_at_coords',
    'mobile_input_at_coords',
    'mobile_find_close_button',
    'mobile_get_toast',
    'mobile_get_operation_history',
    'mobile_close_ad',
    'mobile_template_close',
    'mobile_template_match',
    'mobile_template_match_and_click',
}


def test_registry_exposes_mobile_mcp_style_tool_names():
    runner = Runner()
    names = {item['name'] for item in runner.server.registry.list_tools()}
    missing = EXPECTED_MOBILE_TOOL_NAMES - names
    assert not missing, f'missing mobile-mcp style tools: {sorted(missing)}'


def test_registry_keeps_internal_four_layer_categories():
    runner = Runner()
    categories = {item.category for item in runner.server.registry._tools.values() if item.visible}
    assert {'action', 'observe', 'assert', 'artifact'}.issubset(categories)


def test_registry_keeps_hidden_mobile_mcp_compatibility_tools():
    runner = Runner()
    names = set(runner.server.registry._tools)
    missing = HIDDEN_COMPAT_MOBILE_TOOL_NAMES - names
    assert not missing, f'missing hidden mobile-mcp compatibility tools: {sorted(missing)}'
