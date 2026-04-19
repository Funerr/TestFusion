from __future__ import annotations

from core.flows.base_flow import BaseFlow


class RecoverFlow(BaseFlow):
    def run(self) -> dict[str, object]:
        self.server.call_tool("mobile_terminate_app")
        launch = self.server.call_tool("mobile_launch_app")
        return {"status": launch.get("status", "passed"), "summary": "recovered app by relaunch"}
