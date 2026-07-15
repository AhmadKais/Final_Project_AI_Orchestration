# Distributed Cops-and-Robbers over a Peer-to-Peer Network

Course final project for *Orchestration of AI Agents*, University of Haifa. Two symmetric autonomous agents — **Cop** and **Robber** — chase each other on a grid board with no central server: partial observability is modeled as a Dec-POMDP, location belief comes from a decaying scent-trail (stigmergy) mechanism cross-referenced against (possibly false) verbal hints, and fairness with no referee is enforced by a Commit-Reveal cryptographic protocol over SHA-256.

Full translated specification: [`police_thief_p2p_EN.md`](police_thief_p2p_EN.md) (translated from the original Hebrew, [`police_thief_p2p.pdf`](police_thief_p2p.pdf)).

**Status: Stages 1-2 implemented.** Stage 1 (Base Logic: `domain/board.py`, `domain/rules.py`, `domain/scoring.py`) and Stage 2 (Basic FastMCP Infrastructure: `infra/mcp_server.py`, `infra/mcp_client.py` -- plain geometric moves over `localhost`, no crypto/scent/language yet) are real, tested code. Everything else under `src/police_thief/` is still a stub (`raise NotImplementedError`), to be filled in stage by stage per `docs/PLAN.md`.

## Architecture

Mirrors the reference layout described in the spec's Appendix D:

```
interface/        Live GUI (belief heatmap, turn banner) + Replay Viewer
simulation_sdk/    Single business entry point: config -> Orchestrator -> interface
peer_runtime/      One independent peer: negotiation -> turn loop -> audit
  orchestrator.py    Single-gateway coordinator (Sec. 8.3)
  state_machine.py   Legal turn-phase transitions (Sec. 8.3, Fig. 11)
  deadline_tracker.py  Per-request timeout (Sec. 8.4.1)
  watchdog.py        Whole-loop heartbeat monitor (Sec. 8.4.2)
domain/            Pure game logic -- board, scent, belief, rules, scoring, crypto, protocol
  strategy/          Pluggable movement-policy "brain" (Chapter 6) -- YOUR extension point
infra/             External I/O -- FastMCP transport, LLM providers, Gmail sender, Gatekeeper
shared/            Config loading, Step-0 hardware declaration, versioning
```

The Cop's and Robber's code run as two fully separate processes, selected at launch by `--role` and reading from separate config directories (`config/police/` vs `config/thief/`). They **never share memory or import live state from each other** — that's a hard rule (spec Sec. 2.4.2, Appendix E rule 2), not a style preference.

## Configuration

- [`config/game.json`](config/game.json) — the shared, cryptographically-signed contract both peers must load byte-for-byte identically: board size, scoring, pheromone decay, rate limits, etc. Defaults here are the spec's binding minimums (Appendix F). Never hand-edit a number the spec expresses as a bracketed `[parameter]` anywhere else in the code.
- [`config/police/game.toml`](config/police/game.toml) / [`config/thief/game.toml`](config/thief/game.toml) — private, per-role settings (network port, opponent URL, strategy-class override, LLM mode, email). Not signed, not negotiated.

## Setup

```bash
uv sync
```

## Running (once implemented)

```bash
# Terminal 1
uv run python -m police_thief peer --role police
# Terminal 2
uv run python -m police_thief peer --role thief

# Replay and cryptographically verify a saved match:
uv run python -m police_thief replay --log logs/police_match.json
```

## Development order

Build in the seven layered stages defined in [`docs/PLAN.md`](docs/PLAN.md) / [`docs/PRD/`](docs/PRD/) — each stage must run end-to-end before the next begins (spec Chapter 10). See [`docs/TODO.md`](docs/TODO.md) for the current task breakdown and [`docs/STRATEGY.md`](docs/STRATEGY.md) for how to plug in your own movement-policy brain.

## Tests

```bash
uv run pytest
```

`test_board.py`, `test_rules.py`, `test_scoring.py`, `test_mcp_infra.py`, and `test_state_machine.py` pass (Stages 1-2 + the always-available state machine). `test_scent.py` and `test_crypto.py` are still skipped, each pointing at the PRD stage (4 and 6) that unblocks them.

---

## Academic report (fill in before submission — spec Sec. 9.4.2)

The final README (in **each** of the two submission repositories, Cop and Robber, cross-linked) must additionally contain:

1. **The chosen Dec-POMDP model** — state space, observations, uncertainty formalization (Chapter 1).
2. **FastMCP orchestration dilemmas** — queue management, network-failure handling, Gatekeeper/Orchestrator design choices (Chapters 2, 8).
3. **The strategies implemented** — heuristics, LLM-assisted, and/or Q-Learning, and why (Chapter 6).
4. **Learning curves**, if reinforcement learning was used.
5. **Screenshots** — Live GUI belief map, and Replay App showing `Verified OK`.
6. **A link to the companion repository** (Cop ↔ Robber).

*(Not written yet — this is a scaffold. Fill in once Stages 1-7 are implemented and at least two league matches have been played, per the submission checklist in `docs/TODO.md`.)*
