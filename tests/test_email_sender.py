"""Gmail send-only reporting (Sec. 9.3, Appendix A). No real credentials or
network access is used or required -- the Gmail service is mocked
throughout, which is the standard way to test this kind of integration
code. Real end-to-end sending needs your own credentials.json/token.json
(Appendix A) and is out of scope for an automated test suite.
"""

import base64
import email
import json
from unittest.mock import MagicMock

from police_thief.infra.email_sender import SCOPES, send_report


def test_scopes_is_send_only():
    # Least-privilege: never request read/modify access to the mailbox.
    assert SCOPES == ["https://www.googleapis.com/auth/gmail.send"]


def test_send_report_calls_gmail_send_with_correct_user_id(tmp_path):
    report_path = tmp_path / "result_game1.json"
    report_path.write_text(json.dumps({"cop_score": 20, "thief_score": 5}))

    service = MagicMock()
    service.users.return_value.messages.return_value.send.return_value.execute.return_value = {
        "id": "msg123"
    }

    result = send_report(service, "grader@example.com", "Game result", report_path)

    assert result == {"id": "msg123"}
    service.users.return_value.messages.return_value.send.assert_called_once()
    _, kwargs = service.users.return_value.messages.return_value.send.call_args
    assert kwargs["userId"] == "me"
    assert "raw" in kwargs["body"]


def test_send_report_attaches_the_json_file_content(tmp_path):
    report_path = tmp_path / "result_game1.json"
    payload = {"cop_score": 20, "thief_score": 5}
    report_path.write_text(json.dumps(payload))

    service = MagicMock()
    send_report(service, "grader@example.com", "Game result", report_path)

    _, kwargs = service.users.return_value.messages.return_value.send.call_args
    raw_message = base64.urlsafe_b64decode(kwargs["body"]["raw"]).decode("utf-8", errors="ignore")

    assert "result_game1.json" in raw_message
    assert "grader@example.com" in raw_message
    assert "Game result" in raw_message


def test_send_report_encodes_attachment_bytes_faithfully(tmp_path):
    report_path = tmp_path / "log_game1.json"
    original_bytes = json.dumps({"steps": [1, 2, 3]}).encode("utf-8")
    report_path.write_bytes(original_bytes)

    service = MagicMock()
    send_report(service, "grader@example.com", "Log", report_path)

    _, kwargs = service.users.return_value.messages.return_value.send.call_args
    raw_message_bytes = base64.urlsafe_b64decode(kwargs["body"]["raw"])
    parsed = email.message_from_bytes(raw_message_bytes)

    attachment_part = next(
        part for part in parsed.walk() if part.get_filename() == "log_game1.json"
    )
    assert attachment_part.get_payload(decode=True) == original_bytes
