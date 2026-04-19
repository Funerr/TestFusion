下面是**可直接保存为 `PRD.md` 的最终版**。
这版已经合并了：

* 面向 **Codex** 的执行要求
* **模糊/不规范测试用例**处理链路
* **PASS / FAIL / NEEDS_REVIEW** 三态结果
* **Agent + Skill + MCP + adb + uiautomator2 + pytest** 的完整架构
* **可参考 `mobile-mcp` 开源项目** 的约束说明

补充说明：Codex 官方支持仓库内的项目级 `.codex/config.toml` 配置；你提到的 `mobile-mcp` 是一个公开的 Gitee 项目，定位为移动端 UI 自动化，支持 Android/iOS，主要使用 Python 实现，这适合作为 MCP 设计思路参考，但不应成为本项目的强依赖。 ([OpenAI开发者][1])

---

# PRD：移动端 AI 自动化测试框架（Codex 最终执行版）

## 1. 文档信息

* **文档名称**：移动端 AI 自动化测试框架 PRD
* **版本**：V1.0 Final
* **目标执行工具**：Codex
* **项目类型**：从 0 到 1 的移动端 AI 自动化测试框架
* **输出要求**：一次性完整生成可运行项目，而不是骨架、分阶段半成品或概念设计稿

---

## 2. 项目背景

需要建设一个面向 Android 移动端的 AI 增强型自动化测试框架。

该框架既要具备传统自动化测试的**确定性执行能力**，又要具备 AI 在真实测试场景中的**理解、归一化、补全、诊断、报告**能力。

真实团队里的测试用例并不总是规范的，往往存在：

* 描述模糊
* 前置条件缺失
* 步骤不标准
* 预期结果不可直接断言
* 人能理解但机器不能直接执行

因此，本项目的核心目标不是“只执行规范用例”，而是：

```text id="2w7647"
原始模糊测试用例
→ AI归一化
→ 测试意图提取
→ 候选检查点提取
→ 结构化断言生成
→ 确定性执行
→ 三态结果输出
```

---

## 3. 项目目标

### 3.1 核心目标

构建一套完整的移动端 AI 自动化测试框架，要求：

1. 支持原始文本、模糊文本、结构化测试用例输入
2. 支持 Agent + Skill + MCP 的智能编排
3. 支持 adb + uiautomator2 + pytest 的确定性执行
4. 支持结构化断言 DSL 和 Assertion Engine
5. 支持对模糊测试用例进行归一化、歧义识别和可执行性评分
6. 支持输出三态结果：

   * PASS
   * FAIL
   * NEEDS_REVIEW
7. 支持输出执行日志、截图、页面源、报告、AI 诊断结果
8. 支持至少一个可完整跑通的登录 smoke 闭环

### 3.2 非目标

本期不要求：

1. iOS 真正落地支持
2. 云真机平台接入
3. 企业级权限系统
4. 可视化 Web 控制台
5. 分布式调度系统
6. 复杂视觉 AI 识别作为主断言
7. 多仓库远程 orchestration
8. 企业内网系统深度集成

---

## 4. 设计原则

### 4.1 AI 不做最终裁判

AI 可以做：

* 用例理解
* 归一化
* 执行规划
* 检查点提取
* 候选断言生成
* 失败分析
* 报告生成

AI 不可以直接做：

* 最终 PASS / FAIL 裁判

最终测试结论必须由 Assertion Engine 基于结构化规则给出。

### 4.2 动作与观测分离

MCP 层必须明确区分：

* **Action Tools**：执行动作
* **Observe Tools**：获取状态与证据
* **Assert Tools**：执行断言
* **Artifact Tools**：收集产物

### 4.3 模糊用例可落地

框架不能假设测试用例天然规范，必须具备：

* 模糊用例归一化
* 歧义检测
* 候选检查点提取
* 断言降级
* NEEDS_REVIEW 输出

### 4.4 先可运行，再增强

优先保证完整闭环，而不是过度复杂化。

---

## 5. 用户与使用场景

### 5.1 目标用户

* 移动端测试开发工程师
* 自动化测试工程师
* 希望通过 AI 降低测试编写与维护成本的测试团队

### 5.2 核心使用场景

