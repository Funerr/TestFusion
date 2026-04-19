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
    parser = argparse.ArgumentParser(description="Run a single case through the mobile AI test framework")
    parser.add_argument("--text", help="Raw natural language case text")
    parser.add_argument("--case", help="Path to a JSON/YAML/XLSX/TXT case file")
    parser.add_argument("--case-index", type=int, default=0, help="Index when the case file contains multiple cases")
    args = parser.parse_args()

    runner = Runner()
    if args.text:
        result = runner.run_text_case(args.text)
    elif args.case:
        source = Path(args.case)
        if source.suffix.lower() == ".txt":
            lines = [line.strip() for line in source.read_text(encoding="utf-8").splitlines() if line.strip()]
            result = runner.run_text_case(lines[args.case_index])
        else:
            result = runner.run_case_file(source, case_index=args.case_index)
    else:
        raise SystemExit("One of --text or --case is required")
    print(json.dumps(result.model_dump(mode="json"), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
