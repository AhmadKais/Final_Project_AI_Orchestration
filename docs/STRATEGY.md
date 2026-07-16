# Strategy Module — Extension Guide

> Referenced from spec Appendix F Table 22 and Sec. 6.2.

## How to plug in your own brain

The movement policy is selected in your private `config/<role>/game.toml`, in the `[strategy]` section:

```toml
[strategy]
police_class = "police_thief.domain.strategy:MyPoliceBrain"
thief_class  = "police_thief.domain.strategy:MyThiefBrain"
```

Leaving the section commented out/empty runs the shipped `HeuristicBrain` (Bayesian belief map + Manhattan distance — see `src/police_thief/domain/strategy/heuristic_brain.py`).

## Contract

Subclass `police_thief.domain.strategy.brain_base.BrainBase`:

- Override `_pick_move(self, board, own_pos, belief) -> Move`. **Must always return a legal move** — `PeerRuntime` rejects illegal moves and forces a technical loss (spec Sec. 6.2, Appendix E rule 13-14).
- Cop only: override `_decide_barrier(self, board, cop_pos, belief) -> Coord | None` to choose a barrier placement instead of moving. Only called when `_pick_move` returns `STAY`; validated the same way `Board.place_barrier` is (self-cell or orthogonally adjacent, in bounds, unbarriered, under quota) before it's ever committed to.
- **Watch your own trap.** The spec warns explicitly (Sec. 3.4): "a barrier placed greedily can trap the Cop itself behind a wall it built." `HeuristicBrain._best_barrier_option` only offers a placement if the Cop still has at least one other legal move that keeps making progress toward the target afterward — check the same before you offer one from your own brain.

## The three equal-value tracks (spec Sec. 6.3-6.3.1)

None of these is "more correct" than the others — the course did not teach RL, and a fully competitive agent can be built with heuristics alone:

1. **Pure heuristics** (Bayes + Manhattan) — the shipped default. Deterministic, transparent, easy to debug. Beyond raw pursuit/evasion, `HeuristicBrain` also: seals off one of the target's escape routes with a barrier when tactically close (Cop only, distance 2-3, never self-trapping); tie-breaks the Robber's evasion by which resulting cell keeps the most future mobility open (avoids backing into dead ends); and decays belief confidence toward uniform each turn (`BeliefMap.decay_toward_uniform`) so a stale high-confidence guess can still be overturned by fresh evidence instead of getting stuck.
2. **Your own heuristic algorithm** — combine belief, scent, barrier exploitation, and forward search (minimax/expectimax) in deterministic code.
3. **Reinforcement learning (optional)** — Q-Learning via the Bellman equation, with epsilon-greedy exploration. Only worthwhile if you want the learning-curve evidence for the README (Sec. 9.4.2 item 4).

## Hard boundary: the LLM never decides movement

The language model (see `infra/llm/`) is wired into the strategy module **only** for the verbal bluff layer — producing hint text and classifying/profiling the opponent's language. It must never receive the move decision itself: LLMs reliably hallucinate coordinates, directions, and distances (spec Sec. 6.5's explicit warning). The one exception requires **documented mutual agreement between both competing teams** before the game (Sec. 6.5) — and even then, the local algorithm must still validate legality of anything the model proposes.
