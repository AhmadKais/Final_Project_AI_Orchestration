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

Not started. Deployment/config task, not a new source module.
