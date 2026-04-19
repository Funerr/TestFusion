from __future__ import annotations

import inspect
import json
import os
import subprocess
import sys
from pathlib import Path

from mcp_server.server import LocalMCPServer


ROOT = Path(__file__).resolve().parents[2]


def _send_message(proc: subprocess.Popen, payload: dict) -> None:
    assert proc.stdin is not None
    proc.stdin.write((json.dumps(payload, ensure_ascii=False) + '\n').encode('utf-8'))
    proc.stdin.flush()


def _read_message(proc: subprocess.Popen) -> dict:
    assert proc.stdout is not None
    line = proc.stdout.readline()
    if not line:
        raise RuntimeError('MCP server closed stdout before sending body')
    return json.loads(line.decode('utf-8'))


def test_stdio_mcp_server_exposes_tools():
    env = {**os.environ, "TESTAUTO_DEVICE_BACKEND": "simulation"}
    proc = subprocess.Popen(
        [sys.executable, 'scripts/start_mcp_server.py', '--stdio'],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    try:
        _send_message(
            proc,
            {
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'initialize',
                'params': {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {},
                    'clientInfo': {'name': 'pytest', 'version': '0.1'},
                },
            },
        )
        init_response = _read_message(proc)
        assert init_response['result']['capabilities']['tools']['listChanged'] is False

        # Unknown MCP notifications must not get a JSON-RPC response (no "id"), or the client stream desyncs.
        _send_message(
            proc,
            {'jsonrpc': '2.0', 'method': 'notifications/cancelled', 'params': {'requestId': 0}},
        )
        _send_message(proc, {'jsonrpc': '2.0', 'method': 'notifications/initialized', 'params': {}})
        _send_message(proc, {'jsonrpc': '2.0', 'id': 2, 'method': 'tools/list', 'params': {}})
        list_response = _read_message(proc)
        tools = list_response['result']['tools']
        tool_names = {item['name'] for item in tools}
        assert {'mobile_click_by_id', 'mobile_list_elements', 'mobile_assert_text', 'mobile_start_screen_record'}.issubset(tool_names)
        assert all(set(item).issubset({'name', 'description', 'inputSchema'}) for item in tools)
        assert all(item['inputSchema']['type'] == 'object' for item in tools)

        _send_message(
            proc,
            {
                'jsonrpc': '2.0',
                'id': 3,
                'method': 'tools/call',
                'params': {'name': 'mobile_check_connection', 'arguments': {}},
            },
        )
        call_response = _read_message(proc)
        payload_item = call_response['result']['content'][0]
        assert payload_item['type'] == 'text'
        state = json.loads(payload_item['text'])
        assert state['device']['backend'] == 'simulation'
    finally:
        proc.kill()
        proc.wait(timeout=5)


def test_stdio_mcp_server_supports_json_line_transport():
    env = {**os.environ, "TESTAUTO_DEVICE_BACKEND": "simulation"}
    proc = subprocess.Popen(
        [sys.executable, 'scripts/start_mcp_server.py', '--stdio'],
        cwd=ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
    )
    try:
        _send_message(
            proc,
            {
                'jsonrpc': '2.0',
                'id': 1,
                'method': 'initialize',
                'params': {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {},
                    'clientInfo': {'name': 'pytest', 'version': '0.1'},
                },
            },
        )
        init_response = _read_message(proc)
        assert init_response['result']['serverInfo']['name'] == 'mobile-mcp'
    finally:
        proc.kill()
        proc.wait(timeout=5)


def test_server_uses_official_mcp_stdio_runtime():
    source = inspect.getsource(LocalMCPServer._serve_stdio_async)
    assert "stdio_server" in source
    assert "Server(" in source


def test_repo_root_can_import_official_mcp_package():
    proc = subprocess.run(
        [sys.executable, "-c", "import mcp; print('ok')"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert proc.stdout.strip() == "ok"
