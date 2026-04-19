# Cursor Five-Layer Runtime Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 TestAuto 调整为更适合 Cursor 的 5 层结构，并支持 Excel、DSL、中文技能和系统动作校验。

**Architecture:** 新增输入层、DSL 层和技能层，保留 MCP 执行层与断言层，并把报告逻辑迁到 verification 层。Runner 作为总编排入口，统一把输入编译成可执行计划。

**Tech Stack:** Python, MCP, adb, uiautomator2, pytest

---

### Task 1: 输入层

**Files:**
- Create: `case_input/excel_loader.py`
- Create: `case_input/case_loader.py`
- Modify: `agent/case_parser.py`
- Test: `tests/regression/test_excel_dsl_pipeline.py`

- [x] 写失败测试，覆盖 Excel 中文列头与用例读取
- [x] 实现最小 Excel 解析器
- [x] 把 `agent/case_parser.py` 改成输入层适配器
- [x] 运行回归测试确认通过

### Task 2: DSL 与技能层

**Files:**
- Create: `dsl/models.py`
- Create: `dsl/compiler.py`
- Create: `skills/action_registry.py`
- Create: `skills/*.md`
- Modify: `agent/skill_router.py`
- Modify: `agent/planner.py`
- Test: `tests/regression/test_cursor_rules_integration.py`

- [x] 写失败测试，覆盖中文 DSL 与技能展开
- [x] 实现 DSLCompiler
- [x] 实现中文技能注册与展开
- [x] 运行回归测试确认通过

### Task 3: 执行与校验

**Files:**
- Modify: `core/device/*.py`
- Modify: `mcp_server/mobile_toolkit.py`
- Modify: `mcp_server/tools_*/*.py`
- Modify: `assertions/engine.py`
- Create: `assertions/operators/device_state_equals.py`
- Test: `tests/regression/test_mobile_mcp_alignment.py`

- [x] 写失败测试，覆盖蓝牙状态断言与 MCP 工具
- [x] 实现设备状态字段与快捷开关动作
- [x] 增加设备状态断言
- [x] 运行回归测试确认通过

### Task 4: 报告与文档

**Files:**
- Create: `verification/report_writer.py`
- Create: `verification/failure_analyzer.py`
- Modify: `README.md`
- Modify: `docs/project_guide.md`
- Modify: `.cursor/rules/*.mdc`

- [x] 把 DSL 写进报告和证据包
- [x] 把规则和技能切成中文
- [x] 更新项目说明

### Task 5: 验证

**Files:**
- Modify: `tests/regression/*.py`
- Modify: `tests/stability/*.py`

- [x] 跑 `pytest tests/regression -q`
- [x] 跑 `pytest -q`
- [x] 确认全量通过
