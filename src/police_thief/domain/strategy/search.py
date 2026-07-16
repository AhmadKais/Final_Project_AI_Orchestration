"""Bounded-depth minimax search over move sequences (Sec. 6.3's game-theory
track), used to look several moves ahead instead of greedily
minimizing/maximizing distance to a single-point belief estimate.

The opponent is modeled as a worst-case-competent adversary (minimax, not a
weak/fixed model), so the resulting move is robust against any opponent
strategy rather than tuned to one guess about how they play. Since the true
opponent position is hidden, the search is repeated over the belief map's
most probable cells (`BeliefMap.top_k`) and averaged by their probability --
an expectation over the search's own uncertainty about the world it's
searching in.

Barriers are treated as static within the lookahead horizon: only the
top-level decision (`score_barrier`) adds one, matching how rarely a Cop
places more than one barrier within a handful of turns. Barriers block
BOTH sides symmetrically (`Board.is_legal_move` doesn't distinguish role),
so distance/area here use one shared blocked-cell set for both.

The REAL turn is simultaneous (Sec. 5.3's Commit-Reveal: both sides commit
blind, then reveal together) -- neither side ever sees the other's this-turn
move before choosing its own. `score_moves`/`score_barrier` model that ply
correctly: for each of my candidate moves, they take the WORST case over
every move the opponent could simultaneously make (a maximin over the real
move matrix), not "the opponent reacts after seeing what I just did."
Getting this wrong at the CURRENT decision is what let two mirrored copies
of this brain fall into a perpetual oscillation around an adjacent cell --
each one's search assumed the other could always dodge its exact approach,
so directly closing in was never worth more than staying at a "safe"
distance, and neither ever actually committed to the capture. Only the root
ply gets this exact treatment; `_minimax`'s deeper continuation still uses
the cheaper alternating approximation, which is a standard, reasonable
trade-off -- errors several plies out matter far less than getting the
move actually being played right now correct.

`deadline` (a `time.monotonic()` timestamp) is optional but recommended: it
bounds worst-case search time regardless of board size, opponent-candidate
count, or the grading machine's own speed (Step-0 explicitly acknowledges
hardware varies team to team) -- a slow move decision doesn't just cost
time, it eats into the turn round-trip the OPPONENT's own response timeout
is bounded by. On expiry, every entry point here returns `None` instead of
a partial/best-effort guess, so the caller (`MinimaxBrain`) always knows to
fall back rather than silently act on an incomplete search.
"""

from __future__ import annotations

import time
from collections import deque

from police_thief.domain.board import Board, Coord, Move

_NEG_INF = float("-inf")
_POS_INF = float("inf")
_CAPTURE_VALUE = 1_000.0
_CAPTURE_SPEED_BONUS = 1.0  # per ply of remaining depth left unconsumed
# A wide sweep (0.0-0.15) against multiple opponent archetypes showed
# outcomes essentially flat across this whole range -- reachable area is a
# genuinely secondary signal here, not a lever worth over-tuning. Kept
# small and non-zero so it still breaks ties between equal-distance moves
# toward the more open one.
_AREA_WEIGHT = 0.05
_UNREACHABLE_DISTANCE = 64  # > any real path on a board this size; a barrier wall, not a bug

_DELTAS: tuple[Coord, ...] = ((-1, 0), (1, 0), (0, 1), (0, -1), (0, 0))
_DIRECTIONAL_DELTAS: tuple[Coord, ...] = ((-1, 0), (1, 0), (0, 1), (0, -1))


def _legal_dests(grid_size: int, barriers: frozenset[Coord], pos: Coord) -> list[Coord]:
    row, col = pos
    out = []
    for d_row, d_col in _DELTAS:
        cell = (row + d_row, col + d_col)
        if 0 <= cell[0] < grid_size and 0 <= cell[1] < grid_size and cell not in barriers:
            out.append(cell)
    return out


def _is_captured(cop_pos: Coord, thief_pos: Coord, barriers: frozenset[Coord], grid_size: int) -> bool:
    if cop_pos == thief_pos or thief_pos in barriers:
        return True
    row, col = thief_pos
    for d_row, d_col in _DIRECTIONAL_DELTAS:
        cell = (row + d_row, col + d_col)
        if 0 <= cell[0] < grid_size and 0 <= cell[1] < grid_size and cell not in barriers:
            return False
    return True


