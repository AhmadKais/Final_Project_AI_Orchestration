"""Client engine: calls the opponent's FastMCP server tools over the network
(Table 1). Every request carries an Expiry Deadline (Sec. 8.4.1) -- a missed
deadline is a failure, never an invitation to keep waiting.

Stage 2 scope only (Sec. 10.3.2): `send_move` exchanges a plain geometric
move (role/move/step). Stage 6 layers Commit-Reveal (commit/ack/reveal/
final-audit/capture-claim) on top of this same transport.
"""

from __future__ import annotations

from fastmcp import Client
from fastmcp.exceptions import McpError

from police_thief.domain.board import Move

# MCP error code FastMCP raises when a call_tool() deadline is exceeded.
_TIMEOUT_ERROR_CODE = 408


class OpponentClient:
    """Thin wrapper around a FastMCP client bound to the opponent.

    `opponent_url` is normally a public URL string (e.g.
    "http://127.0.0.1:8801/mcp"), but can also be an in-process `FastMCP`
    instance -- fastmcp.Client accepts either, which is what lets tests
    exercise this class without opening a real socket.
    """

    def __init__(self, opponent_url, *, response_timeout_sec: float):
        self.opponent_url = opponent_url
        self.response_timeout_sec = response_timeout_sec

    async def send_move(self, *, role: str, move: Move | str, step: int) -> dict:
        """Call the opponent's `receive_move` tool with a plain geometric
        move. Raises TimeoutError (not McpError) if no response arrives
        within `response_timeout_sec`, so callers can treat a timeout as
        the deliberate failure mode Sec. 8.4.1 requires -- never silently
        keep waiting.
        """
        move_value = move.value if isinstance(move, Move) else move
        async with Client(self.opponent_url) as client:
            try:
                result = await client.call_tool(
                    "receive_move",
                    {"role": role, "move": move_value, "step": step},
                    timeout=self.response_timeout_sec,
                )
            except McpError as exc:
                if exc.error.code == _TIMEOUT_ERROR_CODE:
                    raise TimeoutError(
                        f"receive_move to {self.opponent_url!r} timed out "
                        f"after {self.response_timeout_sec}s"
                    ) from exc
                raise
            return result.data

    # Stage 6 adds send_commit / send_ack / send_reveal / send_final_audit /
    # send_capture_claim here once Commit-Reveal (Sec. 5.3) is implemented.
