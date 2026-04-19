# HarmonyOS System Capabilities Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为鸿蒙 4.2 补齐高频系统 skill、MCP 和状态断言能力。

**Architecture:** 使用统一系统目录 `system_catalog` 管理系统开关、数值与页面映射；DSL 负责识别中文系统动作；技能注册表把系统动作展开成 MCP 工具；执行层通过 simulation 或 adb 读取和更新系统状态。

**Tech Stack:** Python, MCP, adb, uiautomator2, pytest

---

### Task 1: 测试锁定

**Files:**
- Create: `tests/regression/test_harmony_system_skills_and_mcp.py`
- Modify: `tests/regression/test_mobile_mcp_alignment.py`

- [x] 写失败测试，覆盖系统 skill 展开
- [x] 写失败测试，覆盖系统 MCP
- [x] 运行测试确认失败

### Task 2: 系统状态模型

**Files:**
- Create: `core/device/system_catalog.py`
- Modify: `core/device/device_state.py`
- Modify: `core/device/device_manager.py`

- [x] 增加系统开关和数值状态
- [x] 增加控制中心、通知中心、设置页、权限弹窗
- [x] 增加系统状态读取与更新

### Task 3: MCP 工具

**Files:**
- Modify: `mcp_server/mobile_toolkit.py`
- Modify: `mcp_server/tools_action/mobile_action_tools.py`
- Modify: `mcp_server/tools_observe/mobile_observe_tools.py`
- Modify: `mcp_server/tools_assert/mobile_assert_tools.py`
- Modify: `core/device/adb_client.py`
- Modify: `core/device/u2_client.py`
- Modify: `core/executor/action_executor.py`
- Modify: `core/executor/observe_executor.py`

- [x] 补系统动作工具
- [x] 补系统状态观测工具
- [x] 补系统状态断言工具

### Task 4: DSL / Skill / Rules

**Files:**
- Modify: `dsl/compiler.py`
- Modify: `skills/action_registry.py`
- Modify: `agent/case_normalizer.py`
- Modify: `agent/checkpoint_extractor.py`
- Create: `skills/*.md`
- Create: `.cursor/rules/*.mdc`

- [x] 增加系统中文动作识别
- [x] 增加系统步骤展开
- [x] 增加鸿蒙系统 skill 和 rules

### Task 5: 文档和验证

**Files:**
- Modify: `README.md`
- Modify: `docs/project_guide.md`

- [x] 更新项目说明
- [x] 跑 `pytest tests/regression -q`
- [x] 跑 `pytest -q`
