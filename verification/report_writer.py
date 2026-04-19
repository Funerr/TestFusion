from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from agent.schemas.result_schema import ArtifactBundle, CaseResult
from core.utils.json_util import write_json
from core.utils.time_util import iso_now


class ReportWriter:
    def __init__(self, artifact_root: str | Path = "artifacts") -> None:
        self.root = Path(artifact_root)
        self.screenshots_dir = self.root / "screenshots"
        self.page_sources_dir = self.root / "page_sources"
        self.logs_dir = self.root / "logs"
        self.videos_dir = self.root / "videos"
        self.allure_dir = self.root / "allure-results"
        self.ai_reports_dir = self.root / "ai_reports"
        for path in [
            self.screenshots_dir,
            self.page_sources_dir,
            self.logs_dir,
            self.videos_dir,
            self.allure_dir,
            self.ai_reports_dir,
            self.root / "allure-report",
        ]:
            path.mkdir(parents=True, exist_ok=True)

    def collect_runtime_artifacts(self, server, case_id: str) -> ArtifactBundle:
        screenshot = server.call_tool("mobile_take_screenshot", case_id=case_id)
        page_source = server.call_tool("get_page_source", case_id=case_id, save=True)
        logcat = server.call_tool("get_logcat", case_id=case_id, save=True)
        return ArtifactBundle(
            screenshots=[screenshot["path"]],
            page_sources=[page_source["path"]],
            logs=[logcat["path"]],
        )

    def write_case_outputs(self, result: CaseResult) -> ArtifactBundle:
        result_json = write_json(self.logs_dir / f"{result.case_id}_result.json", result.model_dump(mode="json"))
        review_report = None
        if result.final_status == "NEEDS_REVIEW":
            review_report = self._write_text(
                self.ai_reports_dir / f"{result.case_id}_review.md",
                "\n".join(["# Review Required", *result.review_reasons]),
            )
        ai_report = self._write_text(self.ai_reports_dir / f"{result.case_id}_ai_report.md", self._build_ai_report(result))
        allure_status = {"PASS": "passed", "FAIL": "failed", "NEEDS_REVIEW": "unknown"}[result.final_status]
        allure_result = write_json(
            self.allure_dir / f"{uuid4()}-result.json",
            {
                "uuid": str(uuid4()),
                "name": result.normalized_case.title,
                "status": allure_status,
                "stage": "finished",
                "start": iso_now(),
                "stop": iso_now(),
                "labels": [{"name": "suite", "value": "cursor_mobile_framework"}],
            },
        )
        evidence_bundle = write_json(
            self.logs_dir / f"{result.case_id}_evidence_bundle.json",
            {
                "dsl": result.plan.dsl_text if result.plan else "",
                "screenshots": result.artifacts.screenshots,
                "page_sources": result.artifacts.page_sources,
                "logs": result.artifacts.logs,
                "summary": result.summary,
            },
        )
        result.artifacts.result_json = result_json
        result.artifacts.ai_report = ai_report
        result.artifacts.review_report = review_report
        result.artifacts.allure_result = allure_result
        result.artifacts.evidence_bundle = evidence_bundle
        return result.artifacts

    def export_report(self, destination: str | Path) -> str:
        payload = {
            "artifact_root": str(self.root),
            "logs": sorted(path.name for path in self.logs_dir.glob("*.json")),
            "ai_reports": sorted(path.name for path in self.ai_reports_dir.glob("*.md")),
        }
        return write_json(destination, payload)

    def write_screenrecord(self, case_id: str) -> str:
        target = self.videos_dir / f"{case_id}.mp4"
        target.write_bytes(b"sim-video")
        return str(target)

    def _build_ai_report(self, result: CaseResult) -> str:
        lines = [
            f"# AI Analysis for {result.case_id}",
            f"- Title: {result.normalized_case.title}",
            f"- Final Status: {result.final_status}",
            f"- Execution Mode: {result.execution_mode}",
            f"- Summary: {result.summary}",
        ]
        if result.plan:
            lines.extend(
                [
                    "- DSL:",
                    "```text",
                    result.plan.dsl_text,
                    "```",
                ]
            )
        if result.failure_analysis:
            lines.extend(
                [
                    f"- Probable Cause: {result.failure_analysis.probable_cause}",
                    f"- Suggestion: {result.failure_analysis.suggestion}",
                ]
            )
        if result.review_reasons:
            lines.append("- Review Reasons:")
            lines.extend(f"  - {item}" for item in result.review_reasons)
        return "\n".join(lines) + "\n"

    def _write_text(self, path: Path, content: str) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return str(path)
