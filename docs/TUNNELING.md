# Tunneling Setup (Stage 5)

> This stage is a deployment/config task, not new source code (spec Sec. 10.3.5). It genuinely cannot be completed autonomously in this environment: it needs (a) your own tunneling-tool account/authtoken, and (b) a second machine on a different network to prove NAT traversal actually works. Follow the steps below yourself; the code side (server binding to `0.0.0.0`) is already in place from Stage 2.

## 1. Install a tunneling tool

Pick one (ngrok is the spec's primary example):

```bash
# ngrok (https://ngrok.com/download)
curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list
sudo apt update && sudo apt install ngrok
```

Sign up at ngrok.com, grab your authtoken from the dashboard, then:

```bash
ngrok config add-authtoken <your-token>
```

## 2. Start your peer's FastMCP server (Stage 2 code, unchanged)

```bash
uv run python -m police_thief peer --role police   # or --role thief
```

This binds to `0.0.0.0:<my_port>` per `infra/mcp_server.py:run_server` -- already tunnel-ready, no code changes needed.

## 3. Open a tunnel to that port

```bash
ngrok http <my_port>
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

| Already proven (Stage 2) | Needs you to do |
|---|---|
| `receive_move` tool round-trips correctly | Install ngrok, create an account, get an authtoken |
| Server binds to a real host:port over HTTP (not just in-memory) | Run a peer on an actual second machine/network |
| Timeout handling on a slow/unresponsive opponent | Exchange tunnel URLs and confirm a real cross-network round trip |

## Status

Blocked on user action (tunneling account + a second machine). Not marked complete in `docs/TODO.md` -- see there for the honest status.
