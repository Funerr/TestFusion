from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from mcp_server.mobile_toolkit import MobileToolKit


def register(registry, services):
    toolkit = services.setdefault("mobile_toolkit", MobileToolKit(services))

    registry.register(
        "click",
        "action",
        "Legacy compatibility: click by locator.",
        lambda locator: toolkit.action_executor.execute("click", {"locator": locator}),
        visible=False,
    )
    registry.register(
        "swipe",
        "action",
        "Legacy compatibility: swipe.",
        lambda direction="up", distance=0.5: toolkit.action_executor.execute(
            "swipe", {"direction": direction, "distance": distance}
        ),
        visible=False,
    )
    registry.register(
        "input_text",
        "action",
        "Legacy compatibility: input text by locator.",
        lambda locator, text: toolkit.action_executor.execute("input_text", {"locator": locator, "text": text}),
        visible=False,
    )
    registry.register(
        "back",
        "action",
        "Legacy compatibility: press back.",
        lambda: toolkit.action_executor.execute("back", {}),
        visible=False,
    )
    registry.register(
        "launch_app",
        "action",
        "Legacy compatibility: launch app.",
        lambda package=None, activity=None: toolkit.launch_app(package=package, activity=activity),
        visible=False,
    )
    registry.register(
        "stop_app",
        "action",
        "Legacy compatibility: stop app.",
        lambda package=None: toolkit.terminate_app(package=package),
        visible=False,
    )
    registry.register(
        "wait",
        "action",
        "Legacy compatibility: wait.",
        lambda seconds=0.2: toolkit.wait(seconds),
        visible=False,
    )

    registry.register(
        "get_page_source",
        "observe",
        "Legacy compatibility: page source.",
        lambda case_id=None, save=False, path=None: toolkit.get_page_source(case_id=case_id, save=save, path=path),
        visible=False,
    )
    registry.register(
        "get_current_activity",
        "observe",
        "Legacy compatibility: current activity.",
        lambda: toolkit.get_current_activity(),
        visible=False,
    )
    registry.register(
        "element_exists",
        "observe",
        "Legacy compatibility: element exists.",
        lambda locator: toolkit.element_exists(locator),
        visible=False,
    )
    registry.register(
        "get_element_text",
        "observe",
        "Legacy compatibility: element text.",
        lambda locator: toolkit.get_element_text(locator),
        visible=False,
    )
    registry.register(
        "get_element_attrs",
        "observe",
        "Legacy compatibility: element attrs.",
        lambda locator: toolkit.get_element_attrs(locator),
        visible=False,
    )
    registry.register(
        "take_screenshot",
        "observe",
        "Legacy compatibility: take screenshot.",
        lambda case_id=None, path=None: toolkit.take_screenshot(case_id=case_id, path=path),
        visible=False,
    )
    registry.register(
        "get_logcat",
        "observe",
        "Legacy compatibility: logcat.",
        lambda case_id=None, save=False, path=None: toolkit.get_logcat(case_id=case_id, save=save, path=path),
        visible=False,
    )
    registry.register(
        "get_device_state",
        "observe",
        "Legacy compatibility: device state.",
        lambda: toolkit.get_device_state(),
        visible=False,
    )

    registry.register(
        "run_assertions",
        "assert",
        "Legacy compatibility: run assertions.",
        lambda assertions, context=None: toolkit.run_assertions(assertions, context=context),
        visible=False,
    )
    registry.register(
        "page_contract_assert",
        "assert",
        "Legacy compatibility: page contract assertion.",
        lambda contract, description="Page contract assertion", level="strong": toolkit.assert_page_contract(
            contract,
            description=description,
            level=level,
        ),
        visible=False,
    )
    registry.register(
        "text_assert",
        "assert",
        "Legacy compatibility: text assertion.",
        lambda locator, expected, operator="text_equals", description="Text assertion", level="strong": toolkit.assert_text_spec(
            locator,
            expected,
            operator=operator,
            description=description,
            level=level,
        ),
        visible=False,
    )
    registry.register(
        "state_assert",
        "assert",
        "Legacy compatibility: state assertion.",
        lambda expected_activity, description="State assertion", level="strong": toolkit.assert_state(
            expected_activity,
            description=description,
            level=level,
        ),
        visible=False,
    )

    registry.register(
        "collect_artifacts",
        "artifact",
        "Legacy compatibility: collect artifacts.",
        lambda case_id: toolkit.collect_artifacts(case_id),
        visible=False,
    )
    registry.register(
        "screenrecord",
        "artifact",
        "Legacy compatibility: write mock screenrecord.",
        lambda case_id: {"path": services["report_writer"].write_screenrecord(case_id)},
        visible=False,
    )
    registry.register(
        "export_report",
        "artifact",
        "Legacy compatibility: export report.",
        lambda destination="artifacts/logs/export_summary.json": toolkit.export_report(destination),
        visible=False,
    )
    registry.register(
        "bundle_evidence",
        "artifact",
        "Legacy compatibility: bundle evidence.",
        lambda case_id, artifacts, summary="": toolkit.bundle_evidence(case_id, artifacts, summary=summary),
        visible=False,
    )
