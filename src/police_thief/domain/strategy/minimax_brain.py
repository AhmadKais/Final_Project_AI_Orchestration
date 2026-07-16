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

Tie-breaking among near-equal moves is randomized per instance (see
`_TIE_BREAK_JITTER`): two byte-identical copies of this brain facing each
other compute perfectly correlated responses every turn, which a real
mirror-match trace showed can lock into a stable adjacent-cell standoff
neither side's deterministic tie-break ever resolves -- a known failure
mode of pure-strategy play in symmetric simultaneous games. Independent
per-instance jitter breaks the correlation; real classmate opponents won't
run identical code regardless, so this is a worst-case hardening, not the
common case.

`_SEARCH_DEPTH=4`, not deeper: a controlled sweep (4/5/6/7 against
GreedyBrain, everything else held fixed) found depth >= 5 collapses win
rate from ~93% to ~33% on THIS project's board size -- not a gradual
decline, an immediate cliff, and reproduced with a live trace: at depth 6
the Cop found every approach angle toward an unmoving, cornered target
scored within a few hundredths of STAY and chose to freeze for 26 straight
turns. That's genuine minimax worst-case pessimism, not a bug -- assuming
a perfectly optimal adversary for many more plies makes EVERY option look
equally futile ("a truly optimal evader could dodge any of these anyway"),
which is exactly backwards against GreedyBrain, which isn't remotely
optimal. Depth 4 keeps enough lookahead to fix the simultaneous-move
correctness issue above without searching deep enough to talk itself into
that paranoia. If a future change (a deadline-bounded iterative-deepening
scheme, or an opponent-strength-aware evaluation) revisits this, re-run
that same sweep before trusting a "deeper is better" instinct here.
"""

from __future__ import annotations

import random
import time

from police_thief.domain.belief import BeliefMap
from police_thief.domain.board import Board, Coord, Move
from police_thief.domain.strategy import search
from police_thief.domain.strategy.heuristic_brain import HeuristicBrain

_SEARCH_DEPTH = 4
_BELIEF_CANDIDATES = 3
# Generous relative to actual measured cost (single-digit ms at this
# depth) and small relative to the real per-turn network deadline (30s) --
# a safety net against slower grading hardware, not a budget the search is
# expected to spend routinely.
_TIME_BUDGET_SECONDS = 5.0
# Small enough to never override a genuine value gap (evaluate() moves in
# whole distance units; captures are worth +1000) -- only nudges among
# moves that are otherwise exactly or near-exactly tied. A larger value
# (1.0) was tried to more reliably break the mirror-match standoff above,
# but a controlled test showed it measurably override real, non-tied move
# preferences against GreedyBrain -- not worth trading real-opponent
# quality for a marginal improvement on an opponent (an identical copy of
# this same brain) that essentially never occurs in real play.
_TIE_BREAK_JITTER = 0.05


class MinimaxBrain(HeuristicBrain):
    def __init__(self, role: str, rng: random.Random | None = None):
        super().__init__(role)
        self._rng = rng or random.Random()

    def _pick_move(self, board: Board, own_pos: Coord, belief: BeliefMap) -> Move:
        # Exclude both the mover's own cell AND every barriered cell: both
        # are physically impossible current-opponent-position hypotheses
        # (see BeliefMap.arg_max's docstring). The barrier case is the more
        # damaging of the two in practice -- belief evolves purely from
        # scent, which has no idea a cell it once favored later got walled
        # off, so a stale-but-still-weighty candidate can sit on a barrier
        # indefinitely. A real trace showed this alone worth ~750 points to
        # a "retreat" move against an ~715-point ACTUAL capture opportunity
        # once that phantom candidate's weight got averaged in.
        excluded = frozenset(board.barriers) | {own_pos}
        candidates = belief.top_k(_BELIEF_CANDIDATES, exclude=excluded)
        deadline = time.monotonic() + _TIME_BUDGET_SECONDS
        scored = search.score_moves(self.role, board, own_pos, candidates, depth=_SEARCH_DEPTH, deadline=deadline)
        if scored is None:
            # The search didn't finish within budget -- fall back to the
            # always-fast, always-legal greedy parent rather than delay
            # this turn's commit and risk the OPPONENT's own response
            # timeout, which starts counting from when our commit arrives.
            return super()._pick_move(board, own_pos, belief)
        jittered = {move: value + self._rng.uniform(-_TIE_BREAK_JITTER, _TIE_BREAK_JITTER) for move, value in scored.items()}
        best = max(jittered, key=jittered.get)

        if self.role == "police":
            barrier_target = self._best_barrier_option(board, own_pos, belief)
            if barrier_target is not None:
                barrier_value = search.score_barrier(
                    board, own_pos, barrier_target, candidates, depth=_SEARCH_DEPTH, deadline=deadline
                )
                # Compared against the UNjittered move score -- move-vs-
                # barrier is a real value decision, not a near-tie to nudge.
                if barrier_value is not None and barrier_value >= scored[best]:
                    return Move.STAY

        return best
