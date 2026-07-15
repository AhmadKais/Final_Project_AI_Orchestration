"""Reference default policy: Bayesian belief map + Manhattan distance (Sec.
6.3.1, 6.4). Fully competitive with RL per the spec and requires no training.

Cop minimizes Manhattan distance to argmax_s belief(s); Robber maximizes it.
"""

from __future__ import annotations

from police_thief.domain.belief import BeliefMap
from police_thief.domain.board import Board, Coord, Move
from police_thief.domain.strategy.brain_base import BrainBase


class HeuristicBrain(BrainBase):
    def _pick_move(self, board: Board, own_pos: Coord, belief: BeliefMap) -> Move:
        raise NotImplementedError
