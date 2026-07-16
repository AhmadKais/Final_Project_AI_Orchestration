"""Independent background monitor for the whole game loop (Sec. 8.4.2).

If no heartbeat is observed within `timeout_sec`, persists state and
performs a controlled shutdown instead of leaving a silent freeze.
"""

from __future__ import annotations

import json
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
