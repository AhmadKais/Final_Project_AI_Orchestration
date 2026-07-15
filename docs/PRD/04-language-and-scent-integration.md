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

Not started. Stubs live in `src/police_thief/domain/{scent,belief}.py` and `src/police_thief/infra/llm/`.
