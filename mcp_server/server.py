from __future__ import annotations

import asyncio
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from mcp_server.tool_registry import ToolRegistry, register_default_tools


class LocalMCPServer:
    def __init__(self, services: dict[str, Any]) -> None:
        self.services = services
        self.registry = ToolRegistry()
        self.services["server"] = self
        register_default_tools(self.registry, self.services)

    def call_tool(self, tool_name: str, **kwargs):
        return self.registry.call(tool_name, **kwargs)

    @property
    def tool_calls(self) -> list[dict[str, Any]]:
        return list(self.registry.history)

    def reset_history(self) -> None:
        self.registry.clear_history()

    def serve_stdio(self) -> None:
        asyncio.run(self._serve_stdio_async())

    async def _serve_stdio_async(self) -> None:
        server = Server("mobile-mcp")

        @server.list_tools()
        async def list_tools() -> list[Tool]:
            return self._build_mcp_tools()

        @server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any] | None):
            return await self._handle_mcp_tool_call(name, arguments or {})

        print(f"Mobile MCP Server starting with {len(self.registry.list_tools())} tools", file=sys.stderr)
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    def serve_http(self, host: str = "127.0.0.1", port: int = 8765) -> None:
        outer = self

        class Handler(BaseHTTPRequestHandler):
            def _send(self, payload: dict[str, Any], status: int = 200) -> None:
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))

            def do_GET(self) -> None:  # noqa: N802
                if self.path == "/health":
                    self._send({"status": "ok", "tools": outer.registry.list_tools()})
                else:
                    self._send({"error": "not found"}, status=404)

            def do_POST(self) -> None:  # noqa: N802
                length = int(self.headers.get("Content-Length", "0"))
                payload = json.loads(self.rfile.read(length) or b"{}")
                if self.path == "/tools/list":
                    self._send({"tools": outer.registry.list_tools()})
                    return
                if self.path == "/tools/call":
                    name = payload.get("name")
                    arguments = payload.get("arguments", {})
                    try:
                        result = outer.call_tool(name, **arguments)
                        self._send({"content": [{"type": "text", "text": outer._format_response(result)}], "isError": False})
                    except Exception as exc:  # pragma: no cover - debug endpoint only
                        self._send({"content": [{"type": "text", "text": json.dumps({"error": str(exc)}, ensure_ascii=False)}], "isError": True}, status=500)
                    return
                self._send({"error": "not found"}, status=404)

            def log_message(self, format: str, *args) -> None:  # noqa: A003
                return None

        HTTPServer((host, port), Handler).serve_forever()

    def _build_mcp_tools(self) -> list[Tool]:
        return [
            Tool(
                name=item["name"],
                description=item["description"],
                inputSchema=item["inputSchema"],
            )
            for item in self.registry.list_tools()
        ]

    async def _handle_mcp_tool_call(self, name: str, arguments: dict[str, Any]) -> list[TextContent]:
        try:
            result = self.call_tool(name, **arguments)
            return [TextContent(type="text", text=self._format_response(result))]
        except Exception as exc:  # pragma: no cover - exercised in integration failure paths
            return [TextContent(type="text", text=json.dumps({"error": str(exc)}, ensure_ascii=False, separators=(",", ":")))]

    def _format_response(self, result: Any) -> str:
        if isinstance(result, (dict, list)):
            return json.dumps(result, ensure_ascii=False, separators=(",", ":"))
        return str(result)
