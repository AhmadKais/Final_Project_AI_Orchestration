# Stage 4 — Language and Scent Integration

> Source: spec Sec. 10.3.4 (Table 3, row 4), Chapters 4 & 6. Implements: `domain/scent.py`, `domain/belief.py`, `infra/llm/`.

## Goal

The step-up stage: rigid coordinates are replaced by free-language reporting, the pheromone emission/decay model is implemented, and the LLM is embedded for inference and for constructing lies. **This is where the project's core uncertainty is born** — combining scent dynamics with strategic inference. Most sensitive stage; comes only after infrastructure and logic (Stages 1-3) are proven.

## Scope

- Scent emission/decay: `tau_ij(t+1) = max(0, (1-rho)*tau_ij(t) + delta_tau_ij)`, `rho = pheromone_decay` (0.10), peak `pheromone_center_intensity` (0.9), field `pheromone_grid_size` (5×5).
- Bayesian belief map update from (a) the opponent's unforgeable scent field and (b) their (possibly false) verbal hint.
- LLM providers for the verbal bluff layer only (`template` default, `ollama`, `claude_api`, `claude_cli`) — never for the move decision (Sec. 6.5's hallucination warning), unless both teams explicitly agree otherwise.
- Hint word cap (`hint_max_words`, default 15).

## Out of scope (later stages)

Public networking (Stage 5), Commit-Reveal (Stage 6).

## Acceptance criteria (spec Sec. 10.4)

- Free-language reporting is translated into inference.
- The scent map is updated and decays at every step.
- The LLM produces a hint (true or false).

## Status

**Done** (template provider only; `ollama`/`claude_api`/`claude_cli` providers remain stubbed -- lower priority since `template` is the default and the spec explicitly allows playing the entire series at zero tokens in `template`/`ollama` mode). Implemented: `ScentField.emit`/`.decay` (Gaussian radial falloff calibrated to spec Fig. 4's reference values), `BeliefMap.update_from_scent`/`.update_from_hint` (deterministic direction-keyword parser + Bayesian renormalization), `TemplateProvider`. Covered by `tests/{test_scent,test_belief_updates,test_llm_template}.py` (23 tests). `HeuristicBrain` needed no changes -- it already consumes whatever `BeliefMap` it's given via `arg_max()`, whether built from ground truth (Stage 3 tests) or real scent+hint evidence (this stage). Wiring `update_from_scent`/`update_from_hint` into an actual per-turn call sequence is Orchestrator work (Stage 8 / the end-to-end wiring task).

**Follow-up fix (found via full-game integration testing, not this stage's own tests):** a pure multiplicative Bayesian update only ever sharpens -- a belief that reached ~0.999 confidence at one cell took 10+ turns of strong contradicting evidence to budge at all, since a likelihood ratio of ~2 per turn can't out-race a 0.999 prior. Added `BeliefMap.decay_toward_uniform(rate)`, called once per turn before `update_from_scent`, blending the posterior toward uniform the same way the physical scent trail itself decays. See `test_decay_toward_uniform_erodes_an_overconfident_stale_belief` in `tests/test_belief_updates.py`.