def _bfs_distance(grid_size: int, barriers: frozenset[Coord], start: Coord, goal: Coord) -> int:
    """Shortest walkable-path distance (barriers block, same as real legal
    moves), not raw Manhattan distance -- with up to 14 barriers on a 7x7
    board, the straight-line estimate can be badly wrong exactly when it
    matters most (late game, once the Cop has walled off several cells).
    Returns `_UNREACHABLE_DISTANCE` if no path exists (barriers can, in
    principle, fully partition the board)."""
    if start == goal:
        return 0
    visited = {start}
    queue = deque([(start, 0)])
    while queue:
        pos, dist = queue.popleft()
        row, col = pos
        for d_row, d_col in _DIRECTIONAL_DELTAS:
            cell = (row + d_row, col + d_col)
            if not (0 <= cell[0] < grid_size and 0 <= cell[1] < grid_size) or cell in barriers or cell in visited:
                continue
            if cell == goal:
                return dist + 1
            visited.add(cell)
            queue.append((cell, dist + 1))
    return _UNREACHABLE_DISTANCE


def _reachable_area(grid_size: int, barriers: frozenset[Coord], start: Coord) -> int:
    """Count of cells reachable from `start` (including itself) -- a
    flood-fill "how boxed in am I" signal that a 1-step legal-move count
    can't see: two cells can have the identical number of immediate
    neighbors while one sits in a 20-cell open region and the other in a
    3-cell pocket a Cop has nearly sealed."""
    visited = {start}
    queue = deque([start])
    while queue:
        pos = queue.popleft()
        row, col = pos
        for d_row, d_col in _DIRECTIONAL_DELTAS:
            cell = (row + d_row, col + d_col)
            if 0 <= cell[0] < grid_size and 0 <= cell[1] < grid_size and cell not in barriers and cell not in visited:
                visited.add(cell)
                queue.append(cell)
    return len(visited)


def _evaluate(cop_pos: Coord, thief_pos: Coord, barriers: frozenset[Coord], grid_size: int) -> float:
    """Cop-perspective non-terminal leaf value: higher is better for the
    Cop, lower (more negative) is better for the Thief -- a strict
    zero-sum framing. Only ever called on a NOT-yet-captured state --
    `_minimax` handles capture itself, since it (unlike this function)
    knows how much search depth is left, needed to prefer a sooner
    capture over an equally "certain" later one."""
    distance = _bfs_distance(grid_size, barriers, cop_pos, thief_pos)
    area = _reachable_area(grid_size, barriers, thief_pos)
    return -distance - _AREA_WEIGHT * area


def _ordered_dests(dests: list[Coord], target: Coord, prefer_closer: bool) -> list[Coord]:
    """Try the most promising destinations first, so alpha-beta prunes more
    of the tree: the Cop-to-move branch wants to close in on `target`
    (prefer_closer=True), the Thief-to-move branch wants to open distance
    from it (False). Manhattan distance is intentionally used here, not the
    BFS distance `_evaluate` uses -- this only reorders exploration, it
    never decides a value, so the fast approximation is the right trade."""
    key = lambda cell: abs(cell[0] - target[0]) + abs(cell[1] - target[1])  # noqa: E731
    return sorted(dests, key=key, reverse=not prefer_closer)


def _minimax(
    cop_pos: Coord, thief_pos: Coord, barriers: frozenset[Coord], grid_size: int,
    depth: int, cop_to_move: bool, alpha: float, beta: float, deadline: float | None,
) -> float | None:
    if deadline is not None and time.monotonic() > deadline:
        return None
    if _is_captured(cop_pos, thief_pos, barriers, grid_size):
        # A capture reached with more depth left unconsumed happened
        # SOONER in real turns -- reward it strictly over an equally
        # "certain" capture found deeper in the tree. Without this, every
        # capture scores an identical flat _CAPTURE_VALUE, so the search
        # can be functionally indifferent between capturing THIS turn and
        # capturing three turns from now (or worse, prefer stalling on
        # sub-point floating-point noise from an unrelated branch) --
        # which is exactly backwards: a bird in hand beats a "guaranteed"
        # one that depends on several more turns of the opponent
        # continuing to play into the model's own adversarial assumption.
        return _CAPTURE_VALUE + _CAPTURE_SPEED_BONUS * depth
    if depth == 0:
        return _evaluate(cop_pos, thief_pos, barriers, grid_size)

    if cop_to_move:
        best = _NEG_INF
        dests = _ordered_dests(_legal_dests(grid_size, barriers, cop_pos), thief_pos, prefer_closer=True)
        for dest in dests:
            value = _minimax(dest, thief_pos, barriers, grid_size, depth - 1, False, alpha, beta, deadline)
            if value is None:
                return None
            best = max(best, value)
            alpha = max(alpha, best)
            if alpha >= beta:
                break
        return best

    best = _POS_INF
    dests = _ordered_dests(_legal_dests(grid_size, barriers, thief_pos), cop_pos, prefer_closer=False)
    for dest in dests:
        value = _minimax(cop_pos, dest, barriers, grid_size, depth - 1, True, alpha, beta, deadline)
        if value is None:
            return None
        best = min(best, value)
        beta = min(beta, best)
        if alpha >= beta:
            break
    return best


