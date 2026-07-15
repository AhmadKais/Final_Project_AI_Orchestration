"""Gmail API reporting via OAuth 2.0, send-only scope (Appendix A, Sec. 9.3).

Sends the four mandatory JSON report types (declaration, configuration,
log, results) as attachments to rmisegal+uoh26finalgame@gmail.com. All
sends must pass through the Gatekeeper (infra/gatekeeper.py) first.

Requires credentials.json + token.json (both gitignored, never committed --
Appendix E rules 39-40).
"""

from __future__ import annotations

from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_service(token_path: Path = Path("token.json")):
    """Load/refresh OAuth credentials and build the Gmail API service."""
    raise NotImplementedError


def send_report(service, to_addr: str, subject: str, json_path: Path) -> dict:
    """Attach and send one of the four mandatory JSON report files."""
    raise NotImplementedError