#### 场景 1：执行结构化测试用例

输入 JSON/YAML 用例，自动执行并输出结果。

#### 场景 2：执行原始模糊测试用例

输入类似：

* 登录后看看首页是不是正常
* 切后台再回来应该没问题
* 设置页显示是否正确
* 多点几次看看会不会卡住

框架需要先归一化再执行。

#### 场景 3：自然语言触发

通过 CLI 输入：

* 执行登录 smoke
* 执行首页启动测试
* 执行登录并验证首页

#### 场景 4：失败自动分析

执行失败后自动收集：

* 截图
* 页面源
* activity
* logcat
* 关键断言失败信息

并生成 AI 辅助分析报告。

---

## 6. 总体架构

```text id="8d0uln"
原始测试输入
→ Raw Case Ingestor
→ Case Normalizer
→ Ambiguity Detector
→ Executability Scorer
→ Checkpoint Extractor
→ Agent Case Parser
→ Planner
→ Skill Router
→ Assertion Builder
→ MCP Tools
→ 确定性执行层
→ Observation Layer
→ Assertion Engine
→ Result Builder
→ Report Writer
```

### 6.1 分层说明

#### A. 测试用例理解层

负责：

* 读取原始测试用例
* 归一化
* 歧义检测
* 可执行性评分
* 提取检查点

#### B. Agent 编排层

负责：

* 生成执行计划
* 路由 Skill
* 生成 Assertion Spec
* 协调 MCP 调用
* 汇总结果

#### C. Skill 层

负责：

* 业务流封装
* 页面抽象
* 执行路径抽象
* 恢复流
* 失败诊断流程

#### D. MCP 层

负责暴露统一工具能力：

* Action
* Observe
* Assert
* Artifact

#### E. 确定性执行层

负责：

* adb 调用
* uiautomator2 调用
* pytest 运行
* 页面/流程封装
* 观测数据采集

#### F. 断言层

负责：

* 解析 Assertion DSL
* 调用 Observe 能力
* 给出 PASS / FAIL / NEEDS_REVIEW
* 输出证据

---

## 7. 功能需求

## 7.1 输入层

必须支持以下输入方式：

1. 原始文本测试用例
2. JSON/YAML 测试用例
3. CLI 自然语言命令

### 7.1.1 原始文本示例

* 登录后看看首页是不是正常
* 切后台再回来没问题
* 设置页显示正确
* 打开相机后预览应该正常

### 7.1.2 CLI 示例

```bash id="1v2y2o"
python scripts/run_case.py --text "登录后看看首页是不是正常"
python scripts/run_case.py --text "执行登录 smoke"
python scripts/run_suite.py --suite smoke
```

---

## 7.2 模糊测试用例处理链路

这是本项目的核心能力，必须完整实现。

### 7.2.1 Raw Case Ingestor

负责：

* 读取原始文本
* 保留原始文本原貌
* 生成基础 case_id

### 7.2.2 Case Normalizer

负责将原始测试用例转换为：

* title
* preconditions
* steps
* expected
* ambiguities

示例：

原始：

```text id="x9oa9q"
登录后看看首页是不是正常
```

归一化：

```json id="cb1hgz"
{
  "title": "登录后验证首页可达且关键元素存在",
  "preconditions": [
    "应用已安装",
    "存在可用测试账号"
  ],
  "steps": [
    "启动应用",
    "输入账号",
    "输入密码",
    "点击登录"
  ],
  "expected": [
    "进入首页",
    "首页关键元素存在",
    "无异常弹窗"
  ],
  "ambiguities": [
    "原始描述中“正常”含义不明确，已替换为页面可达+关键元素存在+无异常弹窗"
  ]
}
```

### 7.2.3 Ambiguity Detector

必须识别高风险模糊词，例如：

* 正常
* 没问题
* 看看
* 试试
* 稳定
* 正确
* 合理
* 流畅
* 多次
* 明显异常
* 偶现

输出：

* ambiguity flag
* ambiguity reasons

### 7.2.4 Executability Scorer

必须对用例进行评分，至少包括：

* action_clarity
* expectation_clarity
* observability
* assertability
* overall_score

并给出推荐执行模式：

