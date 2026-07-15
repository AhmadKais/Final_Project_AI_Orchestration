"""Board legality: no diagonals, barrier placement radius, capture detection."""

import pytest

from police_thief.domain.board import Board, Move


def make_board(**overrides) -> Board:
    defaults = dict(grid_size=7, cop_pos=(0, 0), thief_pos=(3, 3), max_barriers=14)
    defaults.update(overrides)
    return Board(**defaults)


# -- movement legality --------------------------------------------------

def test_diagonal_move_is_illegal():
    # Move only defines N/S/E/W/STAY -- there is no diagonal enum member,
    # so "illegal" is enforced by construction. Assert that invariant holds.
    assert {m.value for m in Move} == {"N", "S", "E", "W", "STAY"}


@pytest.mark.parametrize(
    "move,expected",
    [
        (Move.NORTH, (2, 3)),
        (Move.SOUTH, (4, 3)),
        (Move.EAST, (3, 4)),
        (Move.WEST, (3, 2)),
        (Move.STAY, (3, 3)),
    ],
)
def test_orthogonal_move_destination(move, expected):
    board = make_board()
    assert board.destination((3, 3), move) == expected


def test_move_off_board_is_illegal():
    board = make_board(cop_pos=(0, 0), thief_pos=(3, 3))
    assert board.is_legal_move((0, 0), Move.NORTH) is False
    assert board.is_legal_move((0, 0), Move.WEST) is False


def test_move_into_barrier_is_illegal():
    board = make_board()
    board.barriers.add((2, 3))
    assert board.is_legal_move((3, 3), Move.NORTH) is False


def test_apply_move_updates_position():
    board = make_board()
    new_pos = board.apply_move("thief", Move.NORTH)
    assert new_pos == (2, 3)
    assert board.thief_pos == (2, 3)


def test_apply_illegal_move_raises():
    board = make_board(cop_pos=(0, 0))
    with pytest.raises(ValueError):
        board.apply_move("police", Move.NORTH)


def test_apply_move_unknown_role_raises():
    board = make_board()
    with pytest.raises(ValueError):
        board.apply_move("referee", Move.STAY)


def test_legal_moves_always_includes_stay():
    board = make_board(cop_pos=(0, 0))
    assert Move.STAY in board.legal_moves((0, 0))


# -- barrier placement ----------------------------------------------------

def test_barrier_on_own_cell_is_legal():
    board = make_board(cop_pos=(1, 1))
    board.place_barrier((1, 1), (1, 1))
    assert (1, 1) in board.barriers


def test_barrier_on_adjacent_cell_is_legal():
    board = make_board(cop_pos=(1, 1))
    board.place_barrier((1, 1), (1, 2))
    assert (1, 2) in board.barriers


def test_barrier_beyond_adjacency_is_rejected():
    board = make_board(cop_pos=(1, 1))
    with pytest.raises(ValueError):
        board.place_barrier((1, 1), (3, 3))


def test_barrier_off_board_is_rejected():
    board = make_board(cop_pos=(0, 0))
    with pytest.raises(ValueError):
        board.place_barrier((0, 0), (-1, 0))


def test_barrier_quota_is_enforced():
    board = make_board(cop_pos=(0, 0), max_barriers=1)
    board.place_barrier((0, 0), (0, 0))
    with pytest.raises(ValueError):
        board.place_barrier((0, 0), (0, 1))


def test_duplicate_barrier_is_rejected():
    board = make_board(cop_pos=(0, 0))
    board.place_barrier((0, 0), (0, 1))
    with pytest.raises(ValueError):
        board.place_barrier((0, 0), (0, 1))


# -- capture detection ------------------------------------------------------

def test_coordinate_overlap_is_capture():
    board = make_board(cop_pos=(3, 3), thief_pos=(3, 3))
    assert board.is_capture() is True


def test_no_overlap_is_not_capture():
    board = make_board(cop_pos=(0, 0), thief_pos=(3, 3))
    assert board.is_capture() is False


def test_barrier_on_thief_cell_is_capture():
    board = make_board(cop_pos=(3, 2), thief_pos=(3, 3))
    board.place_barrier((3, 2), (3, 3))
    assert board.is_capture() is True


def test_trapped_thief_with_no_directional_move_is_capture():
    # Thief boxed in on all four sides by barriers; STAY must not count
    # as an escape (spec Sec. 3.4: "no legal move whatsoever").
    board = make_board(cop_pos=(0, 0), thief_pos=(3, 3), max_barriers=14)
    for target in [(2, 3), (4, 3), (3, 2), (3, 4)]:
        board.place_barrier((3, 3), target)
    assert board.is_capture() is True


def test_thief_with_stay_only_is_not_falsely_free():
    # Sanity check: legal_moves still reports STAY even when trapped,
    # but is_capture must not be fooled by that.
    board = make_board(cop_pos=(0, 0), thief_pos=(3, 3))
    for target in [(2, 3), (4, 3), (3, 2), (3, 4)]:
        board.place_barrier((3, 3), target)
    assert board.legal_moves((3, 3)) == [Move.STAY]
    assert board.is_capture() is True
