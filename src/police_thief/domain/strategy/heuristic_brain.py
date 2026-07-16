"""Reference default policy: Bayesian belief map + Manhattan distance (Sec.
6.3.1, 6.4). Fully competitive with RL per the spec and requires no training.

Cop: minimizes Manhattan distance to argmax_s belief(s) -- unless within
tactical range, where sealing off one of the target's escape routes
(spatial engineering, Sec. 3.4) is worth more than one step of pursuit.
Robber: maximizes that same distance, tie-broken by which resulting cell
keeps the most future escape routes open (a one-ply lookahead against
walking itself into a dead end).
"""

from __future__ import annotations

from police_thief.domain.belief import BeliefMap
from police_thief.domain.board import Board, Coord, Move
from police_thief.domain.strategy.brain_base import BrainBase

_DIRECTIONAL_MOVES = (Move.NORTH, Move.SOUTH, Move.EAST, Move.WEST)

# Only consider sealing an escape route in this distance window: farther
# out, a barrier is a bet on a guess that's had less time to firm up and
# wastes a step of pursuit; at distance <= 1, moving onto (or next to) the
# target directly is always at least as good as staying to wall it off.
_BARRIER_MIN_RANGE = 2
_BARRIER_MAX_RANGE = 3


class HeuristicBrain(BrainBase):
    def _best_barrier_option(self, board: Board, cop_pos: Coord, belief: BeliefMap) -> Coord | None:
        """A legal placement (the Cop's own cell or one orthogonally
        adjacent) that is also orthogonally adjacent to the believed
        target -- i.e. one of the target's own escape routes -- or None if
        no such placement exists, the quota is exhausted, or the target
        isn't close enough for a barrier to be worth more than a step of
        pursuit."""
        if self.role != "police" or len(board.barriers) >= board.max_barriers:
            return None

        target = belief.arg_max(exclude=cop_pos)
        distance = belief.manhattan_distance(cop_pos, target)
        if not (_BARRIER_MIN_RANGE <= distance <= _BARRIER_MAX_RANGE):
            return None

        target_escape_routes = {board.destination(target, m) for m in _DIRECTIONAL_MOVES}
        candidates = [cop_pos] + [board.destination(cop_pos, m) for m in _DIRECTIONAL_MOVES]
        for cell in candidates:
            if cell == target or not board.in_bounds(cell) or cell in board.barriers:
                continue
            if cell in target_escape_routes and self._leaves_a_path_forward(board, cop_pos, target, cell):
                return cell
        return None

    def _leaves_a_path_forward(self, board: Board, cop_pos: Coord, target: Coord, candidate: Coord) -> bool:
        """True iff, after placing a barrier at `candidate`, the Cop still
        has at least one legal move that strictly reduces its distance to
        the target -- i.e. this placement doesn't wall off its own only
        route forward. The spec warns about exactly this failure mode
        (Sec. 3.4): "a barrier placed greedily can trap the Cop itself
        behind a wall it built." When the Cop is axis-aligned with the
        target, the direct route is usually its only improving move, so
        sealing that same cell would strand it in place forever.
        """
        current_distance = abs(cop_pos[0] - target[0]) + abs(cop_pos[1] - target[1])
        for move in _DIRECTIONAL_MOVES:
            dest = board.destination(cop_pos, move)
            if dest == candidate or not board.in_bounds(dest) or dest in board.barriers:
                continue
            if abs(dest[0] - target[0]) + abs(dest[1] - target[1]) < current_distance:
                return True
        return False

    def _pick_move(self, board: Board, own_pos: Coord, belief: BeliefMap) -> Move:
        if self.role == "police" and self._best_barrier_option(board, own_pos, belief) is not None:
            return Move.STAY  # forgo movement this turn to seal an escape route instead

        target = belief.arg_max(exclude=own_pos)
        legal = board.legal_moves(own_pos)

        if self.role == "police":
            return min(legal, key=lambda m: belief.manhattan_distance(board.destination(own_pos, m), target))

        def evasion_key(move: Move) -> tuple[int, int]:
            dest = board.destination(own_pos, move)
            distance = belief.manhattan_distance(dest, target)
            mobility = len(board.legal_moves(dest))  # avoid backing into a dead end
            return (distance, mobility)

        return max(legal, key=evasion_key)

    def _decide_barrier(self, board: Board, cop_pos: Coord, belief: BeliefMap) -> Coord | None:
        return self._best_barrier_option(board, cop_pos, belief)