* auto
* semi_auto
* manual_review

### 7.2.5 Checkpoint Extractor

必须从模糊预期中提取候选检查点。

例如：

原始：

```text id="y7w9ak"
设置页显示正确
```

提取为：

```json id="ax9xlv"
{
  "checkpoints": [
    "设置页标题存在",
    "关键设置项存在",
    "无错误弹窗",
    "当前activity正确"
  ]
}
```

---

## 7.3 Agent 编排层

必须实现以下模块：

### 7.3.1 `case_parser.py`

负责解析：

* 原始文本
* JSON/YAML 用例
* CLI 输入

输出统一内部模型。

### 7.3.2 `planner.py`

负责生成执行计划，执行计划必须包含：

* steps
* selected_skills
* required_tools
* assertion_specs

### 7.3.3 `skill_router.py`

负责根据步骤类型和测试意图自动选择 Skill。

### 7.3.4 `assertion_builder.py`

负责从：

* normalized_case
* checkpoints
* execution_mode

生成 Assertion DSL。

### 7.3.5 `failure_analyzer.py`

负责对失败进行结构化归因，至少输出：

* failed_step
* failed_assertion
* probable_cause
* evidence_summary
* suggestion

### 7.3.6 `report_writer.py`

负责生成：

* JSON 结构化结果摘要
* AI 辅助分析报告
* 复核建议

---

## 7.4 Skill 层

必须实现以下 Skill：

### 7.4.1 通用 Skill

* `login_skill.py`
* `logout_skill.py`
* `search_skill.py`
* `popup_recover_skill.py`

### 7.4.2 页面 Skill

* `home_skill.py`
* `login_page_skill.py`
* `detail_page_skill.py`
* `settings_page_skill.py`

### 7.4.3 领域 Skill

* `app_startup_skill.py`
* `account_flow_skill.py`
* `order_flow_skill.py`
* `network_recover_skill.py`

### 7.4.4 诊断 Skill

* `ui_fail_diagnose_skill.py`
* `logcat_diagnose_skill.py`
* `flaky_case_diagnose_skill.py`

### 7.4.5 Skill 设计要求

Skill 必须：

* 是实际可调用的 Python 模块
* 可组合
* 可复用
* 可被 Planner 调用
* 不得只是文档说明

---

## 7.5 MCP 层

必须实现一个本地可运行的 MCP Server。

### 7.5.1 Action Tools

必须实现：

* `click_tool.py`
* `swipe_tool.py`
* `input_tool.py`
* `back_tool.py`
* `launch_app_tool.py`
* `stop_app_tool.py`
* `wait_tool.py`

### 7.5.2 Observe Tools

必须实现：

* `get_page_source_tool.py`
* `get_current_activity_tool.py`
* `element_exists_tool.py`
* `get_element_text_tool.py`
* `get_element_attrs_tool.py`
* `take_screenshot_tool.py`
* `get_logcat_tool.py`
* `get_device_state_tool.py`

### 7.5.3 Assert Tools

必须实现：

* `run_assertions_tool.py`
* `page_contract_assert_tool.py`
* `text_assert_tool.py`
* `state_assert_tool.py`

### 7.5.4 Artifact Tools

必须实现：

* `collect_artifacts_tool.py`
* `screenrecord_tool.py`
* `export_report_tool.py`
* `bundle_evidence_tool.py`

### 7.5.5 MCP 分层要求

MCP 层必须保留如下结构，不得合并成单一巨型文件：

```text id="x26ji2"
mcp_server/
├─ server.py
├─ tool_registry.py
├─ tools_action/
├─ tools_observe/
├─ tools_assert/
└─ tools_artifact/
```

---

## 7.6 确定性执行层

### 7.6.1 Device Manager

必须支持：

* 设备发现
* 设备连接
* 设备状态检查
* 设备占用与释放

### 7.6.2 ADB Client

必须封装以下能力：

* shell
* install
* uninstall
* start app
* stop app
* pull/push
* dumpsys
* logcat
* screencap

### 7.6.3 U2 Client

必须封装以下能力：

* 点击
* 滑动
* 输入
* 元素定位
* 获取元素属性
* 获取页面源
* 获取当前 activity
* 获取当前 app

