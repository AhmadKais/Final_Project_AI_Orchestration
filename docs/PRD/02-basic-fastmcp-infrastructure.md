# Stage 2 — Basic FastMCP Infrastructure

> Source: spec Sec. 10.3.2 (Table 3, row 2), Chapter 2. Implements: `infra/mcp_server.py`, `infra/mcp_client.py`.

## Goal

Split the two agents into separate processes and prove the pipe works — a message sent from one agent arrives at the other — before it's loaded with complex content.

## Scope

- Each agent runs its own FastMCP server (`@mcp.tool`) over `localhost`, exposing endpoints to receive geometric moves.
- Each agent is simultaneously a client calling the opponent's server.
- Agents still speak **only in numeric coordinates** — no natural language, no scent, no crypto yet.
- Mandatory process/config separation: `config/police/` vs `config/thief/`, no shared memory or shared Python state between roles (Sec. 2.4.2 — violating this is an automatic disqualification, not just a bug).

## Out of scope (later stages)

Public tunneling (Stage 5), strategy (Stage 3), language/scent (Stage 4), Commit-Reveal (Stage 6).

## Acceptance criteria (spec Sec. 10.4)

- A geometric message sent from Agent A over localhost is received and correctly decoded by Agent B.

## Status

**Done.** Implemented in `src/police_thief/infra/mcp_{server,client}.py`, covered by `tests/test_mcp_infra.py` (5 tests: round trip, `Move` enum acceptance, invalid role/move rejection, timeout-not-a-hang), plus a one-off manual smoke test running the server as a real OS process bound to `127.0.0.1` and connecting a real HTTP client against it -- confirms `run_server`'s host/port binding works, not just the in-process test transport.
