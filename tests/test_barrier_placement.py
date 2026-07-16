"""HeuristicBrain's barrier-placement tactic and mobility-aware evasion
(Sec. 3.4's spatial-engineering advantage, wired into the strategy module)."""

import pytest

from police_thief.domain.belief import BeliefMap
from police_thief.domain.board import Board, Move
from police_thief.domain.strategy.brain_base import BrainBase
from police_thief.domain.strategy.heuristic_brain import HeuristicBrain


def known_target_belief(grid_size, target):
    return BeliefMap(grid_size=grid_size, probabilities={target: 1.0})


def make_board(cop_pos=(0, 0), thief_pos=(6, 6), grid_size=7, max_barriers=14):
    return Board(grid_size=grid_size, cop_pos=cop_pos, thief_pos=thief_pos, max_barriers=max_barriers)


# -- _best_barrier_option / _decide_barrier ---------------------------------

def test_no_barrier_when_far_from_target():
    board = make_board(cop_pos=(0, 0))
    belief = known_target_belief(7, target=(6, 6))  # distance 12, way out of tactical range
    brain = HeuristicBrain(role="police")

    assert brain._decide_barrier(board, board.cop_pos, belief) is None


def test_no_barrier_when_adjacent_to_target():
    # Distance 1: moving onto (or next to) the target directly is always at
    # least as good as staying to wall it off -- never worth a detour.
    board = make_board(cop_pos=(3, 2))
    belief = known_target_belief(7, target=(3, 3))
    brain = HeuristicBrain(role="police")

    assert brain._decide_barrier(board, board.cop_pos, belief) is None


def test_no_barrier_when_already_on_target():
    board = make_board(cop_pos=(3, 3))
    belief = known_target_belief(7, target=(3, 3))
    brain = HeuristicBrain(role="police")

    assert brain._decide_barrier(board, board.cop_pos, belief) is None


def test_barrier_offered_within_tactical_range_seals_an_escape_route():
    # Diagonal offset (not axis-aligned): the Cop has two independent
    # improving directions (SOUTH and EAST both reduce distance), so
    # sealing one of the target's escape routes still leaves the other
    # open -- a genuinely safe, useful placement.
    board = make_board(cop_pos=(2, 2))
    belief = known_target_belief(7, target=(3, 3))  # distance 2
    brain = HeuristicBrain(role="police")

    barrier = brain._decide_barrier(board, board.cop_pos, belief)

    assert barrier is not None
    # Must be one of the target's own orthogonal neighbors -- an actual
    # escape route, not an arbitrary cell.
    row_dist = abs(barrier[0] - 3) + abs(barrier[1] - 3)
    assert row_dist == 1


def test_barrier_never_seals_the_cops_own_only_route_forward():
    # Axis-aligned (same row): the direct path east is the Cop's ONLY
    # improving move. Sealing it would trap the Cop behind its own wall
    # (Sec. 3.4's explicit warning) -- must not be offered.
    board = make_board(cop_pos=(3, 1))
    belief = known_target_belief(7, target=(3, 3))  # distance 2
    brain = HeuristicBrain(role="police")

    assert brain._decide_barrier(board, board.cop_pos, belief) is None


def test_barrier_option_respects_the_quota():
    board = make_board(cop_pos=(2, 2), max_barriers=0)
    belief = known_target_belief(7, target=(3, 3))
    brain = HeuristicBrain(role="police")

    assert brain._decide_barrier(board, board.cop_pos, belief) is None


def test_robber_brain_never_offers_a_barrier():
    board = make_board(thief_pos=(3, 1))
    belief = known_target_belief(7, target=(3, 3))
    brain = HeuristicBrain(role="thief")

    assert brain._decide_barrier(board, board.thief_pos, belief) is None


def test_pick_move_returns_stay_when_a_barrier_is_the_better_play():
    board = make_board(cop_pos=(2, 2))  # diagonal offset -- a safe barrier exists
    belief = known_target_belief(7, target=(3, 3))
    brain = HeuristicBrain(role="police")

    move = brain.pick_move(board, board.cop_pos, belief)

    assert move == Move.STAY


# -- decide_barrier legality wrapper (BrainBase) ----------------------------

class _RogueBarrierBrain(BrainBase):
    def _pick_move(self, board, own_pos, belief):
        return Move.STAY

    def _decide_barrier(self, board, cop_pos, belief):
        return (0, 0)  # not adjacent to cop_pos=(3,3) below


def test_decide_barrier_rejects_illegal_target_from_subclass():
    board = make_board(cop_pos=(3, 3))
    belief = known_target_belief(7, target=(3, 3))
    brain = _RogueBarrierBrain(role="police")

    with pytest.raises(ValueError):
        brain.decide_barrier(board, board.cop_pos, belief)


def test_decide_barrier_passes_through_none():
    board = make_board(cop_pos=(0, 0))
    belief = known_target_belief(7, target=(6, 6))
    brain = HeuristicBrain(role="police")

    assert brain.decide_barrier(board, board.cop_pos, belief) is None


# -- Robber mobility-aware evasion tie-break --------------------------------

def test_thief_prefers_the_move_that_keeps_more_escape_routes_open():
    # Thief at (1, 1), cop believed at (0, 0): SOUTH -> (2,1) and
    # EAST -> (1,2) both increase distance from (0,0) equally (to 3), so
    # this is a genuine tie on the primary criterion. Barriers box in
    # (2,1) far more than (1,2) (2 legal follow-up moves vs. 4) -- only
    # the mobility tie-break can distinguish them.
    board = make_board(thief_pos=(1, 1))
    board.barriers.update({(0, 1), (1, 0), (2, 0), (3, 1), (2, 2)})
    belief = known_target_belief(7, target=(0, 0))
    brain = HeuristicBrain(role="thief")

    move = brain.pick_move(board, board.thief_pos, belief)

    assert move == Move.EAST
