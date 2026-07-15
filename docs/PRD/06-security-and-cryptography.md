# Stage 6 — Security and Cryptography

> Source: spec Sec. 10.3.6 (Table 3, row 6), Chapter 5. Implements: `domain/crypto.py`, `domain/protocol.py`, `shared/system_info.py`.

## Goal

Only once remote communication works (Stage 5) is it wrapped in Commit-Reveal. Encryption adds a trust layer on top of communication already proven operationally reliable.

## Scope

- `commit()`/`verify()` over SHA-256: `H_commit = SHA256(State ‖ Move ‖ Intent ‖ Nonce)`, canonical JSON (sorted keys, fixed separators).
- Nonce generation via `secrets` (never `random`).
- Four-stage sequence: Commit → Acknowledge → Reveal → (end-of-game) Final Audit.
- Mutual log audit at game end; any hash mismatch is an automatic, unappealable technical loss (Appendix E rule 19).
- Step-0 hardware/software declaration, cryptographically signed, including the GitHub commit hash actually played (Appendix E rule 53).

## Out of scope

Reporting/GUI (Stage 7).

## Acceptance criteria (spec Sec. 10.4)

- A move is committed via Commit and then revealed via Reveal with a valid Nonce.
- Step-0 verifies hardware.

## Status

Not started. Stubs live in `src/police_thief/domain/{crypto,protocol}.py` and `src/police_thief/shared/system_info.py`.
