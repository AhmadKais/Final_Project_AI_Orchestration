"""Gmail API reporting via OAuth 2.0, send-only scope (Appendix A, Sec. 9.3).

Sends the four mandatory JSON report types (declaration, configuration,
log, results) as attachments to rmisegal+uoh26finalgame@gmail.com. All
sends must pass through the Gatekeeper (infra/gatekeeper.py) first.

Requires credentials.json + token.json (both gitignored, never committed --
Appendix E rules 39-40).
"""

from __future__ import annotations

import base64
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_service(token_path: Path = Path("token.json"), credentials_path: Path = Path("credentials.json")):
    """Load/refresh OAuth credentials and build the Gmail API service.

    On first run (no token.json yet), runs the InstalledAppFlow consent
    flow using credentials_path and persists the resulting token so
    subsequent runs need no further interaction (Appendix A).
    """
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build

    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def send_report(service, to_addr: str, subject: str, json_path: Path) -> dict:
    """Attach and send one of the four mandatory JSON report files
    (declaration/configuration/log/results, Sec. 9.3.3)."""
    json_path = Path(json_path)
    message = MIMEMultipart()
    message["to"] = to_addr
    message["subject"] = subject
    message.attach(MIMEText(f"Automated report attached: {json_path.name}"))

    attachment = MIMEApplication(json_path.read_bytes(), _subtype="json")
    attachment.add_header("Content-Disposition", "attachment", filename=json_path.name)
    message.attach(attachment)

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return service.users().messages().send(userId="me", body={"raw": raw}).execute()
