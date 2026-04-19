from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.executor.runner import Runner


def main() -> None:
    # MCP hosts may omit or override cwd; framework paths are repo-relative.
    os.chdir(ROOT)
    parser = argparse.ArgumentParser(description="Start the mobile AI test framework MCP server")
    parser.add_argument("--stdio", action="store_true", help="Run as a standard MCP stdio server")
    parser.add_argument("--http", action="store_true", help="Expose the registry over HTTP for local debugging")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    runner = Runner()
    if args.http and not args.stdio:
        runner.server.serve_http(host=args.host, port=args.port)
        return
    runner.server.serve_stdio()


if __name__ == "__main__":
    main()
