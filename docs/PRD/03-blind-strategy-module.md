# Stage 3 — "Blind" Strategy Module

> Source: spec Sec. 10.3.3 (Table 3, row 3), Chapter 6. Implements: `domain/strategy/`.

## Goal

Wire up an initial decision-making module that operates in a world of **complete and accurate information** (no scent, no natural language, no deception yet) — isolating the correctness of the decision core from the uncertainty added in Stage 4.

## Scope

Pick one (all three are equal-value tracks per Sec. 6.3.1 — the course did not teach RL and does not require it):

- Pure heuristics: Manhattan distance + a (not-yet-uncertain) target cell.
- Your own heuristic algorithm.
- Optional: Bellman equation / Q-Learning.

The move decision is always algorithmic — see `domain/strategy/brain_base.py`'s `BrainBase` contract. `HeuristicBrain` is the reference default.

## Out of scope (later stages)

Belief maps under uncertainty (Stage 4 introduces the actual uncertainty this module will later contend with), LLM bluffing (Stage 4).

## Acceptance criteria (spec Sec. 10.4)

- Given a known target location, the agent computes and executes the shortest path without manual intervention.

## Status

**Done.** `BrainBase.pick_move` legality wrapper, `HeuristicBrain._pick_move` (Manhattan-distance greedy movement -- Cop minimizes, Robber maximizes), and `BeliefMap.arg_max`/`manhattan_distance` (the two belief-map methods this stage needs; `update_from_scent`/`update_from_hint` stay stubbed for Stage 4's actual uncertainty) implemented in `src/police_thief/domain/strategy/` and `domain/belief.py`. Covered by `tests/test_strategy.py` (9 tests), including a full run-to-target simulation proving the shortest-path acceptance criterion with no manual intervention.
