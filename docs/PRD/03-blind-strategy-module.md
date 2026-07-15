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

Not started. Stubs live in `src/police_thief/domain/strategy/`.
