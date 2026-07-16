# Distributed Cops-and-Robbers over a Peer-to-Peer Network

Course final project for *Orchestration of AI Agents*, University of Haifa. Two symmetric autonomous agents — **Cop** and **Robber** — chase each other on a grid board with no central server: partial observability is modeled as a Dec-POMDP, location belief comes from a decaying scent-trail (stigmergy) mechanism cross-referenced against (possibly false) verbal hints, and fairness with no referee is enforced by a Commit-Reveal cryptographic protocol over SHA-256.

Full translated specification: [`police_thief_p2p_EN.md`](police_thief_p2p_EN.md) (translated from the original Hebrew, [`police_thief_p2p.pdf`](police_thief_p2p.pdf)).

**Status: playable end-to-end.** All 8 development stages (`docs/PLAN.md`) are implemented and tested, plus all four LLM providers. Stage 5 (Cloud Exposure and Tunneling) is the one piece genuinely blocked on your own action: `tools/ngrok` is pre-downloaded and verified runnable, but opening a real tunnel needs your own ngrok account/authtoken (confirmed by actually running it and hitting `ERR_NGROK_4018`), and proving NAT traversal needs a second machine on a different network -- see `docs/TUNNELING.md`. Two `Orchestrator`s can play a complete, cryptographically-verified game against each other right now (proven by `tests/test_orchestrator_integration.py`, and by `scripts/generate_sample_reports.py`'s real generated match in `docs/sample_reports/`); real network deployment (`simulation_sdk.run_peer`) uses the identical code path, just pointed at a real opponent URL instead of an in-process one. 177 tests, 176 passing, 1 skipped (no display/`tkinter` in the dev sandbox this was built in). Beyond wiring, `HeuristicBrain` now also places barriers tactically (Cop, never self-trapping -- see `docs/STRATEGY.md`) and the belief map decays toward uniform each turn so a stale high-confidence guess can't get permanently stuck.

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

## Running

```bash
# Terminal 1
uv run python -m police_thief peer --role police
# Terminal 2
uv run python -m police_thief peer --role thief

# Replay and cryptographically verify a saved match:
uv run python -m police_thief replay --log logs/police_match.json
```

Both peers need real, reachable `opponent_url`s in their `config/<role>/game.toml` -- `localhost` ports for same-machine testing, or public tunnel URLs for real league play (`docs/TUNNELING.md`).

## Development order

Built in the eight layered stages defined in [`docs/PLAN.md`](docs/PLAN.md) / [`docs/PRD/`](docs/PRD/) — each stage ran end-to-end before the next began (spec Chapter 10; Stage 8 is a courtesy addition that wires 1-7 into an actually-runnable game). See [`docs/TODO.md`](docs/TODO.md) for the current task breakdown and [`docs/STRATEGY.md`](docs/STRATEGY.md) for how to plug in your own movement-policy brain.

## Tests

```bash
uv run pytest
```

176 of 177 tests pass; the one skip is `test_live_gui.py`'s Tkinter widget-construction test, which needs a real display and `python3-tk` (not present in the sandbox this was built in — the pure heatmap/banner logic it depends on is fully tested). The centerpiece is `tests/test_orchestrator_integration.py`: two `Orchestrator`s, wired to each other's in-process FastMCP servers, play a complete game and produce a log that cryptographically re-verifies end to end.

---

## Academic report (fill in before submission — spec Sec. 9.4.2)

The final README (in **each** of the two submission repositories, Cop and Robber, cross-linked) must additionally contain:

1. **The chosen Dec-POMDP model** — state space, observations, uncertainty formalization (Chapter 1).
2. **FastMCP orchestration dilemmas** — queue management, network-failure handling, Gatekeeper/Orchestrator design choices (Chapters 2, 8).
3. **The strategies implemented** — heuristics, LLM-assisted, and/or Q-Learning, and why (Chapter 6).
4. **Learning curves**, if reinforcement learning was used.
5. **Screenshots** — Live GUI belief map, and Replay App showing `Verified OK`.
6. **A link to the companion repository** (Cop ↔ Robber).

*(Not written yet. The system is playable end-to-end; what's left before this section can be filled in is Stage 5 (a real tunneled connection to another machine, blocked on your accounts) and at least two real league matches, per the submission checklist in `docs/TODO.md`.)*
