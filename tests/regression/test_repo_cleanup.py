from __future__ import annotations

from pathlib import Path

from core.executor.runner import Runner


REMOVED_REPO_PATHS = {
    ".cursor/debug-155cf9.log",
    ".cursor/rules/login-smoke.mdc",
    "assertions/templates/login_success.json",
    "assertions/templates/dialog_visible.json",
    "assertions/templates/page_arrival.json",
    "assertions/templates/submit_success.json",
    "configs/devices.yaml",
    "configs/env_dev.yaml",
    "configs/env_prod_mock.yaml",
    "configs/env_test.yaml",
    "configs/logging.yaml",
    "core/device/emulator_manager.py",
    "core/flows/login_flow.py",
    "core/flows/order_flow.py",
    "core/pages/detail_page.py",
    "core/pages/login_page.py",
    "core/pages/settings_page.py",
    "core/utils/retry.py",
    "data/accounts",
    "data/mock",
    "data/seed",
    "docs/architecture.md",
    "docs/assertion_design.md",
    "docs/mcp_tool_spec.md",
    "docs/onboarding.md",
    "docs/raw_case_strategy.md",
    "docs/skill_design.md",
    "pydantic",
    "scripts/collect_logs.py",
    "testcases/checkpoints/home_checkpoints.yaml",
    "testcases/checkpoints/login_checkpoints.yaml",
    "testcases/checkpoints/order_checkpoints.yaml",
    "testcases/manual_cases/login_cases.xlsx",
    "testcases/manual_cases/order_cases.xlsx",
    "testcases/manual_cases/smoke_cases.xlsx",
    "testcases/parsed_cases/login_cases.json",
    "tests/generated",
    "tests/regression/test_login_regression.py",
    "tests/regression/test_order_regression.py",
    "tests/regression/test_settings_regression.py",
    "tests/smoke/test_login_smoke.py",
}


def test_redundant_login_mock_and_process_files_are_removed():
    root = Path.cwd()
    leftovers = sorted(str(root / item) for item in REMOVED_REPO_PATHS if (root / item).exists())
    assert not leftovers, f"redundant files should be removed: {leftovers}"


def test_home_smoke_is_default_without_login_steps():
    runner = Runner()
    result = runner.run_text_case("启动应用后看看首页是不是正常")

    assert result.plan is not None
    assert "规则.首页冒烟" in result.plan.selected_skills
    assert all("login" not in step.skill for step in result.plan.steps)
    assert all("登录" not in step.description for step in result.plan.steps)


def test_chinese_skill_cards_exist():
    root = Path.cwd()
    skill_dir = root / "skills"
    assert skill_dir.exists()
    assert (skill_dir / "打开蓝牙.md").exists()
    assert (skill_dir / "关闭蓝牙.md").exists()
    assert (skill_dir / "首页冒烟.md").exists()
    assert (skill_dir / "首页观察.md").exists()
    assert (skill_dir / "打开WLAN.md").exists()
    assert (skill_dir / "打开定位.md").exists()
    assert (skill_dir / "处理权限弹窗.md").exists()
    assert (skill_dir / "调整亮度.md").exists()


def test_skill_cards_have_cursor_frontmatter():
    skill_dir = Path.cwd() / "skills"

    for skill_file in sorted(skill_dir.glob("*.md")):
        content = skill_file.read_text(encoding="utf-8")
        assert content.startswith("---\n"), f"{skill_file.name} should start with YAML frontmatter"

        parts = content.split("---\n", 2)
        assert len(parts) == 3, f"{skill_file.name} should contain complete YAML frontmatter"
        frontmatter = parts[1]

        assert "name:" in frontmatter, f"{skill_file.name} should define name"
        assert "description:" in frontmatter, f"{skill_file.name} should define description"
        assert "call_mcp:" in frontmatter, f"{skill_file.name} should define call_mcp"
        assert "parameters:" in frontmatter, f"{skill_file.name} should define parameters"
