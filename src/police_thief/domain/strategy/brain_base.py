"""Abstract base class for a movement policy (Sec. 6.2-6.3).

Subclass this to build your own "brain". Override `_pick_move` (both roles)
and `_decide_barrier` (Cop only, called when `_pick_move` returns STAY and
a barrier placement is being considered).
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from police_thief.domain.belief import BeliefMap
from police_thief.domain.board import Board, Coord, Move


class BrainBase(ABC):
    """Connects to PeerRuntime between hint-decode and Commit-pack (Fig. 7)."""

    def __init__(self, role: str):
        self.role = role

    @abstractmethod
    def _pick_move(self, board: Board, own_pos: Coord, belief: BeliefMap) -> Move:
        """Choose this turn's legal move. Must never return an illegal move;
        PeerRuntime will reject it and force a technical loss if it does."""
        raise NotImplementedError

    def _decide_barrier(self, board: Board, cop_pos: Coord, belief: BeliefMap) -> Coord | None:
        """Cop-only: optionally choose a cell (self or orthogonally adjacent)
        to seal instead of moving. Return None to skip placing a barrier."""
        return None

    def pick_move(self, board: Board, own_pos: Coord, belief: BeliefMap) -> Move:
        """Public entry point used by PeerRuntime; wraps `_pick_move` with
        legality validation."""
        move = self._pick_move(board, own_pos, belief)
        if not board.is_legal_move(own_pos, move):
            raise ValueError(
                f"{type(self).__name__}._pick_move returned illegal move "
                f"{move!r} from {own_pos}"
            )
        return move
