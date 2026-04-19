from __future__ import annotations

from pathlib import Path

try:
    import yaml
except Exception:  # pragma: no cover - yaml files are optional in some local environments
    yaml = None

from agent.schemas.normalized_case_schema import NormalizedCase
from case_input.excel_loader import ExcelCaseLoader
from core.utils.json_util import read_json


class CaseFileLoader:
    def __init__(self) -> None:
        self.excel_loader = ExcelCaseLoader()

    def load(self, path: str | Path, case_index: int = 0) -> NormalizedCase:
        source = Path(path)
        suffix = source.suffix.lower()
        if suffix == ".json":
            payload = read_json(source)
            if isinstance(payload, list):
                payload = payload[case_index]
            return NormalizedCase(**payload)
        if suffix in {".yaml", ".yml"}:
            if yaml is None:
                raise RuntimeError("PyYAML is required to parse YAML case files")
            payload = yaml.safe_load(source.read_text(encoding="utf-8"))
            if isinstance(payload, list):
                payload = payload[case_index]
            return NormalizedCase(**payload)
        if suffix == ".xlsx":
            return NormalizedCase(**self.excel_loader.load(source, case_index))

        lines = [line.strip() for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
        return NormalizedCase(
            case_id=f"text_case_{case_index + 1:03d}",
            title=lines[case_index],
            preconditions=[],
            steps=[lines[case_index]],
            expected=[],
            ambiguities=[],
        )
