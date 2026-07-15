"""The discrete grid, coordinates, movement legality, and barrier placement
(Sec. 3.2-3.4).

No diagonals. A Cop turn that forgoes movement may place a barrier on its
own cell or an orthogonally adjacent cell; barriers are irreversible. A
barrier placed on the Robber's current cell is a capture (Appendix E rule 46).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Move(str, Enum):
    NORTH = "N"
    SOUTH = "S"
    EAST = "E"
    WEST = "W"
    STAY = "STAY"


Coord = tuple[int, int]

# Top-left origin, 0-indexed, row grows downward (spec Sec. 3.3).
_MOVE_DELTAS: dict[Move, Coord] = {
    Move.NORTH: (-1, 0),
    Move.SOUTH: (1, 0),
    Move.EAST: (0, 1),
    Move.WEST: (0, -1),
    Move.STAY: (0, 0),
}

# Directional (non-STAY) moves -- used for the "no legal move whatsoever"
# trapped-Robber capture check (Sec. 3.4). STAY never counts as an escape.
_DIRECTIONAL_MOVES: tuple[Move, ...] = (Move.NORTH, Move.SOUTH, Move.EAST, Move.WEST)

_ROLE_TO_ATTR = {"police": "cop_pos", "thief": "thief_pos"}


@dataclass
class Board:
    """Mutable board state: size, barrier set, and both agents' positions."""

    grid_size: int
    cop_pos: Coord
    thief_pos: Coord
    barriers: set[Coord] = field(default_factory=set)
    max_barriers: int = 14

    def in_bounds(self, cell: Coord) -> bool:
        row, col = cell
        return 0 <= row < self.grid_size and 0 <= col < self.grid_size

    def destination(self, pos: Coord, move: Move) -> Coord:
        """The cell `pos` lands on after `move`, ignoring legality."""
        d_row, d_col = _MOVE_DELTAS[move]
        row, col = pos
        return (row + d_row, col + d_col)

    def is_legal_move(self, pos: Coord, move: Move) -> bool:
        """Reject diagonals (impossible by construction -- only orthogonal
        deltas exist), off-board moves, and moves into a barrier."""
        target = self.destination(pos, move)
        return self.in_bounds(target) and target not in self.barriers

    def legal_moves(self, pos: Coord) -> list[Move]:
        """All actions -- including STAY -- legal from `pos` right now."""
        return [move for move in Move if self.is_legal_move(pos, move)]

    def apply_move(self, role: str, move: Move) -> Coord:
        """Return the new position for `role` ("police"/"thief") after `move`."""
        if role not in _ROLE_TO_ATTR:
            raise ValueError(f"Unknown role: {role!r} (expected 'police' or 'thief')")
        attr = _ROLE_TO_ATTR[role]
        pos = getattr(self, attr)
        if not self.is_legal_move(pos, move):
            raise ValueError(f"Illegal move {move!r} from {pos} for role {role!r}")
        new_pos = self.destination(pos, move)
        setattr(self, attr, new_pos)
        return new_pos

    def place_barrier(self, cop_pos: Coord, target: Coord) -> None:
        """Validate target is self-cell or orthogonally adjacent, then seal it."""
        if not self.in_bounds(target):
            raise ValueError(f"Barrier target {target} is off-board")
        row_dist = abs(target[0] - cop_pos[0])
        col_dist = abs(target[1] - cop_pos[1])
        if row_dist + col_dist > 1:
            raise ValueError(
                f"Barrier target {target} is not the Cop's own cell or "
                f"orthogonally adjacent to {cop_pos}"
            )
        if target in self.barriers:
            raise ValueError(f"Cell {target} is already barriered")
        if len(self.barriers) >= self.max_barriers:
            raise ValueError(f"Barrier quota exhausted ({self.max_barriers})")
        self.barriers.add(target)

    def is_capture(self) -> bool:
        """True if the Cop's cell == the Robber's cell, a barrier has landed
        on the Robber (barriers are irreversible, so checking membership is
        equivalent to checking "just landed"), or the Robber has zero
        directional moves left (STAY doesn't count as an escape)."""
        if self.cop_pos == self.thief_pos:
            return True
        if self.thief_pos in self.barriers:
            return True
        if not any(self.is_legal_move(self.thief_pos, m) for m in _DIRECTIONAL_MOVES):
            return True
        return False
