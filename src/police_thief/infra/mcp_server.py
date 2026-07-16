"""This peer's own FastMCP server: exposes tools the opponent calls (Sec. 2.3.2).

Each agent runs its own server instance (local truth) and is simultaneously
a client of the opponent's server (infra/mcp_client.py) -- full symmetry,
no central server.

`receive_move` is the Stage 2 plain-geometric-move tool (role/move/step, no
crypto). Stage 6 layers the full Commit-Reveal conversation on top of the
same transport: `receive_commit` / `receive_ack` / `receive_reveal` /
`receive_final_audit` / `receive_capture_claim` (Sec. 5.3) -- each message
kind gets its own queue so the Orchestrator can await exactly the kind it
needs at each turn phase without cross-kind ordering interference.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from fastmcp import FastMCP

from police_thief.domain.board import Move
from police_thief.domain.protocol import decode_move

_LEGAL_MOVE_VALUES = {m.value for m in Move}
_LEGAL_ROLES = {"police", "thief"}


@dataclass
class MoveMailbox:
    """Async-safe, per-message-kind inboxes for everything this server has
    received. `put`/`get`/`empty()` are Stage 2 aliases for the `moves`
    queue specifically; Stage 6 message kinds each get their own queue."""

    moves: asyncio.Queue = field(default_factory=asyncio.Queue)
    commits: asyncio.Queue = field(default_factory=asyncio.Queue)
    acks: asyncio.Queue = field(default_factory=asyncio.Queue)
    reveals: asyncio.Queue = field(default_factory=asyncio.Queue)
    final_audits: asyncio.Queue = field(default_factory=asyncio.Queue)
    capture_claims: asyncio.Queue = field(default_factory=asyncio.Queue)

    async def put(self, message: dict) -> None:
        await self.moves.put(message)

    async def get(self) -> dict:
        return await self.moves.get()

    def empty(self) -> bool:
        return self.moves.empty()


def build_server(name: str, mailbox: MoveMailbox) -> FastMCP:
    """Construct the FastMCP instance and register the tool surface.
    Invalid roles/moves are rejected in the tool's return value
    (`accepted: False`), mirroring the book's own minimal-server example
    (Sec. 2.3.2) rather than raising through the MCP transport.
    """
    mcp = FastMCP(name)

    @mcp.tool
    async def receive_move(role: str, move: str, step: int) -> dict:
        """Receive a plain geometric move from the opponent (Table 1)."""
        if role not in _LEGAL_ROLES:
            return {"accepted": False, "error": f"unknown role {role!r}"}
        if move not in _LEGAL_MOVE_VALUES:
            return {"accepted": False, "error": f"unknown move {move!r}"}
        await mailbox.moves.put({"role": role, "move": move, "step": step})
        return {"accepted": True, "role": role, "move": move, "step": step}

    @mcp.tool
    async def receive_commit(role: str, step: int, h_commit: str) -> dict:
        """Receive a sealed commitment -- content unknown until Reveal (Sec. 5.3.1)."""
        await mailbox.commits.put({"role": role, "step": step, "h_commit": h_commit})
        return {"accepted": True}

    @mcp.tool
    async def receive_ack(role: str, step: int) -> dict:
        """Acknowledge the opponent's commitment is locked in (Sec. 5.3.2)."""
        await mailbox.acks.put({"role": role, "step": step})
        return {"accepted": True}

    @mcp.tool
    async def receive_reveal(role: str, step: int, move: str, hint: str, intent: str) -> dict:
        """Receive the revealed move + verbal hint (Nonce still hidden, Sec.
        5.3.2). `move` may be a plain direction/STAY, or a STAY with a
        barrier placement folded in (domain.protocol.encode_move) -- only
        the format is checked here; whether the barrier itself is legal is
        the Orchestrator's job, same as for the move."""
        try:
            base_move, _ = decode_move(move)
        except ValueError:
            return {"accepted": False, "error": f"malformed move {move!r}"}
        if base_move.value not in _LEGAL_MOVE_VALUES:
            return {"accepted": False, "error": f"unknown move {move!r}"}
        await mailbox.reveals.put(
            {"role": role, "step": step, "move": move, "hint": hint, "intent": intent}
        )
        return {"accepted": True}

    @mcp.tool
    async def receive_final_audit(role: str, nonces: list[str]) -> dict:
        """Receive all Nonces at end-of-game for the mutual log audit (Sec. 5.4)."""
        await mailbox.final_audits.put({"role": role, "nonces": nonces})
        return {"accepted": True}

    @mcp.tool
    async def receive_capture_claim(role: str, claimed: bool) -> dict:
        """Receive a Capture Claim; the Robber is under cryptographic
        obligation to respond truthfully once revealed (Sec. 3.5)."""
        await mailbox.capture_claims.put({"role": role, "claimed": claimed})
        return {"accepted": True}

    return mcp


def run_server(mcp: FastMCP, *, host: str, port: int) -> None:
    """Bind so a tunnel (ngrok/Localtonet) can expose it publicly for
    league play (Sec. 2.4, Stage 5). Blocking call -- run in its own
    process, per the mandatory Cop/Robber process-separation rule
    (Sec. 2.4.2)."""
    mcp.run(transport="http", host=host, port=port)
