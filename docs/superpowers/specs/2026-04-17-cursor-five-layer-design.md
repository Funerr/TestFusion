# Cursor 五层结构设计

## 目标

把项目收敛成更适合 Cursor 的 5 层结构，支持：

- Excel 用例输入
- 中文规则与技能
- DSL 编译
- MCP + adb + uiautomator2 执行
- 结构化校验与报告

## 设计

### 1. 输入层 `case_input/`

负责读取 Excel、JSON、YAML、TXT，并统一转换成 `NormalizedCase`。

### 2. DSL 层 `dsl/`

负责把原始步骤编译成更稳定的 DSL 表达，明确：

- 前置条件
- 操作步骤
- 预期结果

### 3. 技能层 `skills/`

负责解释抽象动作，并由 `CursorActionRegistry` 展开成 MCP 步骤。

### 4. 执行层 `mcp_server/` + `core/`

负责提供 `mobile_*` 工具并落到设备动作。

### 5. 校验与报告层 `assertions/` + `verification/`

负责状态校验、失败分析、证据打包和 DSL 报告。

## 本轮实现重点

- 新增 Excel 导入
- 新增 DSL 渲染
- 新增中文规则与技能卡片
- 新增“打开蓝牙”系统动作链路
- 新增设备状态断言
- 默认后端改为 `auto -> adb / simulation`
