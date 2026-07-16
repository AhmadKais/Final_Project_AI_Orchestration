# Tunneling Setup (Stage 5)

> This stage is a deployment/config task, not new source code (spec Sec. 10.3.5). It genuinely cannot be completed autonomously in this environment: it needs (a) your own tunneling-tool account/authtoken, and (b) a second machine on a different network to prove NAT traversal actually works. Follow the steps below yourself; the code side (server binding to `0.0.0.0`) is already in place from Stage 2.

## 1. ngrok is downloaded and authenticated

`tools/ngrok` (v3.39.9) is pre-downloaded into this repo -- gitignored, since it's a third-party binary, not source. The authtoken lives in `tools/ngrok.yml` (a project-local config file, not ngrok's usual `~/.config/ngrok/ngrok.yml` default -- kept inside the project on purpose, and gitignored like `credentials.json`/`token.json`), so every ngrok invocation needs `--config tools/ngrok.yml`:

```bash
tools/ngrok version
tools/ngrok config check --config tools/ngrok.yml   # confirms the authtoken is valid
```

**Verified for real, not just configured:** started the project's actual FastMCP server on `127.0.0.1:8901`, opened a real tunnel (`tools/ngrok http 8901 --config tools/ngrok.yml`), and connected an `OpponentClient` through the resulting public `https://*.ngrok-free.app/mcp` URL -- a real move round-tripped correctly over the actual public internet, not just localhost. Everything was killed and cleaned up afterward; nothing was left running.

Without a valid authtoken, `tools/ngrok http <port>` fails immediately with `ERR_NGROK_4018` ("This ngrok session is not authenticated") -- confirmed directly before the token existed, and confirmed fixed after.

## 2. Start your peer's FastMCP server (Stage 2 code, unchanged)

```bash
uv run python -m police_thief peer --role police   # or --role thief
```

This binds to `0.0.0.0:<my_port>` per `infra/mcp_server.py:run_server` -- already tunnel-ready, no code changes needed.

## 3. Open a tunnel to that port

```bash
tools/ngrok http <my_port> --config tools/ngrok.yml
```

ngrok prints a public URL like `https://abcd-1-2-3-4.ngrok-free.app`. Your peer's actual MCP endpoint is that URL + `/mcp`.

## 4. Exchange public URLs with your opponent

Each side sends the other their tunnel URL (out of band -- email, chat, whatever). Each side then updates **their own** `config/<role>/game.toml`:

```toml
[network]
opponent_url = "https://abcd-1-2-3-4.ngrok-free.app/mcp"   # THEIR public URL, not yours
```

## 5. Verify NAT traversal end-to-end

From the opponent's machine (a genuinely different network -- this is the point):

```bash
uv run python -m police_thief peer --role thief   # while you run --role police
```

**Acceptance criterion (spec Sec. 10.4):** a move sent by the remote peer arrives at your local peer, and vice versa -- i.e. the exact Stage 2 round trip (`tests/test_mcp_infra.py`'s scenario), just now over the public internet through two separate tunnels instead of `localhost`.

## What's already proven vs. what needs you

| Already proven / done | Needs you to do |
|---|---|
| `receive_move` tool round-trips correctly | Nothing -- done |
| Server binds to a real host:port over HTTP (not just in-memory) | Nothing -- done |
| ngrok account created, authtoken configured and validated | Nothing -- done |
| A real move round-tripped through an actual public ngrok tunnel | Nothing -- done |
| Timeout handling on a slow/unresponsive opponent | Nothing -- done |
| NAT traversal across two genuinely different networks | Run a peer on an actual second machine and exchange tunnel URLs (steps 2-5 above) -- this is the one piece that needs a second physical machine, which no amount of setup on this one can substitute for |

## Status

The tunneling *infrastructure* is fully working and verified end-to-end: ngrok is authenticated, and a real request round-tripped through a real public tunnel back to this project's own server. What's left is exclusively the multi-machine step (5) -- proving NAT traversal needs an actual second computer on a different network, which is a hardware/logistics requirement, not a setup step.
