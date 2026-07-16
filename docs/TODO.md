# TODO

Mandatory repository content per spec Appendix E rule 50. Grouped by stage; see `docs/PRD/` for full acceptance criteria.

## Stage 1 — Base Logic ✅
- [x] Implement `Board.is_legal_move` / `apply_move` / `legal_moves` (`src/police_thief/domain/board.py`)
- [x] Implement barrier placement + capture detection (`Board.place_barrier`, `Board.is_capture`)
- [x] Implement `domain/rules.py` outcome determination
- [x] Implement `domain/scoring.py` payoff table
- [x] Un-skip and pass `tests/test_board.py` (+ new `test_rules.py`, `test_scoring.py`) -- 40/40 passing

## Stage 2 — Basic FastMCP Infrastructure ✅
- [x] Implement `infra/mcp_server.py` (`MoveMailbox`, `build_server`, `run_server`)
- [x] Implement `infra/mcp_client.py` (`OpponentClient.send_move`)
- [x] Manually verify: two local processes exchange a numeric move over localhost -- confirmed via real HTTP socket smoke test

## Stage 3 — Blind Strategy Module ✅
- [x] Implement `BrainBase.pick_move` legality wrapper
- [x] Implement `HeuristicBrain._pick_move` (full-information version, no belief yet)
- [x] Implement `BeliefMap.arg_max` / `.manhattan_distance` (the non-uncertainty half of belief.py)
- [x] Choose RL vs. heuristics vs. custom algorithm and document the choice -- pure heuristics (no RL), written up in README.md's "Academic report" §3

## Stage 4 — Language and Scent Integration ✅
- [x] Implement `ScentField.emit` / `.decay`
- [x] Implement `BeliefMap.update_from_scent` / `.update_from_hint` (`.arg_max` done in Stage 3)
- [x] Implement `TemplateProvider` (default, zero-token)
- [x] Implement `OllamaProvider`, `ClaudeAPIProvider`, `ClaudeCLIProvider` -- all mocked in tests (no real network/subprocess calls in the suite); `anthropic` added as a real dependency
- [x] `HeuristicBrain` already belief-map-driven, no change needed (verified via `test_belief_updates.py`)

## Stage 5 — Cloud Exposure and Tunneling ⛔ blocked on a second machine only
- [x] ngrok binary downloaded to `tools/ngrok`, verified runnable
- [x] ngrok account created (by the user) and authtoken configured (`tools/ngrok.yml`, gitignored) -- verified with `tools/ngrok config check`
- [x] Real tunnel opened and a real move round-tripped through the actual public ngrok URL to this project's own FastMCP server -- confirmed live, then cleaned up
- [ ] Update `config/<role>/game.toml` `opponent_url` for remote play -- trivial once there's an actual opponent to point at
- [ ] Run one full round against a remote peer -- **the only remaining blocker: requires an actual second machine on a different network**

## Stage 6 — Security and Cryptography ✅
- [x] Implement `domain/crypto.commit` / `.verify` / `.audit_log`
- [x] Implement `domain/protocol.build_message` / `.parse_message`
- [x] Implement `shared/system_info.collect_step0_declaration` / `.sign_declaration`
- [x] Un-skip and pass `tests/test_crypto.py` -- 96/96 passing, zero skips