### 7.6.4 Action Executor

负责：

* 接收动作请求
* 调用 adb/uiautomator2
* 返回结构化动作结果

### 7.6.5 Observe Executor

负责：

* 执行页面源获取
* 执行元素存在性检查
* 执行文本读取
* 执行截图
* 执行 activity 获取
* 执行 logcat 获取

### 7.6.6 Flow Executor

负责：

* 调用 Skill
* 编排 Flow
* 处理中间异常
* 调用恢复流

### 7.6.7 Runner

负责：

* 运行单 case
* 运行 suite
* 输出结果
* 对接 pytest/allure

---

## 7.7 断言系统

这是本项目的关键模块，必须完整实现。

### 7.7.1 Assertion DSL

至少支持以下操作符：

* `element_exists`
* `element_not_exists`
* `text_equals`
* `text_contains`
* `activity_is`
* `wait_until_exists`
* `wait_until_disappear`
* `page_signature_match`

### 7.7.2 Page Contract

必须支持：

* `must_have`
* `one_of`
* `must_not_have`

### 7.7.3 断言分级

#### Strong Assertion

可直接作为 PASS/FAIL 依据，例如：

* activity_is
* element_exists
* text_equals

#### Weak Assertion

有参考价值，但不应单独决定最终结论，例如：

* 文本非空
* 大部分关键元素存在
* 页面大体匹配

#### Observational Check

只收集证据，不直接决定最终通过失败，例如：

* crash 关键词
* ANR 关键词
* 异常弹窗
* 页面跳转异常

### 7.7.4 Assertion Engine

必须负责：

* 解析 Assertion Spec
* 调用 Observe Tools
* 输出 assertion_results
* 汇总最终 verdict

### 7.7.5 Verdict Rule

必须实现以下规则：

1. 强断言全部通过 → `PASS`
2. 存在强断言失败 → `FAIL`
3. 用例模糊、断言不足、仅弱断言或观察型结果 → `NEEDS_REVIEW`

---

## 7.8 测试结果模型

### 7.8.1 Step Result

每步结果至少包含：

* step_id
* action_status
* observation_summary
* assertion_status
* artifacts

### 7.8.2 Case Result

每条 case 必须至少包含：

* case_id
* raw_case
* normalized_case
* ambiguities
* executability_score
* execution_mode
* final_status
* step_results
* assertion_results
* review_reasons
* artifacts
* summary

### 7.8.3 结果示例

```json id="w6x46w"
{
  "case_id": "login_smoke_001",
  "raw_case": "登录后看看首页是不是正常",
  "normalized_case": {
    "title": "登录后验证首页可达且关键元素存在"
  },
  "ambiguities": [
    "原始用例中的“正常”未明确定义"
  ],
  "executability_score": 0.78,
  "execution_mode": "semi_auto",
  "final_status": "NEEDS_REVIEW",
  "step_results": [],
  "assertion_results": [],
  "review_reasons": [
    "首页‘正常’无法完全强判定，已降级为人工复核"
  ],
  "artifacts": [],
  "summary": "核心检查通过，但仍建议人工复核页面完整性"
}
```

---

## 7.9 pytest 测试层

必须提供以下测试目录：

* `smoke/`
* `regression/`
* `stability/`
* `generated/`

必须至少实现以下样例：

* `test_app_launch.py`
* `test_login_smoke.py`
* `test_home_smoke.py`

其中，`test_login_smoke.py` 必须打通以下完整链路：

```text id="9m57ig"
原始模糊用例
→ 归一化
→ 歧义检测
→ 检查点提取
→ 执行计划生成
→ Skill 路由
→ MCP 调用
→ adb/uiautomator2 执行
→ Observe 收集
→ Assertion Engine
→ PASS/FAIL/NEEDS_REVIEW
→ 报告输出
```

---

## 7.10 产物与报告

必须输出以下产物目录：

* `artifacts/screenshots/`
* `artifacts/page_sources/`
* `artifacts/logs/`
* `artifacts/videos/`
* `artifacts/allure-results/`
* `artifacts/allure-report/`
* `artifacts/ai_reports/`

至少要能输出：

