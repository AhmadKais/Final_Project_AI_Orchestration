"""Wire-level message envelope: build_message/parse_message signing and
tamper detection (Sec. 2.3, 5.3)."""

import pytest

from police_thief.domain.protocol import MessageType, build_message, parse_message


def test_build_then_parse_round_trips():
    message = build_message(MessageType.COMMIT, {"h_commit": "abc123"}, step=1, role="police")

    parsed = parse_message({
        "msg_type": message.msg_type.value,
        "payload": message.payload,
        "signature": message.signature,
        "step": message.step,
        "role": message.role,
    })

    assert parsed.msg_type == MessageType.COMMIT
    assert parsed.payload == {"h_commit": "abc123"}
    assert parsed.step == 1
    assert parsed.role == "police"


def test_parse_rejects_tampered_payload():
    message = build_message(MessageType.REVEAL, {"move": "N"}, step=2, role="thief")
    raw = {
        "msg_type": message.msg_type.value,
        "payload": {"move": "S"},  # tampered after signing
        "signature": message.signature,
        "step": message.step,
        "role": message.role,
    }

    with pytest.raises(ValueError):
        parse_message(raw)


def test_parse_rejects_tampered_step():
    message = build_message(MessageType.REVEAL, {"move": "N"}, step=2, role="thief")
    raw = {
        "msg_type": message.msg_type.value,
        "payload": message.payload,
        "signature": message.signature,
        "step": 99,  # tampered: replay under a different step number
        "role": message.role,
    }

    with pytest.raises(ValueError):
        parse_message(raw)


def test_parse_rejects_missing_fields():
    with pytest.raises(ValueError):
        parse_message({"msg_type": "commit", "payload": {}})


def test_parse_rejects_unknown_msg_type():
    message = build_message(MessageType.ACKNOWLEDGE, {}, step=0, role="police")
    raw = {
        "msg_type": "not_a_real_type",
        "payload": message.payload,
        "signature": message.signature,
        "step": message.step,
        "role": message.role,
    }

    with pytest.raises(ValueError):
        parse_message(raw)


def test_different_steps_produce_different_signatures():
    a = build_message(MessageType.COMMIT, {"x": 1}, step=1, role="police")
    b = build_message(MessageType.COMMIT, {"x": 1}, step=2, role="police")
    assert a.signature != b.signature
