"""Game-theoretic policy (Sec. 6.3's search track): upgrades
`HeuristicBrain`'s one-ply greedy distance move with a bounded-depth
minimax search (`domain/strategy/search.py`) that looks several moves
ahead and assumes a worst-case-competent opponent, averaged over the
belief map's top few candidate cells instead of a single point estimate.

Barrier placement stays on the inherited path-safe heuristic
(`_best_barrier_option`) -- it already avoids the self-trapping failure
mode -- but the choice between stepping and walling is now a genuine
value comparison via `search.score_barrier` rather than an unconditional
"always wall if a legal spot exists" rule.
"""

from __future__ import annotations

import time

from police_thief.domain.belief import BeliefMap
from police_thief.domain.board import Board, Coord, Move
from police_thief.domain.strategy import search
from police_thief.domain.strategy.heuristic_brain import HeuristicBrain

_SEARCH_DEPTH = 4
_BELIEF_CANDIDATES = 3
# Generous relative to actual measured cost (sub-millisecond at the default
# depth) and small relative to the real per-turn network deadline (30s) --
# this is a safety net against slower grading hardware or a future depth
# increase, not a budget the search is expected to spend routinely.
_TIME_BUDGET_SECONDS = 2.0


class MinimaxBrain(HeuristicBrain):
    def _pick_move(self, board: Board, own_pos: Coord, belief: BeliefMap) -> Move:
        # `exclude=own_pos`: a belief candidate equal to the mover's own
        # current cell is a contradiction, not just an unlikely guess --
        # Board.is_capture() (checked on REAL positions right after every
        # turn's moves are applied) would already have ended the game if
        # that were true. Feeding that impossible hypothesis into the
        # search made its root-level capture check fire for free on STAY
        # whenever a stale scent trail happened to make the mover's own
        # cell the belief's argmax (see BeliefMap.arg_max's docstring).
        candidates = belief.top_k(_BELIEF_CANDIDATES, exclude=own_pos)
        deadline = time.monotonic() + _TIME_BUDGET_SECONDS
        scored = search.score_moves(self.role, board, own_pos, candidates, depth=_SEARCH_DEPTH, deadline=deadline)
        if scored is None:
            # The search didn't finish within budget -- fall back to the
            # always-fast, always-legal greedy parent rather than delay
            # this turn's commit and risk the OPPONENT's own response
            # timeout, which starts counting from when our commit arrives.
            return super()._pick_move(board, own_pos, belief)
        best = max(scored, key=scored.get)

        if self.role == "police":
            barrier_target = self._best_barrier_option(board, own_pos, belief)
            if barrier_target is not None:
                barrier_value = search.score_barrier(
                    board, own_pos, barrier_target, candidates, depth=_SEARCH_DEPTH, deadline=deadline
                )
                if barrier_value is not None and barrier_value >= scored[best]:
                    return Move.STAY

        return best