1. 一份结构化 JSON 执行结果
2. 一份 allure 测试结果
3. 一份 AI 辅助分析报告
4. 一份复核建议结果（针对 NEEDS_REVIEW）

---

## 7.11 CLI 能力

必须提供以下脚本：

* `run_case.py`
* `run_suite.py`
* `start_mcp_server.py`
* `prepare_device.py`
* `collect_logs.py`
* `export_report.py`

CLI 参考示例：

```bash id="yo7pzd"
python scripts/prepare_device.py
python scripts/start_mcp_server.py
python scripts/run_case.py --text "登录后看看首页是不是正常"
python scripts/run_case.py --case testcases/parsed_cases/login_cases.json
python scripts/run_suite.py --suite smoke
python scripts/export_report.py
```

---

## 8. 外部参考实现约束

本项目在 MCP 服务组织、移动端动作封装、设备交互方式、移动端 AI 自动化测试的工程结构上，可参考公开项目 **mobile-mcp** 的实现方向。该项目公开展示了面向移动端 UI 自动化的 MCP 思路，支持 Android / iOS，并包含较丰富的移动端动作、应用、断言等工具能力。 ([Gitee][2])

但是，**本项目不得与外部仓库形成强耦合依赖，不得要求运行时必须依赖该仓库源码，不得把本项目简单做成其镜像复制版。**

### 8.1 可以参考的内容

* 移动端 MCP 服务端组织方式
* 设备连接与动作封装思路
* 移动端动作能力映射为 MCP tool 的方式
* Python 下的工程化组织模式

### 8.2 不能直接照搬的内容

* 与本项目需求冲突的目录结构
* 缺少断言分层的实现
* 缺少模糊用例归一化的实现
* 缺少三态结果模型的实现
* 与本 PRD 不一致的默认业务假设

### 8.3 本项目必须新增和强化的内容

必须完整实现：

* raw_case_ingestor
* case_normalizer
* ambiguity_detector
* executability_scorer
* checkpoint_extractor
* Assertion DSL
* Assertion Engine
* PASS / FAIL / NEEDS_REVIEW 三态结果
* 结构化 AI 报告与复核包

---

## 9. 项目工程结构

Codex 必须严格生成以下目录结构：

