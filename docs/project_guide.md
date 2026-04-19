# TestAuto 项目指南

## 1. 项目定位

`TestAuto` 现在按 Cursor 的实际使用方式收敛成 5 层结构，目标不是把自然语言直接硬编码成几条点击，而是把测试输入先编译成 DSL，再由技能层解释抽象动作，最后通过 MCP 工具执行并校验。

这条链路适合下面这种场景：

- 测试人员给一份 Excel 用例
- Cursor 先抽出前置条件、操作步骤、预期结果
- 系统把抽象动作整理成 DSL
- 对 `打开蓝牙`、`切后台再回来` 这类抽象动作，用中文技能卡片解释和展开
- 执行层通过 MCP + adb + uiautomator2 落地
- 校验层给出 `PASS / FAIL / NEEDS_REVIEW`
- 报告层输出 DSL、截图、页面源、日志和 AI 诊断

## 2. 五层结构

### 2.1 输入层

目录：`case_input/`

职责：

- 读取 Excel、JSON、YAML、TXT
- 把不同输入形态转成统一的 `NormalizedCase`
- 保留中文列头和测试语义

### 2.2 DSL 编译层

目录：`dsl/`

职责：

- 把原始步骤编译成 DSL `ACTION`
- 明确区分前置条件、操作步骤、预期结果
- 给抽象动作挂上技能提示

### 2.3 技能层

目录：`skills/`

职责：

- 用中文技能卡片描述抽象动作如何落地
- 由 `skills/action_registry.py` 把抽象动作展开成 MCP 步骤
- 当前内置：
  - `打开蓝牙`
  - `首页冒烟`
  - `设备恢复`
  - `打开WLAN`
  - `打开定位`
  - `打开移动数据`
  - `打开NFC`
  - `打开个人热点`
  - `打开飞行模式`
  - `打开控制中心`
  - `打开通知中心`
  - `打开系统设置`
  - `打开系统设置页`
  - `处理权限弹窗`
  - `调整亮度`
  - `调整音量`
  - `深色模式`
  - `自动旋转`

### 2.4 执行层

目录：`mcp_server/`、`core/`

职责：

- 对外提供 `mobile_*` MCP 工具
- 统一调用 adb / uiautomator2 / simulation backend
- 执行动作、采集观察、记录工具调用

当前新增的重要能力：

- `mobile_open_quick_settings`
- `mobile_get_device_state`
- `mobile_assert_device_state`
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

### 2.5 校验与报告层

目录：`assertions/`、`verification/`

职责：

- 运行结构化断言
- 校验设备状态，例如蓝牙开关
- 生成 DSL 化报告与证据包

## 3. 当前主链路

```text
Excel/文本
-> CaseFileLoader
-> CaseNormalizer
-> DSLCompiler
-> CursorActionRegistry
-> ExecutionPlan
-> FlowExecutor
-> AssertionEngine
-> ReportWriter
```

## 4. 默认后端策略

执行后端默认使用 `auto`：

- 若检测到唯一 adb 设备，默认走真机后端
- 若没有可用真机，则自动回退到 simulation 后端

这让本地开发和 Cursor 调试更平滑，也避免仓库里继续保留演示性质过强的默认值。

## 5. 规则与技能

### 5.1 Cursor 规则

目录：`.cursor/rules/`

当前保留：

- `用例编译.mdc`
- `首页冒烟.mdc`
- `系统蓝牙.mdc`
- `设备恢复.mdc`
- `失败诊断.mdc`
- `鸿蒙系统开关.mdc`
- `鸿蒙系统设置.mdc`
- `鸿蒙权限弹窗.mdc`
- `鸿蒙显示与声音.mdc`
- `鸿蒙系统面板.mdc`

### 5.2 技能卡片

目录：`skills/`

当前保留：

- `打开蓝牙.md`
- `首页冒烟.md`
- `设备恢复.md`
- `打开WLAN.md`
- `打开定位.md`
- `打开移动数据.md`
- `打开NFC.md`
- `打开个人热点.md`
- `打开飞行模式.md`
- `打开控制中心.md`
- `打开通知中心.md`
- `打开系统设置.md`
- `打开系统设置页.md`
- `处理权限弹窗.md`
- `调整亮度.md`
- `调整音量.md`
- `深色模式.md`
- `自动旋转.md`

## 6. 用例输入建议

Excel 推荐至少包含以下中文列头：

- `用例ID`
- `用例标题`
- `前置条件`
- `操作步骤`
- `预期结果`

每个单元格可使用换行分隔多条步骤或多条预期。

## 7. 当前边界

当前项目已经更贴近真实 Cursor 场景，但仍保持一些明确边界：

- Android 优先，不扩展 iOS
- 以结构化校验为主，不把视觉模型当最终裁判
- 技能层先覆盖高频抽象动作，再逐步扩展系统能力库
