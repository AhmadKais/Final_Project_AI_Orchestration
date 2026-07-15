"""Cryptographic replay/verification engine (Sec. 7.4-7.5).

Re-walks a saved game log, re-derives each Commit-Reveal hash via
domain.crypto.verify(), and renders a step-by-step "Verified OK" vs
"TAMPERED" (auto-disqualifying) result -- required for the README
screenshot at submission (Appendix C Table 6).
"""

from __future__ import annotations

from pathlib import Path


class ReplayViewer:
    def __init__(self, log_path: Path):
        self.log_path = log_path

    def load(self) -> list[dict]:
        raise NotImplementedError

    def verify_all(self) -> bool:
        """Return True iff every step's commit/reveal hash re-derives correctly."""
        raise NotImplementedError

    def step_through(self) -> None:
        """Interactive/visual step-by-step walk with a Verified OK / TAMPERED badge."""
        raise NotImplementedError
