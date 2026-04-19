---
name: enable-wlan
description: Use when 需要在鸿蒙 4.2 设备上打开 WLAN 或 Wi‑Fi，并希望用统一 skill 解释抽象系统动作。
call_mcp: true
parameters:
  method:
    type: string
    required: false
    description: 执行方式，可选 auto、control_center 或 settings，默认 auto
  verify:
    type: boolean
    required: false
    description: 是否在执行后校验 WLAN 状态，默认 true
---

# Implementation

1. 优先打开控制中心，必要时回退到 WLAN 设置页。
2. 执行 `mobile_toggle_system_setting`，传入 `setting="wlan"` 和 `enabled=true`。
3. 通过 `mobile_assert_system_state` 校验 WLAN 已开启。

# Examples

## Example 1 - 打开 WLAN
**Input:**
```json
{"method":"control_center","verify":true}
```
