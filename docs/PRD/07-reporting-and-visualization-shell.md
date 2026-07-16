# Stage 7 — Reporting and Visualization Shell

> Source: spec Sec. 10.3.7 (Table 3, row 7), Chapters 9 & 7, Appendix A. Implements: `infra/email_sender.py`, `infra/gatekeeper.py`, `interface/`.

## Goal

Build the outer shell last, since it consumes all the layers beneath it: Gmail API reporting via OAuth 2.0, the live GUI, and the Replay App.

## Scope

- OAuth 2.0 setup (Appendix A): `credentials.json` + `token.json`, `gmail.send`-only scope, both gitignored.
- Gatekeeper pattern in front of every send: Quota Manager → Token Bucket → DOS Detector (Sec. 9.3.1-9.3.2).
- Four mandatory signed JSON report types: declaration, configuration, log, results — sent to `rmisegal+uoh26finalgame@gmail.com`, each team separately.
- Live GUI: belief heatmap (local truth only, never the objective board — Appendix E rules 8-9) + turn-status banner.
- Replay Viewer: step-by-step cryptographic re-verification, rendering `Verified OK` vs `TAMPERED`.

## Acceptance criteria (spec Sec. 10.4)

- A game summary is sent via Gmail.
- The GUI displays the (local-truth) state.
- The Replay App replays a recorded round.

## Status

**Done, with one honest gap.** `infra/gatekeeper.py` (QuotaManager/TokenBucket/DOSDetector/Gatekeeper, matching the book's own Token-Bucket code sample), `infra/email_sender.py` (`get_service`/`send_report`, matching Appendix A's OAuth flow -- tested with a mocked Gmail service, since real credentials aren't something I can or should generate), `interface/replay_viewer.py` (full `load`/`verify_all`/`step_through`, CLI-based `Verified OK`/`TAMPERED` output), and `interface/live_gui.py` (`heatmap_color`/`banner_state` pure logic + a Tkinter `LiveGUI` class) are all implemented. Covered by `tests/{test_gatekeeper,test_email_sender,test_replay_viewer,test_live_gui}.py` (35 tests, 126/127 project-wide passing).

**The gap:** this sandbox has no display and no `tkinter` module installed, so `LiveGUI`'s actual widget rendering is untested here -- only its pure color/banner logic is (which is what determines what gets drawn). The test file includes a `pytest.importorskip`-guarded construction test that will run for real once you have `python3-tk` and a display. Gmail OAuth similarly needs your own `credentials.json`/`token.json` (Appendix A) to exercise for real; `send_report` is fully tested against a mock instead.
