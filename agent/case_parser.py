from __future__ import annotations

from pathlib import Path

from agent.raw_case_ingestor import RawCaseIngestor
from agent.schemas.normalized_case_schema import NormalizedCase
from case_input.case_loader import CaseFileLoader


class CaseParser:
    def __init__(self) -> None:
        self.ingestor = RawCaseIngestor()
        self.loader = CaseFileLoader()

    def parse_text(self, text: str):
        return self.ingestor.ingest_text(text)

    def parse_file(self, path: str | Path, case_index: int = 0) -> NormalizedCase:
        return self.loader.load(path, case_index)
