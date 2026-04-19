from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.executor.runner import Runner
from core.utils.json_util import write_json


SUITES = {
    "smoke": [
        ("text", "启动应用后看看首页是不是正常"),
        ("text", "启动应用并检查首页"),
        ("file", "testcases/parsed_cases/smoke_cases.json"),
    ],
    "regression": [
        ("text", "启动应用后看看首页是不是正常"),
        ("text", "搜索功能试试"),
        ("text", "切后台再回来没问题"),
    ],
    "stability": [
        ("text", "启动应用并检查首页"),
        ("text", "启动应用并检查首页"),
        ("text", "切后台再回来没问题"),
    ],
}


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a named case suite")
    parser.add_argument("--suite", default="smoke", choices=sorted(SUITES))
    args = parser.parse_args()

    runner = Runner()
    results = []
    for kind, payload in SUITES[args.suite]:
        if kind == "text":
            results.append(runner.run_text_case(payload).model_dump(mode="json"))
        else:
            results.append(runner.run_case_file(payload).model_dump(mode="json"))
    output = Path("artifacts/logs") / f"suite_{args.suite}.json"
    write_json(output, {"suite": args.suite, "results": results})
    print(json.dumps({"suite": args.suite, "output": str(output), "count": len(results)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
