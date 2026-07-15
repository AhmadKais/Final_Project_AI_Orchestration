"""Single-gateway Orchestrator (Sec. 8.3, Fig. 12).

Owns the GamePhaseMachine, the MCP connector (infra.mcp_client/mcp_server),
the decision module (domain.strategy.BrainBase), the log manager, the
DeadlineTracker, and the Watchdog. No peripheral module talks to another
directly -- everything is coordinated through this class.
"""

from __future__ import annotations

from dataclasses import dataclass

from police_thief.domain.strategy.brain_base import BrainBase
from police_thief.peer_runtime.deadline_tracker import DeadlineTracker
from police_thief.peer_runtime.state_machine import GamePhaseMachine


@dataclass
class Orchestrator:
    role: str
    brain: BrainBase
    phase: GamePhaseMachine
    deadline: DeadlineTracker

    async def run_turn(self) -> None:
        """Drive one full turn through WAITING_FOR_OPPONENT -> ... -> VERIFYING."""
        raise NotImplementedError

    async def run_game(self) -> None:
        """Loop run_turn() until capture, survival, or technical loss."""
        raise NotImplementedError
