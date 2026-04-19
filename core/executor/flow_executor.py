from __future__ import annotations

from agent.schemas.step_schema import StepResultModel


class FlowExecutor:
    def __init__(self, server, device_manager) -> None:
        self.server = server
        self.device_manager = device_manager

    def execute_plan(self, plan, context: dict) -> list[StepResultModel]:
        results: list[StepResultModel] = []
        for step in plan.steps:
            try:
                payload = self._execute_step(step, context)
                status = self._status_from_payload(payload)
                results.append(
                    StepResultModel(
                        step_id=step.step_id,
                        action_status=status,
                        observation_summary=self._summary_for_step(step.description, payload),
                        assertion_status="pending",
                        artifacts=self._artifact_list(payload),
                    )
                )
            except Exception as exc:  # pragma: no cover - failure path
                results.append(
                    StepResultModel(
                        step_id=step.step_id,
                        action_status="failed",
                        observation_summary=str(exc),
                        assertion_status="skipped",
                        artifacts=[],
                    )
                )
        return results

    def _execute_step(self, step, context: dict):
        if step.action == "mobile_launch_app":
            return self._launch_app(step, context)
        return self.server.call_tool(step.action, **step.params)

    def _launch_app(self, step, context: dict):
        payload = self.server.call_tool(step.action, **step.params)
        if isinstance(payload, dict) and payload.get("status") == "failed":
            return {
                "status": "failed",
                "error": payload.get("error", "app launch failed"),
                "summary": payload.get("error", "app launch failed"),
            }
        return payload

    def _status_from_payload(self, payload) -> str:
        if isinstance(payload, dict):
            if payload.get("status") in {"passed", "failed"}:
                return payload["status"]
            if payload.get("success") is False:
                return "failed"
        return "passed"

    def _summary_for_step(self, description: str, payload) -> str:
        if not isinstance(payload, dict):
            return description
        if payload.get("error"):
            return str(payload["error"])
        if payload.get("activity"):
            return f"{description} -> {payload['activity']}"
        if payload.get("screen"):
            return f"{description} -> {payload['screen']}"
        if payload.get("text"):
            return f"{description} -> {payload['text']}"
        return description

    def _artifact_list(self, payload) -> list[str]:
        if not isinstance(payload, dict):
            return []
        if payload.get("path"):
            return [str(payload["path"])]
        return []
