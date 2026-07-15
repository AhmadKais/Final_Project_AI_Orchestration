"""This peer's own FastMCP server: exposes tools the opponent calls (Sec. 2.3.2).

Each agent runs its own server instance (local truth) and is simultaneously
a client of the opponent's server (infra/mcp_client.py) -- full symmetry,
no central server.

Stage 2 scope only (Sec. 10.3.2): the `receive_move` tool carries a plain
geometric move (role/move/step) with no cryptographic signature, no scent,
no natural language. Commit-Reveal wraps this same conversation in Stage 6
(Sec. 5.3); the tool surface will grow then, not change shape now.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from fastmcp import FastMCP

from police_thief.domain.board import Move

_LEGAL_MOVE_VALUES = {m.value for m in Move}
_LEGAL_ROLES = {"police", "thief"}


@dataclass
class MoveMailbox:
    """Async-safe inbox for moves this server has received. The run loop
    (Stage 8's Orchestrator, not yet built) will `await get()` from it;
    for now tests and manual runs consume it directly."""

    _queue: asyncio.Queue = field(default_factory=asyncio.Queue)

    async def put(self, message: dict) -> None:
        await self._queue.put(message)

    async def get(self) -> dict:
        return await self._queue.get()

    def empty(self) -> bool:
        return self._queue.empty()


def build_server(name: str, mailbox: MoveMailbox) -> FastMCP:
    """Construct the FastMCP instance and register the Stage-2 `receive_move`
    tool. Invalid roles/moves are rejected in the tool's return value
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
        await mailbox.put({"role": role, "move": move, "step": step})
        return {"accepted": True, "role": role, "move": move, "step": step}

    return mcp


def run_server(mcp: FastMCP, *, host: str, port: int) -> None:
    """Bind so a tunnel (ngrok/Localtonet) can expose it publicly for
    league play (Sec. 2.4, Stage 5). Blocking call -- run in its own
    process, per the mandatory Cop/Robber process-separation rule
    (Sec. 2.4.2)."""
    mcp.run(transport="http", host=host, port=port)
