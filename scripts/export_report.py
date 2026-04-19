from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.executor.runner import Runner


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the aggregated artifact summary")
    parser.add_argument("--destination", default="artifacts/logs/export_summary.json")
    args = parser.parse_args()

    runner = Runner()
    path = runner.export_report(args.destination)
    print(json.dumps({"path": path}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
