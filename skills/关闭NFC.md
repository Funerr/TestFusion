---
name: disable-nfc
description: Use when 需要在鸿蒙 4.2 设备上关闭 NFC，并将抽象系统动作展开为可执行的 MCP 步骤。
call_mcp: true
parameters:
  method:
    type: string
    required: false
    description: 执行方式，可选 auto、control_center 或 settings，默认 auto
  verify:
    type: boolean
    required: false
    description: 是否在执行后校验 NFC 状态，默认 true
---

# Implementation

1. 优先打开控制中心，必要时回退到 NFC 设置页。
2. 执行 `mobile_toggle_system_setting`，传入 `setting="nfc"` 和 `enabled=false`。
3. 通过 `mobile_assert_system_state` 或系统页面元素确认 NFC 已关闭。

# Examples

## Example 1 - 关闭 NFC
**Input:**
```json
{"method":"auto","verify":true}
```
