"""Single business entry point (Appendix D): wires config -> Orchestrator ->
interface for one role, and exposes the replay/verification entry point.

This is the only module `__main__.py` should import from directly.
"""

from __future__ import annotations

from pathlib import Path

from police_thief.peer_runtime.orchestrator import Orchestrator
from police_thief.shared.config_manager import GameConfig, Role, load_game_config


def build_peer(role: Role, config_root: Path = Path("config")) -> Orchestrator:
    """Load config, construct the brain (from [strategy] or HeuristicBrain
    default), and assemble a ready-to-run Orchestrator for this role."""
    raise NotImplementedError


def run_peer(role: Role, config_root: Path = Path("config")) -> None:
    raise NotImplementedError


def run_replay(log_path: Path) -> None:
    """Launch the replay viewer against a saved game log for cryptographic
    re-verification (Sec. 7.4-7.5)."""
    raise NotImplementedError
