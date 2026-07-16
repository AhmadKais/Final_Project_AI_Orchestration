# Stage 5 — Cloud Exposure and Tunneling

> Source: spec Sec. 10.3.5 (Table 3, row 5), Chapter 2 (extension). No new module — configuration/deployment only.

## Goal

Move from `localhost` to public addresses using a tunneling tool (ngrok, Localtonet), and connect agents running on remote computers. From this point the system is a genuine distributed system with real latency and disconnection risk.

## Scope

- Expose each peer's FastMCP server publicly via a tunnel.
- Update `config/<role>/game.toml`'s `[network] opponent_url` to the opponent's public tunnel URL.
- Verify NAT traversal works end-to-end against a peer on a different network.

## Out of scope

Cryptographic hardening — deliberately deferred to Stage 6, so a network fault is never confused with a cryptographic fault.

## Acceptance criteria (spec Sec. 10.4)

- An agent on a remote computer connects via ngrok and plays a full round against the local agent.

## Status

**Blocked on user action, not something I can complete autonomously.** This stage needs (a) a tunneling-tool account/authtoken belonging to you, and (b) a second machine on a different network to prove NAT traversal for real -- neither exists in this sandbox, and I won't create accounts on your behalf. The code side has been ready since Stage 2 (`infra/mcp_server.py:run_server` already binds to a real host:port, verified with an actual OS-level HTTP smoke test, not just in-memory). A step-by-step runbook is in [`docs/TUNNELING.md`](../TUNNELING.md) for when you're ready to run it yourself.
