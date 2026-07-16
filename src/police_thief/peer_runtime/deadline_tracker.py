"""Per-request timeout tracking (Sec. 8.4.1).

Every FastMCP request carries a Timestamp + Expiry Deadline. A missed
deadline is a failure, not an invitation to keep waiting -- triggers a
controlled Retry or a technical-loss declaration, never an indefinite wait.
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class DeadlineTracker:
    timeout_sec: float
    started_at: float = 0.0

    def start(self) -> None:
        self.started_at = time.monotonic()

    def is_expired(self) -> bool:
        return (time.monotonic() - self.started_at) > self.timeout_sec

    def remaining(self) -> float:
        return max(0.0, self.timeout_sec - (time.monotonic() - self.started_at))
