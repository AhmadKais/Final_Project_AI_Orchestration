"""Independent background monitor for the whole game loop (Sec. 8.4.2).

If no heartbeat is observed within `timeout_sec`, persists state and
performs a controlled shutdown instead of leaving a silent freeze.
"""

from __future__ import annotations

import time


def watchdog_check(last_heartbeat: float, timeout_sec: float = 180) -> str:
    elapsed = time.time() - last_heartbeat
    if elapsed > timeout_sec:
        persist_state()
        controlled_shutdown()
        return "SHUTDOWN"
    return "ALIVE"


def persist_state() -> None:
    raise NotImplementedError


def controlled_shutdown() -> None:
    raise NotImplementedError
