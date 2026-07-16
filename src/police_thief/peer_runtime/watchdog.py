"""Independent background monitor for the whole game loop (Sec. 8.4.2).

If no heartbeat is observed within `timeout_sec`, persists state and
performs a controlled shutdown instead of leaving a silent freeze.
"""

from __future__ import annotations

import json
import threading
import time
from pathlib import Path

_STATE_MARKER_PATH = Path("logs") / "watchdog_state.json"


def watchdog_check(last_heartbeat: float, timeout_sec: float = 180) -> str:
    elapsed = time.time() - last_heartbeat
    if elapsed > timeout_sec:
        persist_state()
        controlled_shutdown()
        return "SHUTDOWN"
    return "ALIVE"


class HeartbeatWatchdog:
    """Runs `watchdog_check` on a real background OS thread, not just
    another asyncio task sharing the main event loop -- Sec. 8.4.2 calls
    for "an independent background process," and a same-loop asyncio task
    would be starved by exactly the kind of CPU-bound freeze in the main
    coroutine it's meant to catch. `Orchestrator.run_game` calls
    `heartbeat()` after each turn and checks `triggered` at the top of the
    loop."""

    def __init__(self, timeout_sec: float, *, poll_interval_sec: float | None = None):
        self.timeout_sec = timeout_sec
        self.poll_interval_sec = poll_interval_sec or max(1.0, timeout_sec / 4)
        self.last_heartbeat = time.time()
        self.triggered = threading.Event()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def heartbeat(self) -> None:
        self.last_heartbeat = time.time()

    def start(self) -> None:
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=self.poll_interval_sec + 1)

    def _run(self) -> None:
        while not self._stop.is_set():
            if watchdog_check(self.last_heartbeat, self.timeout_sec) == "SHUTDOWN":
                self.triggered.set()
                return
            self._stop.wait(self.poll_interval_sec)


def persist_state(marker_path: Path = _STATE_MARKER_PATH) -> None:
    """Write a minimal, timestamped freeze marker so the run can be
    diagnosed after the fact. The Orchestrator owns the real game state;
    this module-level function only has the fact that a freeze occurred."""
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    marker_path.write_text(json.dumps({"frozen_at": time.time()}))


def controlled_shutdown() -> None:
    """Extension point for releasing MCP connections and closing logs. A
    no-op at this layer -- the Orchestrator, which actually holds those
    resources, is responsible for closing them when it observes SHUTDOWN."""
    return None
