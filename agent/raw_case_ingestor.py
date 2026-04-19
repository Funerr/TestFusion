from __future__ import annotations

from pathlib import Path

from agent.schemas.raw_case_schema import RawCase
from core.utils.time_util import utc_timestamp


class RawCaseIngestor:
    def ingest_text(self, raw_text: str) -> RawCase:
        return RawCase(case_id=self._case_id(raw_text), raw_text=raw_text.strip())

    def ingest_file(self, path: str | Path, line_no: int = 0) -> RawCase:
        lines = [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]
        return self.ingest_text(lines[line_no])

    def _case_id(self, raw_text: str) -> str:
        token = "".join(ch for ch in raw_text if ch.isalnum())[:12] or "case"
        return f"raw_{token}_{utc_timestamp()}"
