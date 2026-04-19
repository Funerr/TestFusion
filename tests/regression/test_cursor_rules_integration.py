from __future__ import annotations

import json
from pathlib import Path


def test_cursor_rules_and_mcp_registration_exist(runner):
    mcp_config = Path('.cursor/mcp.json')
    assert mcp_config.exists(), '.cursor/mcp.json must exist for Cursor MCP registration'

    payload = json.loads(mcp_config.read_text(encoding='utf-8'))
    assert 'mobile' in payload['mcpServers']
    config = payload['mcpServers']['mobile']
    assert config['command']
    assert config['command'] != 'python'
    assert Path(config['command']).is_absolute()
    assert Path(config['cwd']).is_absolute()
    assert config['cwd'].endswith('TestAuto')
    assert config['args'][0] == '-u'
    assert Path(config['args'][1]).is_absolute()
    assert config['args'][1].endswith('scripts/start_mcp_server.py')

    rules_dir = Path('.cursor/rules')
    assert rules_dir.exists()
    rule_names = {path.name for path in rules_dir.glob('*.mdc')}
    assert {
        '用例编译.mdc',
        '首页冒烟.mdc',
        '系统蓝牙.mdc',
        '设备恢复.mdc',
        '失败诊断.mdc',
        '鸿蒙系统开关.mdc',
        '鸿蒙系统设置.mdc',
        '鸿蒙权限弹窗.mdc',
        '鸿蒙显示与声音.mdc',
        '鸿蒙系统面板.mdc',
    }.issubset(rule_names)

    result = runner.run_text_case('启动应用后看看首页是不是正常')
    assert '规则.首页冒烟' in result.plan.selected_skills
    assert result.plan.dsl_text
    assert '操作步骤' in result.plan.dsl_text