## Stage 7 — Reporting and Visualization Shell ✅ (Gmail done for real now; LiveGUI screenshot still needs a display)
- [x] Complete Gmail OAuth setup (`credentials.json`, `token.json` — both gitignored, confirmed untracked) -- real Cloud project + consent screen + `gmail.send`-only scope done by the user, verified with a real sent email (real Gmail message ID, token reused without re-prompting) -- see `docs/GMAIL_SETUP.md`
- [x] Implement `infra/gatekeeper.py` (QuotaManager, TokenBucket, DOSDetector)
- [x] Implement `infra/email_sender.py` (tested against a mocked Gmail service)
- [x] Implement `interface/live_gui.py` (belief heatmap, turn banner) -- pure logic tested; live Tkinter rendering untested, no display/`python3-tk` in this sandbox
- [x] Implement `interface/replay_viewer.py` (Verified OK / TAMPERED)
- [x] Generate the 4 sample JSON reports (declaration/config/log/results) -- `scripts/generate_sample_reports.py` plays a real match and writes them to `docs/sample_reports/`; the log passes `ReplayViewer.verify_all()`. This is illustrative sample data (same purpose as the book's own attached examples), not a real league submission -- that still needs `credentials.json`/`token.json` and an actual opponent.

## Stage 8 — Orchestrator Integration ✅
- [x] Implement `shared/config_manager.py` (load/merge/hash `game.json` + `game.toml`)
- [x] Extend `infra/mcp_{server,client}.py` with the full Commit-Reveal message surface (commit/ack/reveal/final-audit/capture-claim)
- [x] Implement `peer_runtime/{deadline_tracker,watchdog}.py`
- [x] Implement `peer_runtime/orchestrator.py` (full per-turn Commit→Ack→Reveal→Verify loop + end-of-game mutual audit)
- [x] Implement `simulation_sdk/__init__.py` (`build_peer`, `run_peer`, `run_replay`)
- [x] Fix `BeliefMap.arg_max()` (was raising on an empty map -- broke turn 0) and add `COMMITTING -> TECHNICAL_LOSS` to the state machine (Fig. 11 says every communication stage should reach it, `COMMITTING` was missing)
- [x] Two Orchestrators play a full game end-to-end in-process, log passes `ReplayViewer.verify_all()`

## Post-wiring strategy hardening ✅
- [x] Wire Cop barrier placement all the way through the Commit-Reveal protocol (`domain/protocol.encode_move`/`decode_move`) -- previously implemented at the Board level (Stage 1) but never actually reachable from a real turn
- [x] Fix a real self-trapping bug: `HeuristicBrain` could wall off its own only route to the target (Sec. 3.4's own warning) -- now checks a safe alternate route exists first
- [x] Add mobility-aware tie-break to the Robber's evasion (prefers the resulting cell with more future legal moves, avoids dead ends)
- [x] Fix a real stuck-belief bug found via multi-seed integration testing: `BeliefMap.decay_toward_uniform` prevents an old, highly-confident-but-stale belief from taking 10+ turns to correct
- [x] Download ngrok into `tools/` (gitignored), confirm the exact remaining blocker directly (`ERR_NGROK_4018`, needs a real account)
- [x] Implement `OllamaProvider`/`ClaudeAPIProvider`/`ClaudeCLIProvider` for real (previously stubbed)
- [x] Generate real sample JSON reports from an actual match (`scripts/generate_sample_reports.py`)
- [x] Wire Step-0 hardware declaration exchange into `run_game()` (Sec. 5.5, Appendix E rules 24 & 53) -- `collect_step0_declaration`/`sign_declaration` existed since Stage 6 but were never actually called during a real game; now exchanged before the first move via a new `receive_step0`/`send_step0` MCP tool, and recorded in the log
- [x] Wire the Watchdog into `run_game()` (Sec. 8.4.2) -- also implemented-but-unused since Stage 8; `HeartbeatWatchdog` now runs on a real background OS thread (not another asyncio task in the same event loop, which a CPU-bound freeze would starve too) and the main loop checks it every turn
- [x] 182 tests, 181 passing, 1 skipped (no display/`tkinter`)

## Competitive strategy hardening ✅
- [x] Investigated the lecturer-provided reference simulator (`github.com/rmisegal/Game-P2P-Cop-Chase`) for wire compatibility -- its own README settles the question: it's an explicitly-basic "learning aid, not a submission skeleton," and "where this repo differs from the book, the book and its binding parameter table win." The book itself states the wire contract is set by live per-pair negotiation, not a fixed universal protocol -- confirmed our `crypto.py`/`scent.py` already follow the book's own literal formulas where the reference repo deviates (nonce placement, decay shape). No rewrite needed.
- [x] Implemented `domain/strategy/search.py` + `MinimaxBrain` -- belief-space-weighted bounded-depth minimax (worst-case-adversary search, not a fixed opponent model), now the SDK's default brain in place of the plain one-ply `HeuristicBrain`
- [x] Added `tests/support/local_sim.py` + `tests/test_strategy_adversarial.py` -- a local (non-networked) full-game simulator running statistical win-rate trials against a `RandomBrain` baseline, a `GreedyBrain` that reproduces the reference repo's own shipped policy, and `HeuristicBrain` itself, across randomized start positions
- [x] The adversarial harness caught two real bugs on its first run (not present in the old hand-picked unit tests, which only ever used a 100%-confident correct belief): (1) minimax had no time-preference -- a capture found this turn and one found three turns later both scored a flat +1000, so the search could stall indefinitely instead of closing a sure capture now; fixed with a depth-based speed bonus. (2) A stale, over-confident belief (built from several early scent deposits stacking on one cell before the opponent moved on) could coincide with the mover's own current cell, which the search treated as a live hypothesis even though `Board.is_capture()` on real positions had already ruled it out that same turn; fixed by excluding the mover's own cell from `BeliefMap.arg_max`/`.top_k`, and by decoupling belief-forgetting from the book-binding scent-decay rate (private per-peer tuning, not negotiated physics) so stale confidence fades faster.
- [x] 192 tests, 191 passing, 1 skipped (no display/`tkinter`)

## Submission checklist (Appendix C Table 6) — do last
- [ ] Two GitHub repos (Cop, Robber), cross-linked READMEs
- [ ] `v1.0-submission` annotated Git tag, pushed
- [ ] README report components complete in both repos (Sec. 9.4.2) -- items 1-4 (Dec-POMDP model, FastMCP dilemmas, strategies, learning curves) written for real in `README.md`; items 5-6 (screenshots, companion link) still need a real display and the repo split, and then copying this whole section into both split repos' READMEs
- [ ] Belief-map and `Verified OK` replay screenshots attached
- [ ] At least 2 matches played against different teams
- [ ] End-of-match email sent by both sides, separately
- [ ] `.gitignore` verified — no secrets committed
