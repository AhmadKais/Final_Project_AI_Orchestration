"""Commit-Reveal protocol over SHA-256 (Sec. 5.3).

H_commit = SHA256(State || Move || Intent || Nonce), canonical JSON
(sorted keys, fixed separators) so both peers hash byte-identical input.
Four stages: Commit -> Acknowledge -> Reveal -> (end-of-game) Audit. The
Nonce stays secret until the final audit to defeat dictionary attacks.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass


@dataclass(frozen=True)
class Commitment:
    h_commit: str
    nonce: str


def _canonical_payload(state: str, move: str, intent: str, nonce: str) -> bytes:
    """Canonical JSON (sorted keys, fixed separators) so both peers hash
    byte-identical input regardless of dict ordering (Sec. 5.3)."""
    return json.dumps(
        {"state": state, "move": move, "intent": intent, "nonce": nonce},
        sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")


def commit(state: str, move: str, intent: str) -> Commitment:
    """Generate a nonce, hash (state, move, intent, nonce) canonically, and
    return the commitment. Only h_commit is transmitted; nonce stays secret."""
    nonce = secrets.token_hex(16)
    h_commit = hashlib.sha256(_canonical_payload(state, move, intent, nonce)).hexdigest()
    return Commitment(h_commit=h_commit, nonce=nonce)


def verify(state: str, move: str, intent: str, nonce: str, h_commit: str) -> bool:
    """Recompute the hash from revealed fields and compare via constant-time
    comparison (secrets.compare_digest) against the original commitment."""
    recomputed = hashlib.sha256(_canonical_payload(state, move, intent, nonce)).hexdigest()
    return secrets.compare_digest(recomputed, h_commit)


def audit_log(entries: list[dict]) -> list[tuple[int, bool]]:
    """Re-verify every committed step in a full game log at end-of-game.
    Returns (step_index, is_valid) pairs; any False triggers a technical loss
    (Appendix E rule 19). Each entry must carry step/state/move/intent/nonce/
    h_commit -- the same fields revealed at the Final Audit stage (Sec. 5.3.2)."""
    results = []
    for entry in entries:
        is_valid = verify(
            entry["state"], entry["move"], entry["intent"],
            entry["nonce"], entry["h_commit"],
        )
        results.append((entry["step"], is_valid))
    return results