```text id="4q495j"
mobile_ai_test_framework/
├── README.md
├── requirements.txt
├── pyproject.toml
├── pytest.ini
├── .env.example
├── .gitignore
├── .codex/
│   └── config.toml
│
├── configs/
│   ├── framework.yaml
│   ├── devices.yaml
│   ├── env_dev.yaml
│   ├── env_test.yaml
│   ├── env_prod_mock.yaml
│   └── logging.yaml
│
├── agent/
│   ├── __init__.py
│   ├── raw_case_ingestor.py
│   ├── case_normalizer.py
│   ├── ambiguity_detector.py
│   ├── executability_scorer.py
│   ├── checkpoint_extractor.py
│   ├── case_parser.py
│   ├── planner.py
│   ├── skill_router.py
│   ├── assertion_builder.py
│   ├── failure_analyzer.py
│   ├── report_writer.py
│   └── schemas/
│       ├── raw_case_schema.py
│       ├── normalized_case_schema.py
│       ├── plan_schema.py
│       ├── step_schema.py
│       ├── assertion_spec_schema.py
│       └── result_schema.py
│
├── skills/
│   ├── __init__.py
│   ├── base_skill.py
│   ├── common/
│   │   ├── login_skill.py
│   │   ├── logout_skill.py
│   │   ├── search_skill.py
│   │   └── popup_recover_skill.py
│   ├── pages/
│   │   ├── home_skill.py
│   │   ├── login_page_skill.py
│   │   ├── detail_page_skill.py
│   │   └── settings_page_skill.py
│   ├── domain/
│   │   ├── app_startup_skill.py
│   │   ├── account_flow_skill.py
│   │   ├── order_flow_skill.py
│   │   └── network_recover_skill.py
│   └── diagnose/
│       ├── ui_fail_diagnose_skill.py
│       ├── logcat_diagnose_skill.py
│       └── flaky_case_diagnose_skill.py
│
├── mcp_server/
│   ├── __init__.py
│   ├── server.py
│   ├── tool_registry.py
│   ├── tools_action/
│   │   ├── click_tool.py
│   │   ├── swipe_tool.py
│   │   ├── input_tool.py
│   │   ├── back_tool.py
│   │   ├── launch_app_tool.py
│   │   ├── stop_app_tool.py
│   │   └── wait_tool.py
│   ├── tools_observe/
│   │   ├── get_page_source_tool.py
│   │   ├── get_current_activity_tool.py
│   │   ├── element_exists_tool.py
│   │   ├── get_element_text_tool.py
│   │   ├── get_element_attrs_tool.py
│   │   ├── take_screenshot_tool.py
│   │   ├── get_logcat_tool.py
│   │   └── get_device_state_tool.py
│   ├── tools_assert/
│   │   ├── run_assertions_tool.py
│   │   ├── page_contract_assert_tool.py
│   │   ├── text_assert_tool.py
│   │   └── state_assert_tool.py
│   └── tools_artifact/
│       ├── collect_artifacts_tool.py
│       ├── screenrecord_tool.py
│       ├── export_report_tool.py
│       └── bundle_evidence_tool.py
│
├── core/
│   ├── __init__.py
│   ├── device/
│   │   ├── device_manager.py
│   │   ├── adb_client.py
│   │   ├── u2_client.py
│   │   ├── device_state.py
│   │   └── emulator_manager.py
│   ├── executor/
│   │   ├── action_executor.py
│   │   ├── observe_executor.py
│   │   ├── flow_executor.py
│   │   └── runner.py
│   ├── pages/
│   │   ├── base_page.py
│   │   ├── home_page.py
│   │   ├── login_page.py
│   │   ├── detail_page.py
│   │   └── settings_page.py
│   ├── flows/
│   │   ├── base_flow.py
│   │   ├── login_flow.py
│   │   ├── order_flow.py
│   │   └── recover_flow.py
│   └── utils/
│       ├── locator.py
│       ├── retry.py
│       ├── waiters.py
│       ├── time_util.py
│       └── json_util.py
│
├── assertions/
│   ├── __init__.py
│   ├── engine.py
│   ├── dsl/
│   │   ├── assertion_spec.py
│   │   ├── page_contract.py
│   │   └── matchers.py
│   ├── operators/
│   │   ├── element_exists.py
│   │   ├── element_not_exists.py
│   │   ├── text_equals.py
│   │   ├── text_contains.py
│   │   ├── activity_is.py
│   │   ├── wait_until_exists.py
│   │   ├── wait_until_disappear.py
│   │   └── page_signature_match.py
│   └── templates/
│       ├── page_arrival.json
│       ├── dialog_visible.json
│       ├── submit_success.json
│       └── login_success.json
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── smoke/
│   │   ├── test_app_launch.py
│   │   ├── test_login_smoke.py
│   │   └── test_home_smoke.py
│   ├── regression/
│   │   ├── test_login_regression.py
│   │   ├── test_order_regression.py
│   │   └── test_settings_regression.py
│   ├── stability/
│   │   ├── test_repeat_launch.py
│   │   ├── test_long_run.py
│   │   └── test_recover_after_crash.py
│   └── generated/
│       ├── test_generated_login.py
│       └── test_generated_search.py
│
├── testcases/
│   ├── manual_cases/
│   │   ├── raw_cases.txt
│   │   ├── login_cases.xlsx
│   │   ├── smoke_cases.xlsx
│   │   └── order_cases.xlsx
│   ├── parsed_cases/
│   │   ├── login_cases.json
│   │   └── smoke_cases.json
│   └── checkpoints/
│       ├── login_checkpoints.yaml
│       ├── home_checkpoints.yaml
│       └── order_checkpoints.yaml
│
├── data/
│   ├── accounts/
│   │   ├── test_accounts.yaml
│   │   └── invalid_accounts.yaml
│   ├── mock/
│   │   └── mock_payloads.json
│   └── seed/
│       └── seed_data.json
│
├── artifacts/
│   ├── screenshots/
│   ├── page_sources/
│   ├── logs/
│   ├── videos/
│   ├── allure-results/
│   ├── allure-report/
│   └── ai_reports/
│
├── scripts/
│   ├── run_case.py
│   ├── run_suite.py
│   ├── start_mcp_server.py
│   ├── prepare_device.py
│   ├── collect_logs.py
│   └── export_report.py
│
├── docs/
│   ├── architecture.md
│   ├── raw_case_strategy.md
│   ├── assertion_design.md
│   ├── skill_design.md
│   ├── mcp_tool_spec.md
│   └── onboarding.md
│
└── ci/
    ├── Jenkinsfile
    ├── gitlab-ci.yml
    └── docker/
        ├── Dockerfile
        └── entrypoint.sh
```

