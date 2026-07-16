"""Cryptographic replay/verification engine (Sec. 7.4-7.5).

Re-walks a saved game log, re-derives each Commit-Reveal hash via
domain.crypto.verify(), and renders a step-by-step "Verified OK" vs
"TAMPERED" (auto-disqualifying) result -- required for the README
screenshot at submission (Appendix C Table 6).
"""

from __future__ import annotations

import json
from pathlib import Path

from police_thief.domain.crypto import verify


class ReplayViewer:
    def __init__(self, log_path: Path):
        self.log_path = Path(log_path)

    def load(self) -> list[dict]:
        """Load the log file. Accepts either a bare JSON list of step
        entries, or a {"entries": [...]} wrapper (the shape the log file
        variable in Appendix F Table 20 uses)."""
        with open(self.log_path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data = data.get("entries", [])
        if not isinstance(data, list):
            raise ValueError(f"{self.log_path}: expected a list of log entries")
        return data

    def _verify_entry(self, entry: dict) -> bool:
        return verify(entry["state"], entry["move"], entry["intent"], entry["nonce"], entry["h_commit"])

    def verify_all(self) -> bool:
        """Return True iff every step's commit/reveal hash re-derives correctly."""
        return all(self._verify_entry(entry) for entry in self.load())

    def step_through(self) -> None:
        """Print a step-by-step Verified OK / TAMPERED walkthrough (Sec.
        7.4-7.5) -- the CLI form of the "retrospective witness"; a
        graphical wrapper can layer over this same verification logic
        without duplicating it."""
        for entry in self.load():
            status = "Verified OK" if self._verify_entry(entry) else "TAMPERED"
            print(f"step {entry['step']}: {entry['role']} {entry['move']} -- {status}")