def _worst_simultaneous_continuation(
    my_dest: Coord, opp_dests: list[Coord], barriers: frozenset[Coord], grid_size: int,
    continuation_depth: int, cop_role: bool, deadline: float | None,
) -> float | None:
    """Given MY resolved destination and every destination the opponent
    could simultaneously (blindly) choose from their believed current
    cell, the worst-case continuation value for ME across all of them --
    correct maximin for a one-shot simultaneous game, in place of assuming
    the opponent could react to my exact choice. `continuation_depth` plies
    after this one use the cheaper alternating `_minimax` approximation,
    resuming with me to move again (both sides already moved this round)."""
    worst = None
    for opp_dest in opp_dests:
        cop_pos, thief_pos = (my_dest, opp_dest) if cop_role else (opp_dest, my_dest)
        value = _minimax(
            cop_pos, thief_pos, barriers, grid_size, continuation_depth, cop_role, _NEG_INF, _POS_INF, deadline
        )
        if value is None:
            return None
        # `value` is always in Cop-perspective units. The opponent picks
        # whichever of ITS moves is worst for me: low if I'm the Cop (the
        # Thief wants a low cop-perspective value), high if I'm the Thief
        # (the Cop wants a high one, which is bad for the Thief).
        if worst is None or (value < worst if cop_role else value > worst):
            worst = value
    return worst


def score_moves(
    role: str, board: Board, own_pos: Coord,
    opponent_candidates: list[tuple[Coord, float]], depth: int,
    deadline: float | None = None,
) -> dict[Move, float] | None:
    """This turn's legal moves scored by belief-weighted, simultaneous-move-
    correct lookahead, in the mover's own units (higher is always better
    for `role`). Returns None if `deadline` passes before every move/
    candidate pair could be scored -- a partial ranking is worse than a
    known, honest fallback."""
    barriers = frozenset(board.barriers)
    grid_size = board.grid_size
    cop_role = role == "police"
    continuation_depth = max(depth - 2, 0)

    scored: dict[Move, float] = {}
    for move in board.legal_moves(own_pos):
        my_dest = board.destination(own_pos, move)
        total = 0.0
        for opp_pos, weight in opponent_candidates:
            opp_dests = _legal_dests(grid_size, barriers, opp_pos)
            worst = _worst_simultaneous_continuation(
                my_dest, opp_dests, barriers, grid_size, continuation_depth, cop_role, deadline
            )
            if worst is None:
                return None
            total += weight * worst
        # Cop-perspective value is already "higher is better" for police;
        # negate for the Thief so both roles maximize their own score.
        scored[move] = total if cop_role else -total
    return scored


def best_move(
    role: str, board: Board, own_pos: Coord,
    opponent_candidates: list[tuple[Coord, float]], depth: int = 4,
    deadline: float | None = None,
) -> Move | None:
    scored = score_moves(role, board, own_pos, opponent_candidates, depth, deadline)
    if scored is None:
        return None
    return max(scored, key=scored.get)


def score_barrier(
    board: Board, cop_pos: Coord, barrier_target: Coord,
    opponent_candidates: list[tuple[Coord, float]], depth: int = 4,
    deadline: float | None = None,
) -> float | None:
    """Cop-only: the search value (Cop units) of staying put and sealing
    `barrier_target` instead of moving, in the same simultaneous-correct
    units as `score_moves`. The Thief's move THIS round is evaluated
    against the barriers as they stood before this turn -- matching
    `Orchestrator.run_turn`, where a newly placed barrier is applied only
    after both sides' reveals, so it can never retroactively block a move
    the Thief already committed to in the same turn. The continuation
    plies (after this round) use the new barrier, since sealing it is what
    the whole decision is for. Returns None on deadline expiry, same
    contract as `score_moves`."""
    old_barriers = frozenset(board.barriers)
    new_barriers = old_barriers | {barrier_target}
    grid_size = board.grid_size
    continuation_depth = max(depth - 2, 0)

    total = 0.0
    for opp_pos, weight in opponent_candidates:
        opp_dests = _legal_dests(grid_size, old_barriers, opp_pos)
        worst = _worst_simultaneous_continuation(
            cop_pos, opp_dests, new_barriers, grid_size, continuation_depth, True, deadline
        )
        if worst is None:
            return None
        total += weight * worst
    return total
