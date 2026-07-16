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
- [ ] Choose RL vs. heuristics vs. custom algorithm and document the choice in the README -- deferred to submission time (pure heuristics is the shipped default)

## Stage 4 — Language and Scent Integration ✅ (mostly)
- [x] Implement `ScentField.emit` / `.decay`
- [x] Implement `BeliefMap.update_from_scent` / `.update_from_hint` (`.arg_max` done in Stage 3)
- [x] Implement `TemplateProvider` (default, zero-token)
- [ ] Implement `OllamaProvider`, `ClaudeAPIProvider`, `ClaudeCLIProvider` -- deferred, not required for zero-token play
- [x] `HeuristicBrain` already belief-map-driven, no change needed (verified via `test_belief_updates.py`)

## Stage 5 — Cloud Exposure and Tunneling ⛔ blocked on you
- [ ] Set up ngrok/Localtonet for both roles -- **requires your own account/authtoken, see `docs/TUNNELING.md`**
- [ ] Update `config/<role>/game.toml` `opponent_url` for remote play
- [ ] Run one full round against a remote peer -- **requires an actual second machine on a different network**

## Stage 6 — Security and Cryptography ✅
- [x] Implement `domain/crypto.commit` / `.verify` / `.audit_log`
- [x] Implement `domain/protocol.build_message` / `.parse_message`
- [x] Implement `shared/system_info.collect_step0_declaration` / `.sign_declaration`
- [x] Un-skip and pass `tests/test_crypto.py` -- 96/96 passing, zero skips

## Stage 7 — Reporting and Visualization Shell ✅ (mostly)
- [ ] Complete Gmail OAuth setup (`credentials.json`, `token.json` — never commit) -- **needs your own Google account/credentials, see Appendix A / `docs/`**
- [x] Implement `infra/gatekeeper.py` (QuotaManager, TokenBucket, DOSDetector)
- [x] Implement `infra/email_sender.py` (tested against a mocked Gmail service)
- [x] Implement `interface/live_gui.py` (belief heatmap, turn banner) -- pure logic tested; live Tkinter rendering untested, no display/`python3-tk` in this sandbox
- [x] Implement `interface/replay_viewer.py` (Verified OK / TAMPERED)
- [ ] Generate the 4 sample JSON reports (declaration/config/log/results) for at least one real match -- game logs now generate for real (Stage 8), but the declaration/config/results trio still need a real league match, not just the in-process integration test

## Stage 8 — Orchestrator Integration ✅
- [x] Implement `shared/config_manager.py` (load/merge/hash `game.json` + `game.toml`)
- [x] Extend `infra/mcp_{server,client}.py` with the full Commit-Reveal message surface (commit/ack/reveal/final-audit/capture-claim)
- [x] Implement `peer_runtime/{deadline_tracker,watchdog}.py`
- [x] Implement `peer_runtime/orchestrator.py` (full per-turn Commit→Ack→Reveal→Verify loop + end-of-game mutual audit)
- [x] Implement `simulation_sdk/__init__.py` (`build_peer`, `run_peer`, `run_replay`)
- [x] Fix `BeliefMap.arg_max()` (was raising on an empty map -- broke turn 0) and add `COMMITTING -> TECHNICAL_LOSS` to the state machine (Fig. 11 says every communication stage should reach it, `COMMITTING` was missing)
- [x] Two Orchestrators play a full game end-to-end in-process, log passes `ReplayViewer.verify_all()` -- 146/147 tests passing project-wide (1 skip: no display/`tkinter`)

## Submission checklist (Appendix C Table 6) — do last
- [ ] Two GitHub repos (Cop, Robber), cross-linked READMEs
- [ ] `v1.0-submission` annotated Git tag, pushed
- [ ] README report components complete in both repos (Sec. 9.4.2)
- [ ] Belief-map and `Verified OK` replay screenshots attached
- [ ] At least 2 matches played against different teams
- [ ] End-of-match email sent by both sides, separately
- [ ] `.gitignore` verified — no secrets committed
