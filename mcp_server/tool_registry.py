from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ToolDefinition:
    name: str
    category: str
    description: str
    handler: Callable[..., Any]
    input_schema: dict[str, Any] | None = None
    visible: bool = True


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}
        self.history: list[dict[str, Any]] = []

    def register(
        self,
        name: str,
        category: str,
        description: str,
        handler: Callable[..., Any],
        input_schema: dict[str, Any] | None = None,
        visible: bool = True,
    ) -> None:
        self._tools[name] = ToolDefinition(
            name=name,
            category=category,
            description=description,
            handler=handler,
            input_schema=input_schema or {"type": "object", "properties": {}, "additionalProperties": True},
            visible=visible,
        )

    def register_alias(
        self,
        alias: str,
        target: str,
        *,
        visible: bool = False,
        description: str | None = None,
        input_schema: dict[str, Any] | None = None,
        category: str | None = None,
    ) -> None:
        if target not in self._tools:
            raise KeyError(f"target tool not registered: {target}")
        base = self._tools[target]
        self._tools[alias] = ToolDefinition(
            name=alias,
            category=category or base.category,
            description=description or base.description,
            handler=base.handler,
            input_schema=input_schema or base.input_schema,
            visible=visible,
        )

    def call(self, name: str, **kwargs):
        if name not in self._tools:
            raise KeyError(f"tool not registered: {name}")
        tool = self._tools[name]
        result = tool.handler(**kwargs)
        self.history.append({
            "tool": name,
            "category": tool.category,
            "arguments": kwargs,
            "result_preview": self._preview(result),
        })
        return result

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": item.name,
                "description": item.description,
                "inputSchema": item.input_schema,
            }
            for item in self._tools.values()
            if item.visible
        ]

    def list_tool_definitions(self) -> list[dict[str, Any]]:
        return [
            {
                "name": item.name,
                "category": item.category,
                "description": item.description,
                "inputSchema": item.input_schema,
            }
            for item in self._tools.values()
            if item.visible
        ]

    def clear_history(self) -> None:
        self.history.clear()

    def _preview(self, result: Any) -> Any:
        if isinstance(result, dict):
            return {key: result[key] for key in list(result)[:5]}
        return str(result)


def register_default_tools(registry: ToolRegistry, services: dict[str, Any]) -> None:
    from mcp_server.legacy_compat_tools import register as register_legacy_compat
    from mcp_server.tools_action.adb_action_tools import register as register_adb_action
    from mcp_server.tools_action.mobile_action_tools import register as register_mobile_action
    from mcp_server.tools_artifact.adb_artifact_tools import register as register_adb_artifact
    from mcp_server.tools_artifact.mobile_artifact_tools import register as register_mobile_artifact
    from mcp_server.tools_observe.adb_observe_tools import register as register_adb_observe
    from mcp_server.tools_assert.mobile_assert_tools import register as register_mobile_assert
    from mcp_server.tools_observe.mobile_observe_tools import register as register_mobile_observe

    for register in [
        register_mobile_action,
        register_adb_action,
        register_mobile_observe,
        register_adb_observe,
        register_mobile_assert,
        register_mobile_artifact,
        register_adb_artifact,
        register_legacy_compat,
    ]:
        register(registry, services)
