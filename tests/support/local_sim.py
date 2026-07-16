"""Local (non-networked) full-game simulator + adversary brains, used to
statistically evaluate move-strategy quality directly -- bypassing the
commit-reveal/MCP transport layer, which is already covered end-to-end by
`test_orchestrator_integration.py`. Mirrors `Orchestrator.run_turn`'s exact
per-turn sequence (both moves resolved against the same pre-turn board
snapshot, then apply-move, then barrier, then capture check, then
scent-emit -> scent-decay -> belief-decay -> belief-update-from-scent) so
results generalize to real play.

Hints are intentionally left empty: `update_from_hint("")` is a no-op, so
belief only ever evolves from the (unforgeable) scent trail here -- the
bluff/hint channel is a separate concern already covered by the LLM/
trash-talk tests and would only add noise to a strategy comparison.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from police_thief.domain.belief import BeliefMap
from police_thief.domain.board import Board, Coord, Move
from police_thief.domain.rules import GameOutcome, determine_outcome
from police_thief.domain.scent import ScentField
from police_thief.domain.strategy.brain_base import BrainBase

# Mirrors config/game.json's binding defaults (Appendix F).
GRID_SIZE = 7
COP_START: Coord = (0, 0)
THIEF_START: Coord = (3, 3)
MAX_BARRIERS = 14
MAX_MOVES = 35
SURVIVAL_THRESHOLD = 35
PHEROMONE_CENTER_INTENSITY = 0.9
PHEROMONE_DECAY = 0.10
PHEROMONE_GRID_SIZE = 5
BELIEF_FORGET_RATE = 0.4  # mirrors Orchestrator's own default (see its docstring)


class RandomBrain(BrainBase):
    """Rock-bottom baseline: a uniformly random legal move, never a barrier."""

    def __init__(self, role: str, rng: random.Random | None = None):
        super().__init__(role)
        self._rng = rng or random.Random()

    def _pick_move(self, board: Board, own_pos: Coord, belief: BeliefMap) -> Move:
        return self._rng.choice(board.legal_moves(own_pos))


class GreedyBrain(BrainBase):
    """Reproduces the lecturer-provided reference simulator's shipped
    baseline (rmisegal/Game-P2P-Cop-Chase, `domain/brains.py`): one-ply
    greedy Manhattan distance to `belief.arg_max()`, no lookahead. Police
    walls the cell it would have stepped into instead of moving, 15% of
    the time (the reference's `PoliceBrain.barrier_chance`). This is a
    realistic opponent archetype -- the repo is an explicitly-endorsed
    "learning aid" students may read, extend, or start from."""

    barrier_chance = 0.15

    def __init__(self, role: str, rng: random.Random | None = None):
        super().__init__(role)
        self._rng = rng or random.Random()
        self._pending_barrier_target: Coord | None = None

    def _pick_move(self, board: Board, own_pos: Coord, belief: BeliefMap) -> Move:
        target = belief.arg_max()
        legal = board.legal_moves(own_pos)

        if self.role != "police":
            return max(legal, key=lambda m: belief.manhattan_distance(board.destination(own_pos, m), target))

        best = min(legal, key=lambda m: belief.manhattan_distance(board.destination(own_pos, m), target))
        self._pending_barrier_target = None
        if best != Move.STAY and len(board.barriers) < board.max_barriers and self._rng.random() < self.barrier_chance:
            dest = board.destination(own_pos, best)
            if dest not in board.barriers:
                self._pending_barrier_target = dest
                return Move.STAY
        return best

    def _decide_barrier(self, board: Board, cop_pos: Coord, belief: BeliefMap) -> Coord | None:
        return self._pending_barrier_target


@dataclass
class GameResult:
    outcome: GameOutcome
    steps_taken: int
    winner: str  # "police", "thief", or "technical_loss"


def play_game(
    police_brain: BrainBase, thief_brain: BrainBase, *,
    cop_start: Coord = COP_START, thief_start: Coord = THIEF_START,
    grid_size: int = GRID_SIZE, max_barriers: int = MAX_BARRIERS,
    max_moves: int = MAX_MOVES, survival_threshold: int = SURVIVAL_THRESHOLD,
    belief_forget_rate: float = BELIEF_FORGET_RATE,
) -> GameResult:
    board = Board(grid_size=grid_size, cop_pos=cop_start, thief_pos=thief_start, max_barriers=max_barriers)

    # Each side independently tracks the OTHER's scent + belief, exactly as
    # two separate Orchestrator instances would.
    police_view_of_thief_scent = ScentField(grid_size=grid_size)
    police_belief = BeliefMap(grid_size=grid_size)
    thief_view_of_cop_scent = ScentField(grid_size=grid_size)
    thief_belief = BeliefMap(grid_size=grid_size)

    step = 0
    while True:
        cop_move = police_brain.pick_move(board, board.cop_pos, police_belief)
        thief_move = thief_brain.pick_move(board, board.thief_pos, thief_belief)

        barrier_target = None
        if cop_move == Move.STAY:
            barrier_target = police_brain.decide_barrier(board, board.cop_pos, police_belief)

        board.apply_move("police", cop_move)
        board.apply_move("thief", thief_move)
        if barrier_target is not None:
            board.place_barrier(board.cop_pos, barrier_target)

        if board.is_capture():
            outcome = determine_outcome(
                steps_taken=step + 1, max_moves=max_moves, captured=True,
                survival_threshold=survival_threshold, forgery_detected=False,
            )
            return GameResult(outcome=outcome, steps_taken=step + 1, winner="police")

        police_view_of_thief_scent.emit(center=board.thief_pos, peak=PHEROMONE_CENTER_INTENSITY, field_size=PHEROMONE_GRID_SIZE)
        police_view_of_thief_scent.decay(PHEROMONE_DECAY)
        police_belief.decay_toward_uniform(belief_forget_rate)
        police_belief.update_from_scent(police_view_of_thief_scent)

        thief_view_of_cop_scent.emit(center=board.cop_pos, peak=PHEROMONE_CENTER_INTENSITY, field_size=PHEROMONE_GRID_SIZE)
        thief_view_of_cop_scent.decay(PHEROMONE_DECAY)
        thief_belief.decay_toward_uniform(belief_forget_rate)
        thief_belief.update_from_scent(thief_view_of_cop_scent)

        step += 1
        if step >= max_moves or step >= survival_threshold:
            outcome = determine_outcome(
                steps_taken=step, max_moves=max_moves, captured=False,
                survival_threshold=survival_threshold, forgery_detected=False,
            )
            return GameResult(outcome=outcome, steps_taken=step, winner="thief")
