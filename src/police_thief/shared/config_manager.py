"""Loads and merges the shared signed config (config/game.json) with the
private per-role config (config/<role>/game.toml).

Per Appendix B: shared JSON values always override matching TOML keys, so
the private file can never weaken a signed condition. Both peers must load
byte-for-byte identical JSON; config_sha256() is what gets cryptographically
locked before a series (Sec. 5.5, Appendix F rule 1).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

Role = Literal["police", "thief"]


@dataclass(frozen=True)
class GameConfig:
    """Merged, read-only view of shared + private config for one role."""

    role: Role
    values: dict[str, Any]

    def __getitem__(self, key: str) -> Any:
        return self.values[key]


def load_shared_config(path: Path) -> dict[str, Any]:
    """Load config/game.json. Raises if the file is missing or malformed."""
    raise NotImplementedError


def load_private_config(path: Path) -> dict[str, Any]:
    """Load config/<role>/game.toml."""
    raise NotImplementedError


def merge(shared: dict[str, Any], private: dict[str, Any]) -> dict[str, Any]:
    """Overlay: shared JSON keys win over private TOML keys."""
    raise NotImplementedError


def config_sha256(shared: dict[str, Any]) -> str:
    """Canonical (sorted-keys, fixed-separator) SHA-256 of the shared config,
    used to prove both peers agreed on identical game physics (Sec. 5.5)."""
    raise NotImplementedError


def load_game_config(role: Role, config_root: Path) -> GameConfig:
    """Convenience entry point: load + merge + return a GameConfig for `role`."""
    raise NotImplementedError
