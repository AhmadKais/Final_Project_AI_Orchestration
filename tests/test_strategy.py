"""Stage 3 (Blind Strategy Module): full-information Manhattan-distance
movement, with no scent/belief uncertainty -- the target is simply known.
"""

import pytest

from police_thief.domain.belief import BeliefMap
from police_thief.domain.board import Board, Move
from police_thief.domain.strategy.brain_base import BrainBase
from police_thief.domain.strategy.heuristic_brain import HeuristicBrain


def known_target_belief(grid_size: int, target) -> BeliefMap:
    """A belief map with 100% certainty on one cell -- the "blind"/full-info
    mode this stage's acceptance criterion describes (no uncertainty yet)."""
    return BeliefMap(grid_size=grid_size, probabilities={target: 1.0})


def make_board(cop_pos=(0, 0), thief_pos=(6, 6), grid_size=7) -> Board:
    return Board(grid_size=grid_size, cop_pos=cop_pos, thief_pos=thief_pos)


# -- BeliefMap utility methods --------------------------------------------

def test_arg_max_returns_highest_probability_cell():
    belief = BeliefMap(grid_size=7, probabilities={(1, 1): 0.2, (5, 5): 0.9, (0, 0): 0.1})
    assert belief.arg_max() == (5, 5)


def test_arg_max_on_empty_map_initializes_uniform_prior():
    # Turn 0 has no evidence yet, but the brain still needs a target to aim
    # at -- arg_max must not raise (Stage 8's Orchestrator calls pick_move
    # before any scent/hint update has ever run).
    belief = BeliefMap(grid_size=7)
    target = belief.arg_max()
    assert target in [(r, c) for r in range(7) for c in range(7)]
    assert len(set(belief.probabilities.values())) == 1  # uniform


def test_manhattan_distance():
    belief = BeliefMap(grid_size=7)
    assert belief.manhattan_distance((0, 0), (3, 4)) == 7
    assert belief.manhattan_distance((2, 2), (2, 2)) == 0


# -- HeuristicBrain: Cop minimizes distance --------------------------------

def test_cop_moves_toward_known_target():
    board = make_board(cop_pos=(2, 2))
    belief = known_target_belief(7, target=(5, 5))
    brain = HeuristicBrain(role="police")

    move = brain.pick_move(board, board.cop_pos, belief)

    assert move in (Move.SOUTH, Move.EAST)  # either reduces distance by 1


def test_cop_stays_when_already_on_target():
    board = make_board(cop_pos=(3, 3))
    belief = known_target_belief(7, target=(3, 3))
    brain = HeuristicBrain(role="police")

    move = brain.pick_move(board, board.cop_pos, belief)

    assert move == Move.STAY


# -- HeuristicBrain: Robber maximizes distance (evasion) -------------------

def test_thief_moves_away_from_known_target():
    board = make_board(thief_pos=(3, 3))
    belief = known_target_belief(7, target=(0, 0))  # the (believed) Cop location
    brain = HeuristicBrain(role="thief")

    move = brain.pick_move(board, board.thief_pos, belief)

    assert move in (Move.SOUTH, Move.EAST)  # either increases distance from (0,0)


def test_thief_respects_barriers_when_evading():
    board = make_board(thief_pos=(3, 3))
    board.barriers.update({(4, 3), (2, 3), (3, 4), (3, 2)})  # boxed in
    belief = known_target_belief(7, target=(0, 0))
    brain = HeuristicBrain(role="thief")

    move = brain.pick_move(board, board.thief_pos, belief)

    assert move == Move.STAY  # only legal option left


# -- BrainBase legality wrapper --------------------------------------------

class _RogueBrain(BrainBase):
    """A misbehaving brain that always returns an illegal move, to prove
    the base class's legality wrapper actually catches it (Sec. 6.2: a
    brain must never be able to force an illegal move through)."""

    def _pick_move(self, board, own_pos, belief):
        return Move.NORTH  # illegal from (0, 0): off-board


def test_pick_move_rejects_illegal_move_from_subclass():
    board = make_board(cop_pos=(0, 0))
    belief = known_target_belief(7, target=(5, 5))
    brain = _RogueBrain(role="police")

    with pytest.raises(ValueError):
        brain.pick_move(board, board.cop_pos, belief)


# -- Acceptance criterion: shortest path with no manual intervention -------

def test_cop_reaches_known_target_via_repeated_pick_move_with_no_manual_help():
    board = make_board(cop_pos=(0, 0))
    target = (4, 3)
    belief = known_target_belief(7, target=target)
    brain = HeuristicBrain(role="police")

    steps = 0
    max_steps = 20
    while board.cop_pos != target and steps < max_steps:
        move = brain.pick_move(board, board.cop_pos, belief)
        board.apply_move("police", move)
        steps += 1

    assert board.cop_pos == target
    assert steps == belief.manhattan_distance((0, 0), target)  # shortest path, no wasted steps
