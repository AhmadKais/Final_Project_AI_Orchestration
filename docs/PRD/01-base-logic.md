# Stage 1 — Base Logic

> Source: spec Sec. 10.3.1 (Table 3, row 1), Chapter 3. Implements: `domain/board.py`, `domain/rules.py`, `domain/scoring.py`.

## Goal

The physical core of the game, with **no communication or intelligence whatsoever**. Everything runs in a single process. If two agents can't move correctly on a local board, there's no point connecting a network between them.

## Scope

- Grid of size `grid_size` (default 7×7), coordinate system (top-left origin, 0-indexed).
- Movement: one orthogonal step (N/S/E/W) or STAY. No diagonals.
- Cop-only barrier placement: self-cell or one orthogonally-adjacent cell, up to `max_barriers` (default 14). Barriers are irreversible.
- Capture detection by coordinate overlap: Cop lands on Robber's cell, a barrier lands on the Robber's cell, or the Robber has zero legal moves.
- Scoring table (Table 2 / Appendix F Table 17): capture, survival, technical-loss payoffs.

## Out of scope (later stages)

Networking, scent, belief, language, cryptography, GUI.

## Acceptance criteria (spec Sec. 10.4)

- Two agents move legally on the `grid_size` grid.
- A move beyond `max_barriers` is rejected.
- Coordinate overlap triggers a capture.

## Status

**Done.** Implemented in `src/police_thief/domain/{board,rules,scoring}.py`, covered by `tests/{test_board,test_rules,test_scoring}.py` (40 tests, all passing). Runs as pure in-process logic with no networking, matching the stage's scope.
