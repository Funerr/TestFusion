from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.executor.runner import Runner


def main() -> None:
    runner = Runner()
    payload = {
        "devices": runner.device_manager.discover_devices(),
        "prepare": runner.device_manager.prepare(),
        "health": runner.device_manager.check_health(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
