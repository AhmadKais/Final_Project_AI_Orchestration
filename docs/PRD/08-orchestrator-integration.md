# Stage 8 — Orchestrator Integration (wiring everything together)

> Source: Chapter 8 (Orchestrator pattern, state machine, reliability). Not one of the book's own 7 numbered stages (Table 3 doesn't assign Chapter 8 its own row -- the Orchestrator is the connective tissue woven through all of them). Implements: `peer_runtime/orchestrator.py`, `shared/config_manager.py`, `peer_runtime/{deadline_tracker,watchdog}.py`, `simulation_sdk/__init__.py`.

## Goal

Stages 1-7 each implemented and unit-tested one subsystem in isolation. This stage proves they actually work *together*: an `Orchestrator` that drives one full turn (Commit -> Acknowledge -> Reveal -> Verify), advances a local-truth `Board`, updates `BeliefMap` from real `ScentField` + hint evidence, and completes a full game with a mutual cryptographic audit at the end.

## Scope

- `shared/config_manager.py`: load + merge `config/game.json` (shared, signed) with `config/<role>/game.toml` (private) -- shared always wins on key collision (Appendix B).
- `infra/mcp_server.py` / `infra/mcp_client.py` extended beyond Stage 2's plain-move tool with the full Commit-Reveal message surface: `receive_commit`/`receive_ack`/`receive_reveal`/`receive_final_audit`/`receive_capture_claim` and matching `send_*` client methods, each message kind on its own queue.
- `peer_runtime/deadline_tracker.py`, `peer_runtime/watchdog.py`: real implementations of the Sec. 8.4 reliability patterns.
- `peer_runtime/orchestrator.py`: the full per-turn protocol -- commit, exchange, reveal, verify, advance the board, update belief from the opponent's newly-true position, detect capture/survival, and (at game end) exchange Nonces and audit the opponent's entire log.
- `simulation_sdk/__init__.py`: `build_peer` (config -> Orchestrator), `run_peer` (real network deployment), `run_replay`.

## Design bugs this stage surfaced and fixed

`BeliefMap.arg_max()` used to raise on an empty map (Stage 3's test asserted this). Wiring a real turn loop showed that was wrong: turn 0 always starts with zero evidence, and the brain still needs *some* target to move toward. Fixed to auto-initialize a uniform prior instead of raising; the state machine also needed `COMMITTING -> TECHNICAL_LOSS` added (a real network failure can happen while waiting for the opponent's ack, and the book's own Fig. 11 already describes TECHNICAL_LOSS as reachable from every communication stage, not just some of them).

## Follow-up: two more implemented-but-unwired mechanisms found and fixed

The same pattern that caused the barrier-placement gap (see `docs/TODO.md`'s "Post-wiring strategy hardening") turned up twice more on a deliberate audit against Appendix E's full rule list:

- **Step-0 (Sec. 5.5, Appendix E rules 24 & 53).** `collect_step0_declaration`/`sign_declaration` existed since Stage 6, fully unit-tested, but `run_game()` never actually called them. Added a `receive_step0`/`send_step0` MCP tool and `Orchestrator._exchange_step0()`, run once before the first move; both sides' declarations are recorded in the written log. A missing/failed opponent declaration is *not* a technical loss -- rule 24's own sanction is "forfeiture of eligibility for the computational-fairness bonus," softer than the hash-mismatch disqualification rule.
- **Watchdog (Sec. 8.4.2, Appendix E rule 7).** Same story: `watchdog_check` existed and was tested, but nothing called it during a real game. Added `HeartbeatWatchdog`, which runs on a genuine background **OS thread**, not another asyncio task sharing the main event loop -- the spec explicitly calls for "an independent background process," and a same-loop task would be starved by exactly the CPU-bound freeze it's meant to catch. `run_game()` heartbeats after Step-0 and after every turn, and checks `triggered` before each new turn.

## Deliberately not wired in

Capture-claim honesty cross-checking via `domain.rules.check_capture_claim` -- the underlying Commit-Reveal hash verification already catches any move a side could lie about, so a dishonest claim can't actually change the outcome; cross-checking the claim itself is optional richness. The mechanic is implemented and unit-tested from Stage 1.

Real two-*process* network deployment (`simulation_sdk.run_peer` actually binding a socket and playing against a genuinely separate process) is not testable in this sandbox, same as Stage 5's tunneling -- proven instead with fastmcp's in-process transport, which exercises the exact same tool-call code path.

## Acceptance criteria (not in the book -- this stage's own)

- Two `Orchestrator`s, wired to each other's in-process FastMCP servers, play a complete game to a definite outcome (capture or survival), with no forgery detected on either side.
- The resulting game log (both sides' moves, not just one) passes `ReplayViewer.verify_all()`.
- A Cop and Robber starting close together on a small barrier-free board reliably reach a capture well before the step budget, proving the Manhattan-pursuit heuristic and belief updates are actually influencing play, not just running without crashing.
- Both sides' Step-0 declarations are present after `run_game()` and recorded in the log.
- `HeartbeatWatchdog` triggers within its timeout when heartbeats stop, and does not trigger while they keep coming.

## Status

**Done.** Covered by `tests/test_orchestrator_integration.py` (6 tests, including the full two-sided game and the Step-0 exchange), `tests/test_config_manager.py` (8 tests), and `tests/test_deadline_and_watchdog.py` (10 tests, including `HeartbeatWatchdog`). Verified stable across 5 repeated runs (async/threading timing was the main flakiness concern). Full project suite: 182 tests, 181 passed, 1 skipped (tkinter, no display in this sandbox).
