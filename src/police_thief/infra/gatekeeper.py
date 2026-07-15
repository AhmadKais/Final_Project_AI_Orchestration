"""Gatekeeper pattern: three cumulative protection gates in front of the
Gmail API (Sec. 9.3.1-9.3.2) -- Quota Manager -> Token Bucket -> DOS Detector.

NOTE: these are rate-tokens for load regulation, unrelated to LLM tokens
or OAuth tokens (see the terminology box in Sec. 9.3.1).
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class QuotaManager:
    """Daily operation counter; blocks once the daily safety threshold is hit."""

    daily_limit: int
    _count: int = 0

    def allow(self) -> bool:
        raise NotImplementedError


@dataclass
class TokenBucket:
    """tokens <- min(C, tokens + r*dt); allow iff tokens >= 1 (Sec. 9.3.2)."""

    capacity: float
    refill_rate: float
    tokens: float = 0.0
    last: float = 0.0

    def __post_init__(self) -> None:
        self.tokens = self.capacity
        self.last = time.monotonic()

    def _refill(self) -> None:
        raise NotImplementedError

    def allow(self, cost: float = 1.0) -> bool:
        raise NotImplementedError


class DOSDetector:
    """Flags anomalous send patterns (e.g. an infinite-loop bug) and locks
    the whole pipeline (circuit breaker) to protect the account."""

    def check(self, recent_send_timestamps: list[float]) -> bool:
        raise NotImplementedError


class Gatekeeper:
    """Composes QuotaManager -> TokenBucket -> DOSDetector in front of
    infra.email_sender.send_report (Fig. 13)."""

    def __init__(self, quota: QuotaManager, bucket: TokenBucket, dos: DOSDetector):
        self.quota = quota
        self.bucket = bucket
        self.dos = dos

    def try_send(self, send_fn, *args, **kwargs):
        raise NotImplementedError
