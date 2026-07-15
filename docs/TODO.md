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

## Stage 3 — Blind Strategy Module
- [ ] Implement `BrainBase.pick_move` legality wrapper
- [ ] Implement `HeuristicBrain._pick_move` (full-information version, no belief yet)
- [ ] Choose RL vs. heuristics vs. custom algorithm and document the choice in the README

## Stage 4 — Language and Scent Integration
- [ ] Implement `ScentField.emit` / `.decay`
- [ ] Implement `BeliefMap.update_from_scent` / `.update_from_hint` / `.arg_max`
- [ ] Implement `TemplateProvider` (default, zero-token)
- [ ] Implement `OllamaProvider`, `ClaudeAPIProvider`, `ClaudeCLIProvider`
- [ ] Wire `HeuristicBrain` to use the belief map instead of ground truth

## Stage 5 — Cloud Exposure and Tunneling
- [ ] Set up ngrok/Localtonet for both roles
- [ ] Update `config/<role>/game.toml` `opponent_url` for remote play
- [ ] Run one full round against a remote peer

## Stage 6 — Security and Cryptography
- [ ] Implement `domain/crypto.commit` / `.verify` / `.audit_log`
- [ ] Implement `domain/protocol.build_message` / `.parse_message`
- [ ] Implement `shared/system_info.collect_step0_declaration` / `.sign_declaration`
- [ ] Un-skip and pass `tests/test_crypto.py`

## Stage 7 — Reporting and Visualization Shell
- [ ] Complete Gmail OAuth setup (`credentials.json`, `token.json` — never commit)
- [ ] Implement `infra/gatekeeper.py` (QuotaManager, TokenBucket, DOSDetector)
- [ ] Implement `infra/email_sender.py`
- [ ] Implement `interface/live_gui.py` (belief heatmap, turn banner)
- [ ] Implement `interface/replay_viewer.py` (Verified OK / TAMPERED)
- [ ] Generate the 4 sample JSON reports (declaration/config/log/results) for at least one real match

## Submission checklist (Appendix C Table 6) — do last
- [ ] Two GitHub repos (Cop, Robber), cross-linked READMEs
- [ ] `v1.0-submission` annotated Git tag, pushed
- [ ] README report components complete in both repos (Sec. 9.4.2)
- [ ] Belief-map and `Verified OK` replay screenshots attached
- [ ] At least 2 matches played against different teams
- [ ] End-of-match email sent by both sides, separately
- [ ] `.gitignore` verified — no secrets committed
