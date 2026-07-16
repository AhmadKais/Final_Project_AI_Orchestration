# Tunneling Setup (Stage 5)

> This stage is a deployment/config task, not new source code (spec Sec. 10.3.5). It genuinely cannot be completed autonomously in this environment: it needs (a) your own tunneling-tool account/authtoken, and (b) a second machine on a different network to prove NAT traversal actually works. Follow the steps below yourself; the code side (server binding to `0.0.0.0`) is already in place from Stage 2.

## 1. ngrok is already downloaded

`tools/ngrok` (v3.39.9) is pre-downloaded into this repo -- gitignored, since it's a third-party binary, not source. Verify it runs:

```bash
tools/ngrok version
```

Sign up at ngrok.com, grab your authtoken from the dashboard, then:

```bash
tools/ngrok config add-authtoken <your-token>
```

Without this step, `tools/ngrok http <port>` fails immediately with `ERR_NGROK_4018` ("This ngrok session is not authenticated") -- confirmed directly: as of ngrok v3, opening even a single free HTTP tunnel requires a signed-in account, not just the binary. Creating that account has to be you; it's tied to your email and is a real external signup, not something to do on your behalf.

## 2. Start your peer's FastMCP server (Stage 2 code, unchanged)

```bash
uv run python -m police_thief peer --role police   # or --role thief
```

This binds to `0.0.0.0:<my_port>` per `infra/mcp_server.py:run_server` -- already tunnel-ready, no code changes needed.

## 3. Open a tunnel to that port

```bash
tools/ngrok http <my_port>
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
| `receive_move` tool round-trips correctly | Create an ngrok account, get an authtoken |
| Server binds to a real host:port over HTTP (not just in-memory) | Run a peer on an actual second machine/network |
| Timeout handling on a slow/unresponsive opponent | Exchange tunnel URLs and confirm a real cross-network round trip |
| ngrok binary downloaded, verified runnable | Run `tools/ngrok config add-authtoken <token>` once |

## Status

Blocked on user action (ngrok account + a second machine) -- confirmed by actually running `tools/ngrok http` and hitting `ERR_NGROK_4018`, not just assumed. Not marked complete in `docs/TODO.md` -- see there for the honest status.
