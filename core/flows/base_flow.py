from __future__ import annotations

from typing import Any


class BaseFlow:
    def __init__(self, server: Any):
        self.server = server
