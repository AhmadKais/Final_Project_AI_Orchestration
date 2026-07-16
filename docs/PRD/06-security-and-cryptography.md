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

**Done.** `domain/crypto.py` (`commit`/`verify`/`audit_log`, matching the book's own SHA-256 code sample in Sec. 5.3.2 exactly), `domain/protocol.py` (envelope build/parse with its own SHA-256 signature, distinct from `H_commit` -- catches tampering with message metadata like step/role, not just the move triple), and `shared/system_info.py` (`collect_step0_declaration` from `/proc/cpuinfo`, `/proc/meminfo`, `nvidia-smi` where present, plus `sign_declaration` via HMAC-SHA256). Covered by `tests/{test_crypto,test_protocol,test_system_info}.py` (19 tests). All previously-skipped crypto tests now run for real -- the suite has zero skips.
