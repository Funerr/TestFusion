# TestAuto

面向 Cursor 的移动端自动化测试框架，核心目标是把测试人员提供的 Excel / 文本用例，编译成更稳定的 DSL、技能展开结果和 MCP 调用步骤，再由 `uiautomator2 + adb + MCP` 完成执行、校验和报告。

## 现在的 5 层结构

1. `case_input/`
   负责读取 Excel、JSON、YAML、TXT 等测试输入。
2. `dsl/`
   负责把原始步骤整理成更清晰的 DSL 表达。
3. `skills/`
   负责解释抽象动作，例如“打开蓝牙”“切后台再恢复”。
4. `mcp_server/` + `core/`
   负责对外暴露 MCP 工具，并落到 adb / uiautomator2 执行。
5. `assertions/` + `verification/`
   负责结构化校验、失败诊断和测试报告。

## 典型链路

```text
Excel/文本用例
-> case_input
-> DSLCompiler
-> Skill Registry
-> MCP 工具执行
-> Assertion Engine
-> Report Writer
```

## 快速开始

```bash
pip install -r requirements.txt
cp .env.example .env
python scripts/run_case.py --text "启动应用后看看首页是不是正常"
python scripts/start_mcp_server.py --stdio
```

## Cursor 侧入口

- MCP 配置：`.cursor/mcp.json`
- 技能说明：`skills/`

## MCP 连接失败排查（Windows 常见）

如果 Cursor 日志出现类似下面的信息：

- `Connection failed: MCP error -32000: Connection closed`
- `ϵͳ�Ҳ���ָ����·����`（这通常是乱码，原文多为“系统找不到指定的路径”）

一般不是 MCP 协议问题，而是 **启动命令或路径不可用**。建议按顺序检查：

1. **使用绝对路径，不要用相对路径**
   - `command` 建议写成 Python 可执行文件的绝对路径。
   - `args` 中脚本也用绝对路径，例如：`D:\\TestFusion\\scripts\\start_mcp_server.py`。
2. **确认 Cursor 启动时的工作目录（cwd）**
   - 如果 `cwd` 指向不存在目录，Windows 会直接报“系统找不到指定的路径”并秒退。
3. **确认解释器和依赖存在**
   - 在同一终端手动执行：
     - `python D:\\TestFusion\\scripts\\start_mcp_server.py --stdio`
   - 若失败，先修复 Python 环境（`pip install -r requirements.txt`）。
4. **避免中文路径/特殊字符路径导致编码异常**
   - 尽量把项目放到纯英文路径（如 `D:\\dev\\TestFusion`）。
5. **先在命令行验证，再粘贴到 `.cursor/mcp.json`**
   - 终端可启动后再填到 Cursor，能避免大量“连上即断开”。

示例（Windows）：

```json
{
  "mcpServers": {
    "testfusion": {
      "command": "C:\\\\Python311\\\\python.exe",
      "args": ["D:\\\\dev\\\\TestFusion\\\\scripts\\\\start_mcp_server.py", "--stdio"],
      "cwd": "D:\\\\dev\\\\TestFusion"
    }
  }
}
```

### 对照你这类日志的“直接结论”

如果日志里出现下面两类报错，说明问题已经很明确：

1. `'<Python313>' 不是内部或外部命令`
   - 你把 `command` 配成了 **目录**（例如 `...\\Python313`），不是可执行文件。
   - 改成 `python`（走 PATH）或 `...\\Python313\\python.exe`（绝对路径）。
2. `python: can't open file '...\\scripts\\start_mcp_server.py': [Errno 2] No such file or directory`
   - 你填的脚本路径不存在（目录名或仓库名写错、脚本不在该位置）。
   - 先在 PowerShell 执行 `Test-Path` 验证，再写入 Cursor 配置。

你可以直接用下面这个模板（和你给的可运行配置写法一致）：

```json
{
  "mcpServers": {
    "testfusion": {
      "command": "python",
      "args": ["D:\\\\06_code\\\\TestFusion\\\\scripts\\\\start_mcp_server.py", "--stdio"],
      "cwd": "D:\\\\06_code\\\\TestFusion",
      "env": {
        "PYTHONPATH": "D:\\\\06_code\\\\TestFusion"
      }
    }
  }
}
```

建议在 Windows 终端逐条验证（都通过再开 Cursor）：

```powershell
where python
Test-Path "D:\06_code\TestFusion\scripts\start_mcp_server.py"
cd D:\06_code\TestFusion
python scripts\start_mcp_server.py --stdio
```

## 当前重点能力

- 支持中文技能卡片
- 支持 Excel 用例导入
- 支持 DSL 渲染与落盘
- 支持系统级抽象动作，例如“打开蓝牙”
- 支持 `PASS / FAIL / NEEDS_REVIEW`

## 鸿蒙 4.2 高频系统能力

当前已经补齐一批更适合华为 / 鸿蒙 4.2 的系统 skill 与 MCP：

- 系统开关：WLAN、蓝牙、定位、移动数据、飞行模式、NFC、个人热点、深色模式、自动旋转
- 系统面板：控制中心、通知中心
- 系统设置：打开设置首页、打开指定设置页
- 权限弹窗：允许、仅本次允许、使用时允许、拒绝
- 系统数值：亮度、媒体音量、铃声音量

核心新增 MCP：

- `mobile_open_control_center`
- `mobile_open_notification_center`
- `mobile_open_system_settings`
- `mobile_open_system_page`
- `mobile_toggle_system_setting`
- `mobile_handle_permission_dialog`
- `mobile_set_system_value`
- `mobile_get_system_state`
- `mobile_assert_system_state`
- `mobile_assert_permission_dialog`
