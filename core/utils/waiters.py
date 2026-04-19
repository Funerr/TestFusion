from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")


def wait_until(condition: Callable[[], T], timeout: float = 3.0, interval: float = 0.2) -> T:
    deadline = time.time() + timeout
    last_value: T | None = None
    while time.time() < deadline:
        last_value = condition()
        if last_value:
            return last_value
        time.sleep(interval)
    return last_value  # type: ignore[return-value]
