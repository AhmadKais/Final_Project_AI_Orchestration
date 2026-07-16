# Development Plan

Mandatory repository content per spec Appendix C / Appendix E rule 50 (README, `config/`, PRD files, PLAN, TODO).

## Approach

Build in the seven layered stages defined in `docs/PRD/`, in order, per spec Chapter 10. Each stage must run end-to-end ("the behavior was observed", not just "the code was written" — Sec. 10.4) before the next stage starts. Skipping ahead (e.g. Stage 2 → Stage 6) turns every future bug into an unsolvable multi-variable investigation, per the spec's explicit warning.

| # | Stage | PRD |
|---|---|---|
| 1 | Base Logic (board, movement, barriers, capture, scoring) | [01-base-logic.md](PRD/01-base-logic.md) |
| 2 | Basic FastMCP Infrastructure (localhost, numeric coords) | [02-basic-fastmcp-infrastructure.md](PRD/02-basic-fastmcp-infrastructure.md) |
| 3 | "Blind" Strategy Module (full-information decision core) | [03-blind-strategy-module.md](PRD/03-blind-strategy-module.md) |
| 4 | Language and Scent Integration (uncertainty, belief, LLM bluffing) | [04-language-and-scent-integration.md](PRD/04-language-and-scent-integration.md) |
| 5 | Cloud Exposure and Tunneling (public network) | [05-cloud-exposure-and-tunneling.md](PRD/05-cloud-exposure-and-tunneling.md) |
| 6 | Security and Cryptography (Commit-Reveal, Step-0) | [06-security-and-cryptography.md](PRD/06-security-and-cryptography.md) |
| 7 | Reporting and Visualization Shell (Gmail, GUI, Replay) | [07-reporting-and-visualization-shell.md](PRD/07-reporting-and-visualization-shell.md) |
| 8 | Orchestrator Integration (wiring 1-7 into a runnable game loop) | [08-orchestrator-integration.md](PRD/08-orchestrator-integration.md) |

## Status: all 8 stages implemented

Stages 1-4 and 6-8 are done and tested (146 tests passing, 1 skipped for lack of a display/`tkinter` in this sandbox). Stage 5 (Cloud Exposure and Tunneling) is genuinely blocked on user action -- it needs your own ngrok/Localtonet account and a second machine on a different network; see [`docs/TUNNELING.md`](../TUNNELING.md). Stage 8 is a courtesy addition beyond the book's own 7 numbered stages (Chapter 8's Orchestrator pattern is woven through all of them, not assigned its own row in Table 3) -- it's what proves Stages 1-7 actually work together, not just in isolation.

## Milestone discipline

For each stage, define a binary criterion before moving on — "does the behavior actually run end-to-end", not "is the code written." Acceptance criteria for each stage are listed in its PRD file (mirrors spec Sec. 10.4).

## Non-negotiables regardless of stage (see Appendix E for the full list)

- Cop and Robber code run as two fully separate processes; never share memory or import live state between them.
- The move decision is always algorithmic; the LLM only ever produces the verbal bluff layer (unless both teams explicitly agree to the Sec. 6.5 exception).
- Every quantitative rule comes from `config/game.json` (Appendix F is the single source of truth) — never hardcode a number the book expresses as a bracketed `[parameter]`.

## Submission target (not yet applicable at scaffold stage)

Per spec Appendix C, final submission is **two separate GitHub repositories** (Cop, Robber) with a cross-linked README in each. This working tree is a single development repo by design (matches the Appendix D reference layout); splitting into two repos is a later packaging step, not a Stage-1 concern.
