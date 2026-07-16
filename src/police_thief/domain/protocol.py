"""Wire-level message shapes exchanged over FastMCP tools (Sec. 2.3, 5.3).

Covers the Commit / Acknowledge / Reveal / Audit message envelope, and the
Capture Claim message. Kept separate from mcp_server/mcp_client (infra) so
the message schema can be unit-tested without a network.
"""

from __future__ import annotations

import hashlib
import json
import secrets
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


def _envelope_signature(msg_type: MessageType, payload: dict, *, step: int, role: str) -> str:
    """Integrity signature over the message envelope itself (type/payload/
    step/role) -- distinct from domain.crypto's H_commit, which protects
    specifically the (state, move, intent) triple. This one catches
    tampering with metadata like the step number or role, e.g. replaying
    an old message under a new step."""
    canonical = json.dumps(
        {"msg_type": msg_type.value, "payload": payload, "step": step, "role": role},
        sort_keys=True, separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def build_message(msg_type: MessageType, payload: dict, *, step: int, role: str) -> SignedMessage:
    signature = _envelope_signature(msg_type, payload, step=step, role=role)
    return SignedMessage(msg_type=msg_type, payload=payload, signature=signature, step=step, role=role)


def parse_message(raw: dict) -> SignedMessage:
    """Parse a raw dict received over FastMCP and verify its envelope
    signature. Raises ValueError on missing fields, an unknown msg_type, or
    a signature that doesn't match the content -- i.e. tampering."""
    required = {"msg_type", "payload", "signature", "step", "role"}
    missing = required - raw.keys()
    if missing:
        raise ValueError(f"Message missing required fields: {sorted(missing)}")

    msg_type = MessageType(raw["msg_type"])
    expected_signature = _envelope_signature(
        msg_type, raw["payload"], step=raw["step"], role=raw["role"]
    )
    if not secrets.compare_digest(raw["signature"], expected_signature):
        raise ValueError("Message signature does not match its content -- possible tampering")

    return SignedMessage(
        msg_type=msg_type, payload=raw["payload"], signature=raw["signature"],
        step=raw["step"], role=raw["role"],
    )