---

## 10. 关键数据结构

### 10.1 Raw Case

```json id="qry1bk"
{
  "case_id": "raw_001",
  "raw_text": "登录后看看首页是不是正常"
}
```

### 10.2 Normalized Case

```json id="4828lp"
{
  "case_id": "raw_001",
  "title": "登录后验证首页可达且关键元素存在",
  "preconditions": [
    "应用已安装",
    "存在可用测试账号"
  ],
  "steps": [
    "启动应用",
    "输入账号",
    "输入密码",
    "点击登录"
  ],
  "expected": [
    "进入首页",
    "首页关键元素存在",
    "无异常弹窗"
  ],
  "ambiguities": [
    "原始描述中“正常”含义不明确，已归一化为页面可达+关键元素存在+无异常弹窗"
  ]
}
```

### 10.3 Execution Plan

```json id="2h61x9"
{
  "case_id": "login_smoke_001",
  "title": "登录后验证首页可达且关键元素存在",
  "steps": [
    {
      "step_id": "step_1",
      "action": "launch_app",
      "skill": "app_startup_skill",
      "params": {
        "package": "com.demo.app"
      }
    },
    {
      "step_id": "step_2",
      "action": "login",
      "skill": "login_skill",
      "params": {
        "username": "test_user",
        "password": "123456"
      }
    }
  ],
  "assertions": [
    {
      "type": "activity_is",
      "level": "strong",
      "expected": "com.demo.MainActivity"
    },
    {
      "type": "page_signature_match",
      "level": "strong",
      "expected": {
        "must_have": [
          {"by": "id", "value": "home_tab"},
          {"by": "id", "value": "search_box"}
        ]
      }
    }
  ]
}
```

### 10.4 Assertion Result

```json id="xvqt1u"
{
  "assertion_type": "activity_is",
  "level": "strong",
  "expected": "com.demo.MainActivity",
  "actual": "com.demo.MainActivity",
  "passed": true,
  "evidence": {
    "activity": "com.demo.MainActivity"
  }
}
```

### 10.5 Case Result

```json id="1ri3qu"
{
  "case_id": "login_smoke_001",
  "raw_case": "登录后看看首页是不是正常",
  "normalized_case": {},
  "ambiguities": [],
  "executability_score": 0.78,
  "execution_mode": "semi_auto",
  "final_status": "NEEDS_REVIEW",
  "step_results": [],
  "assertion_results": [],
  "review_reasons": [
    "首页‘正常’缺乏完整可强判定标准"
  ],
  "artifacts": [],
  "summary": "登录成功，核心页面检查通过，但保留人工复核"
}
```

---

## 11. 技术要求

必须使用：

* Python 3.11+
* pytest
* uiautomator2
* adb
* allure-pytest
* pydantic 或 dataclasses
* PyYAML

代码要求：

* 类型注解
* 必要注释
* 异常处理
* 结构化日志
* 不得大量使用 `pass`
* 关键方法不得留空
* 核心模块不得只有类定义没有实现

---

## 12. 非功能要求

### 12.1 可运行性

项目生成后必须可安装、可运行、可调试。

### 12.2 可维护性

模块边界清晰，职责明确。

### 12.3 可扩展性

支持后续新增：

* Skill
* Tool
* Assertion Operator
* 用例类型

### 12.4 可调试性

关键路径必须有日志：

* 用例开始
* 归一化结果
* 计划生成
* Skill 路由
* MCP 调用
* 动作执行
* 观测结果
* 断言结果
* 失败原因

### 12.5 容错性

关键动作必须具备：

