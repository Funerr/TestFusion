from __future__ import annotations

from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from core.executor.runner import Runner


CONTENT_TYPES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
  <Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>
</Types>
"""

ROOT_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>
"""

WORKBOOK_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <sheets>
    <sheet name="Sheet1" sheetId="1" r:id="rId1"/>
  </sheets>
</workbook>
"""

WORKBOOK_RELS_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/sharedStrings" Target="sharedStrings.xml"/>
</Relationships>
"""

STYLES_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>
  <fills count="1"><fill><patternFill patternType="none"/></fill></fills>
  <borders count="1"><border/></borders>
  <cellStyleXfs count="1"><xf/></cellStyleXfs>
  <cellXfs count="1"><xf xfId="0"/></cellXfs>
  <cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>
"""


def _write_simple_excel(path: Path, row: list[str]) -> None:
    shared_strings = [
        "用例ID",
        "用例标题",
        "前置条件",
        "操作步骤",
        "预期结果",
        *row,
    ]
    count = len(shared_strings)
    shared_xml = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        '<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
        f'count="{count}" uniqueCount="{count}">',
    ]
    for value in shared_strings:
        shared_xml.append(f"<si><t>{value}</t></si>")
    shared_xml.append("</sst>")

    sheet_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row r="1">
      <c r="A1" t="s"><v>0</v></c>
      <c r="B1" t="s"><v>1</v></c>
      <c r="C1" t="s"><v>2</v></c>
      <c r="D1" t="s"><v>3</v></c>
      <c r="E1" t="s"><v>4</v></c>
    </row>
    <row r="2">
      <c r="A2" t="s"><v>5</v></c>
      <c r="B2" t="s"><v>6</v></c>
      <c r="C2" t="s"><v>7</v></c>
      <c r="D2" t="s"><v>8</v></c>
      <c r="E2" t="s"><v>9</v></c>
    </row>
  </sheetData>
</worksheet>
"""

    with ZipFile(path, "w", compression=ZIP_DEFLATED) as workbook:
        workbook.writestr("[Content_Types].xml", CONTENT_TYPES_XML)
        workbook.writestr("_rels/.rels", ROOT_RELS_XML)
        workbook.writestr("xl/workbook.xml", WORKBOOK_XML)
        workbook.writestr("xl/_rels/workbook.xml.rels", WORKBOOK_RELS_XML)
        workbook.writestr("xl/styles.xml", STYLES_XML)
        workbook.writestr("xl/sharedStrings.xml", "\n".join(shared_xml))
        workbook.writestr("xl/worksheets/sheet1.xml", sheet_xml)


def test_excel_case_is_compiled_to_chinese_dsl_and_bluetooth_skill(tmp_path: Path):
    case_file = tmp_path / "蓝牙用例.xlsx"
    _write_simple_excel(
        case_file,
        [
            "CASE-001",
            "打开蓝牙后检查开关状态",
            "手机已解锁\n应用无需启动",
            "打开蓝牙",
            "蓝牙已开启",
        ],
    )

    runner = Runner(artifact_root=tmp_path / "artifacts", backend="mock")
    result = runner.run_case_file(case_file)

    assert result.normalized_case.title == "打开蓝牙后检查开关状态"
    assert result.plan is not None
    assert result.plan.dsl_text
    assert "前置条件" in result.plan.dsl_text
    assert "操作步骤" in result.plan.dsl_text
    assert "ACTION 打开蓝牙" in result.plan.dsl_text
    assert "技能.打开蓝牙" in result.plan.selected_skills
    assert [step.action for step in result.plan.steps] == ["mobile_toggle_system_setting"]
    assert result.plan.steps[0].params == {"setting": "bluetooth", "enabled": True, "source": "auto"}
    assert result.final_status == "PASS"
    assert any(item.description == "蓝牙已开启" and item.passed for item in result.assertion_results)
