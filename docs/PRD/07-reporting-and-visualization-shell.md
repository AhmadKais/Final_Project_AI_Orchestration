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

Not started. Stubs live in `src/police_thief/infra/{email_sender,gatekeeper}.py` and `src/police_thief/interface/`.
