from __future__ import annotations

import os
from pathlib import Path
from typing import Any

try:
    import yaml
except Exception:  # pragma: no cover - dependency is optional in local environments
    yaml = None

from agent.ambiguity_detector import AmbiguityDetector
from agent.case_normalizer import CaseNormalizer
from agent.case_parser import CaseParser
from agent.checkpoint_extractor import CheckpointExtractor
from agent.executability_scorer import ExecutabilityScorer
from agent.schemas.result_schema import ArtifactBundle, AssertionResultModel, CaseResult
from assertions.engine import AssertionEngine
from core.device.device_manager import DeviceManager
from core.executor.action_executor import ActionExecutor
from core.executor.flow_executor import FlowExecutor
from core.executor.observe_executor import ObserveExecutor
from mcp_server.server import LocalMCPServer
from verification.failure_analyzer import FailureAnalyzer
from verification.report_writer import ReportWriter
from agent.planner import Planner
from agent.raw_case_ingestor import RawCaseIngestor


class Runner:
    def __init__(self, artifact_root: str | Path | None = None, backend: str | None = None) -> None:
        framework = self._load_yaml("configs/framework.yaml")
        app_cfg = {
            "simulation_package": "com.example.cursor.app",
            "simulation_home_activity": "com.example.cursor.MainActivity",
            "real_package": None,
            "real_home_activity": None,
            **framework.get("app", {}),
        }
        execution_cfg = {
            "backend": "auto",
            "retry_times": 2,
            "default_timeout": 5,
            "poll_interval": 0.2,
            **framework.get("execution", {}),
        }
        reporting_cfg = {
            "artifact_root": "artifacts",
            **framework.get("reporting", {}),
        }

        selected_backend = backend or os.getenv("TESTAUTO_DEVICE_BACKEND") or execution_cfg.get("backend", "auto")
        resolved_backend = self._resolve_backend(selected_backend)
        selected_artifact_root = Path(
            artifact_root or os.getenv("TESTAUTO_ARTIFACT_ROOT") or reporting_cfg.get("artifact_root", "artifacts")
        )

        if resolved_backend == "adb":
            package = os.getenv("TESTAUTO_APP_PACKAGE") or app_cfg.get("real_package")
            home_activity = os.getenv("TESTAUTO_HOME_ACTIVITY") or app_cfg.get("real_home_activity")
            serial = os.getenv("TESTAUTO_DEVICE_SERIAL") or ""
        else:
            package = os.getenv("TESTAUTO_APP_PACKAGE") or app_cfg.get("simulation_package")
            home_activity = os.getenv("TESTAUTO_HOME_ACTIVITY") or app_cfg.get("simulation_home_activity")
            serial = os.getenv("TESTAUTO_DEVICE_SERIAL") or "simulation-device"

        self.device_manager = DeviceManager(
            backend=resolved_backend,
            serial=serial,
            package=package,
            home_activity=home_activity,
            artifact_root=selected_artifact_root,
        )
        self.action_executor = ActionExecutor(self.device_manager)
        self.observe_executor = ObserveExecutor(self.device_manager)
        self.assertion_engine = AssertionEngine(self.observe_executor)
        self.report_writer = ReportWriter(selected_artifact_root)
        self.services: dict[str, Any] = {
            "device_manager": self.device_manager,
            "action_executor": self.action_executor,
            "observe_executor": self.observe_executor,
            "assertion_engine": self.assertion_engine,
            "report_writer": self.report_writer,
        }
        self.server = LocalMCPServer(self.services)
        self.flow_executor = FlowExecutor(self.server, self.device_manager)
        self.raw_case_ingestor = RawCaseIngestor()
        self.case_normalizer = CaseNormalizer()
        self.case_parser = CaseParser()
        self.ambiguity_detector = AmbiguityDetector()
        self.executability_scorer = ExecutabilityScorer()
        self.checkpoint_extractor = CheckpointExtractor()
        self.planner = Planner(package=self.device_manager.package, home_activity=self.device_manager.home_activity)
        self.failure_analyzer = FailureAnalyzer()

    def run_text_case(self, text: str) -> CaseResult:
        raw_case = self.raw_case_ingestor.ingest_text(text)
        normalized_case = self.case_normalizer.normalize(raw_case)
        return self._run_pipeline(raw_case.raw_text, normalized_case)

    def run_normalized_case(self, case) -> CaseResult:
        return self._run_pipeline(case.title, case)

    def run_case_file(self, path: str | Path, case_index: int = 0) -> CaseResult:
        case = self.case_parser.parse_file(path, case_index)
        return self.run_normalized_case(case)

    def export_report(self, destination: str | Path = "artifacts/logs/export_summary.json") -> str:
        return self.report_writer.export_report(destination)

    def _run_pipeline(self, raw_case_text: str, normalized_case) -> CaseResult:
        detected, detected_reasons = self.ambiguity_detector.detect(raw_case_text)
        ambiguities = list(dict.fromkeys([*normalized_case.ambiguities, *detected_reasons])) if detected else normalized_case.ambiguities
        normalized_case = normalized_case.model_copy(update={"ambiguities": ambiguities})
        score = self.executability_scorer.score(normalized_case)
        checkpoints = self.checkpoint_extractor.extract(normalized_case)
        plan = self.planner.build_plan(normalized_case, score.recommended_mode, checkpoints)
        self.server.reset_history()
        self.device_manager.prepare()
        self.server.call_tool("mobile_start_screen_record")
        context = {
            "server": self.server,
            "device_manager": self.device_manager,
            "execution_mode": score.recommended_mode,
            "ambiguities": ambiguities,
            "normalized_case": normalized_case,
        }
        step_results = self.flow_executor.execute_plan(plan, context)
        artifact_payload = self.server.call_tool("collect_artifacts", case_id=normalized_case.case_id)
        video_payload = self.server.call_tool("mobile_stop_screen_record", case_id=normalized_case.case_id)
        assertion_payload = self.server.call_tool(
            "run_assertions",
            assertions=[item.model_dump(mode="json") for item in plan.assertions],
            context={"execution_mode": score.recommended_mode, "ambiguities": ambiguities},
        )
        verdict = assertion_payload["verdict"]
        review_reasons = list(assertion_payload["review_reasons"])
        if any(item.action_status != "passed" for item in step_results):
            verdict = "FAIL"
            review_reasons.append("存在动作执行失败")
        assertion_results = [AssertionResultModel(**item) for item in assertion_payload["results"]]
        step_assertion_status = {"PASS": "passed", "FAIL": "failed", "NEEDS_REVIEW": "needs_review"}[verdict]
        for item in step_results:
            item.assertion_status = step_assertion_status
        artifacts = ArtifactBundle(**artifact_payload)
        artifacts.videos = [video_payload["path"]]
        summary = self._build_summary(verdict, normalized_case.title, review_reasons, assertion_results)
        result = CaseResult(
            case_id=normalized_case.case_id,
            raw_case=raw_case_text,
            normalized_case=normalized_case,
            ambiguities=ambiguities,
            executability_score=score,
            execution_mode=score.recommended_mode,
            final_status=verdict,
            step_results=step_results,
            assertion_results=assertion_results,
            review_reasons=review_reasons,
            artifacts=artifacts,
            summary=summary,
            plan=plan,
            checkpoints=checkpoints,
            tool_calls=self.server.tool_calls,
        )
        result.failure_analysis = self.failure_analyzer.analyze(result)
        self.report_writer.write_case_outputs(result)
        bundle = self.server.call_tool(
            "bundle_evidence",
            case_id=result.case_id,
            artifacts=result.artifacts.model_dump(mode="json"),
            summary=result.summary,
        )
        result.artifacts.evidence_bundle = bundle["path"]
        return result

    def _load_yaml(self, path: str | Path) -> dict[str, Any]:
        source = Path(path)
        if not source.exists() or yaml is None:
            return {}
        return yaml.safe_load(source.read_text(encoding="utf-8")) or {}

    def _resolve_backend(self, configured_backend: str) -> str:
        if configured_backend != "auto":
            return configured_backend
        probe = DeviceManager(backend="adb", serial="", package=None, home_activity=None)
        devices = probe.discover_devices()
        if devices:
            return "adb"
        return "simulation"

    def _build_summary(self, verdict: str, title: str, review_reasons: list[str], assertion_results: list[AssertionResultModel]) -> str:
        passed = sum(1 for item in assertion_results if item.passed)
        total = len(assertion_results)
        if verdict == "PASS":
            return f"{title}：{passed}/{total} 条断言通过，核心检查全部满足。"
        if verdict == "FAIL":
            failed = [item.description for item in assertion_results if not item.passed]
            return f"{title}：存在失败断言 {failed}。"
        return f"{title}：核心检查已执行，建议人工复核，原因：{'；'.join(review_reasons)}。"
