"""Wire-level message shapes exchanged over FastMCP tools (Sec. 2.3, 5.3).

Covers the Commit / Acknowledge / Reveal / Audit message envelope, and the
Capture Claim message. Kept separate from mcp_server/mcp_client (infra) so
the message schema can be unit-tested without a network.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MessageType(str, Enum):
    COMMIT = "commit"
    ACKNOWLEDGE = "acknowledge"
    REVEAL = "reveal"
    FINAL_AUDIT = "final_audit"
    CAPTURE_CLAIM = "capture_claim"


@dataclass(frozen=True)
class SignedMessage:
    msg_type: MessageType
    payload: dict
    signature: str
    step: int
    role: str


def build_message(msg_type: MessageType, payload: dict, *, step: int, role: str) -> SignedMessage:
    raise NotImplementedError


def parse_message(raw: dict) -> SignedMessage:
    raise NotImplementedError