* timeout
* retry
* 异常捕获
* 恢复策略

---

## 13. MVP 必须打通的闭环

必须至少完整实现并打通下面这个闭环：

### 测试目标

```text id="7g8n7o"
登录后看看首页是不是正常
```

### 系统必须完成：

1. 读取原始用例
2. 归一化
3. 歧义检测
4. 提取检查点
5. 生成执行计划
6. 路由 `login_skill`
7. 通过 MCP 调用：

   * launch
   * input
   * click
   * observe
8. 通过 uiautomator2 完成执行
9. 获取：

   * activity
   * page source
   * screenshot
10. 执行 Assertion Engine
11. 输出：

* PASS / FAIL / NEEDS_REVIEW

12. 输出：

* JSON 结果
* allure 结果
* AI 辅助分析报告

---

## 14. README 必须包含的内容

README 至少必须说明：

1. 项目简介
2. 安装方式
3. 环境准备
4. Android 设备连接
5. adb 检查方式
6. uiautomator2 初始化
7. MCP Server 启动方式
8. 运行单 case 的方式
9. 运行 suite 的方式
10. 产物输出目录
11. 模糊用例如何被归一化
12. PASS / FAIL / NEEDS_REVIEW 的判定规则
13. 默认假设与限制说明

---

## 15. `.codex/config.toml` 要求

项目必须包含 `.codex/config.toml`。

该文件的目标是：

* 让 Codex 在当前仓库内稳定工作
* 明确这是 Python 项目
* 优先保守修改
* 优先一次性完整落地
* 优先运行项目内脚本进行验证
* 遇到小歧义时尽量采用合理默认值，而不是频繁打断

Codex 官方支持项目级 `.codex/config.toml`，并会在仓库内按目录层级加载项目配置。 ([OpenAI开发者][1])

---

## 16. 验收标准

只有同时满足以下条件，才算完成：

1. 完整目录结构生成完毕
2. 核心模块有实际实现
3. MCP Server 可启动
4. CLI 脚本可执行
5. smoke 用例可跑
6. 断言闭环完整
7. 模糊测试用例处理链路完整
8. 支持三态 verdict
9. 输出 JSON + allure + AI report
10. 文档完整
11. 没有要求“下次再补”
12. 没有把关键模块留空

---

## 17. 对 Codex 的强制执行要求

这部分最重要，必须严格遵守。

### 17.1 必须一次性完整实现

必须一次性完成整个项目实现。
不允许分阶段交付，不允许先给半成品再等待继续。

### 17.2 禁止中途停下确认

在实现过程中，禁止频繁中断询问：

* 是否继续
* 是否先做一部分
* 是否下一步再补

默认直接完整实现。

### 17.3 禁止只给骨架

不允许只输出：

* 空目录
* 空文件
* 占位类
* TODO 列表
* 伪代码

### 17.4 禁止关键路径留空

以下模块不得留空：

* `agent/raw_case_ingestor.py`
* `agent/case_normalizer.py`
* `agent/ambiguity_detector.py`
* `agent/executability_scorer.py`
* `agent/checkpoint_extractor.py`
* `agent/planner.py`
* `agent/assertion_builder.py`
* `mcp_server/server.py`
* `core/executor/action_executor.py`
* `core/executor/observe_executor.py`
* `assertions/engine.py`
* `tests/smoke/test_login_smoke.py`

### 17.5 优先保证闭环

如复杂度冲突，优先保证：

* 本地可运行
* 模糊用例可归一化
* 登录 smoke 闭环完整
* 三态结果可输出
* 报告可产出

### 17.6 遇到小歧义时默认策略

遇到小范围未明确需求时：

* 不要中断提问
* 采用合理默认值
* 在 README 中说明假设

---

## 18. 交付物清单

最终必须交付：

1. 完整项目代码
2. 完整目录结构
3. `.codex/config.toml`
4. `requirements.txt`
5. `pyproject.toml`
6. `pytest.ini`
7. `.env.example`
8. CLI 脚本
9. MCP Server
10. 模糊用例处理模块
11. Assertion DSL
12. Assertion Engine
13. smoke 样例
14. 文档
15. 示例测试数据
16. 结果输出目录

---
