from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET


_NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


class ExcelCaseLoader:
    HEADER_ALIASES = {
        "case_id": {"用例id", "用例编号", "编号", "id", "case id"},
        "title": {"用例标题", "用例名称", "标题", "title"},
        "preconditions": {"前置条件", "前置", "preconditions"},
        "steps": {"操作步骤", "测试步骤", "步骤", "steps"},
        "expected": {"预期结果", "预期", "expected"},
    }

    def load(self, path: str | Path, case_index: int = 0) -> dict[str, object]:
        source = Path(path)
        with ZipFile(source) as workbook:
            shared_strings = self._read_shared_strings(workbook)
            rows = self._read_rows(workbook, shared_strings)

        if len(rows) < 2:
            raise ValueError(f"excel case file is empty: {source}")

        header_row = rows[0]
        data_rows = [row for row in rows[1:] if any(value.strip() for value in row)]
        try:
            selected = data_rows[case_index]
        except IndexError as exc:
            raise IndexError(f"case index out of range: {case_index}") from exc

        header_map = self._match_headers(header_row)
        return {
            "case_id": self._get_value(selected, header_map, "case_id") or f"excel_case_{case_index + 1:03d}",
            "title": self._get_value(selected, header_map, "title") or "未命名用例",
            "preconditions": self._split_lines(self._get_value(selected, header_map, "preconditions")),
            "steps": self._split_lines(self._get_value(selected, header_map, "steps")),
            "expected": self._split_lines(self._get_value(selected, header_map, "expected")),
            "ambiguities": [],
        }

    def _read_shared_strings(self, workbook: ZipFile) -> list[str]:
        if "xl/sharedStrings.xml" not in workbook.namelist():
            return []
        root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
        strings: list[str] = []
        for item in root.findall("x:si", _NS):
            text = "".join(node.text or "" for node in item.findall(".//x:t", _NS))
            strings.append(text)
        return strings

    def _read_rows(self, workbook: ZipFile, shared_strings: list[str]) -> list[list[str]]:
        root = ET.fromstring(workbook.read("xl/worksheets/sheet1.xml"))
        rows: list[list[str]] = []
        for row in root.findall(".//x:row", _NS):
            cells = row.findall("x:c", _NS)
            values: list[str] = []
            for cell in cells:
                cell_type = cell.attrib.get("t")
                value_node = cell.find("x:v", _NS)
                raw_value = value_node.text if value_node is not None and value_node.text is not None else ""
                if cell_type == "s" and raw_value:
                    values.append(shared_strings[int(raw_value)])
                else:
                    values.append(raw_value)
            rows.append(values)
        return rows

    def _match_headers(self, headers: list[str]) -> dict[str, int]:
        normalized = [self._normalize_header(item) for item in headers]
        matched: dict[str, int] = {}
        for field, aliases in self.HEADER_ALIASES.items():
            for index, value in enumerate(normalized):
                if value in aliases:
                    matched[field] = index
                    break
        return matched

    def _normalize_header(self, value: str) -> str:
        return value.strip().lower().replace(" ", "")

    def _get_value(self, row: list[str], header_map: dict[str, int], field: str) -> str:
        index = header_map.get(field)
        if index is None or index >= len(row):
            return ""
        return row[index].strip()

    def _split_lines(self, raw_value: str) -> list[str]:
        items = [
            line.strip().lstrip("0123456789.、- ").strip()
            for line in raw_value.splitlines()
            if line.strip()
        ]
        return items
