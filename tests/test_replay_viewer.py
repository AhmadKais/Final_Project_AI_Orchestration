"""Cryptographic replay/verification engine: Verified OK vs TAMPERED (Sec. 7.4-7.5)."""

import json

import pytest

from police_thief.domain.crypto import commit
from police_thief.interface.replay_viewer import ReplayViewer


def _write_log(tmp_path, entries):
    log_path = tmp_path / "log.json"
    log_path.write_text(json.dumps(entries))
    return log_path


def _make_entry(step, role, state, move, intent):
    commitment = commit(state, move, intent)
    return {
        "step": step, "role": role, "state": state, "move": move,
        "intent": intent, "nonce": commitment.nonce, "h_commit": commitment.h_commit,
    }


def test_load_bare_list(tmp_path):
    entries = [_make_entry(0, "police", "s0", "N", "true")]
    log_path = _write_log(tmp_path, entries)

    loaded = ReplayViewer(log_path).load()

    assert loaded == entries


def test_load_wrapped_entries(tmp_path):
    entries = [_make_entry(0, "police", "s0", "N", "true")]
    log_path = tmp_path / "log.json"
    log_path.write_text(json.dumps({"game_uid": "abc", "entries": entries}))

    loaded = ReplayViewer(log_path).load()

    assert loaded == entries


def test_load_rejects_non_list_non_wrapper(tmp_path):
    log_path = tmp_path / "log.json"
    log_path.write_text(json.dumps("not a log"))

    with pytest.raises(ValueError):
        ReplayViewer(log_path).load()


def test_verify_all_true_for_untampered_log(tmp_path):
    entries = [
        _make_entry(0, "police", "s0", "N", "true"),
        _make_entry(1, "thief", "s1", "S", "false"),
    ]
    log_path = _write_log(tmp_path, entries)

    assert ReplayViewer(log_path).verify_all() is True


def test_verify_all_false_when_one_entry_tampered(tmp_path):
    entries = [
        _make_entry(0, "police", "s0", "N", "true"),
        _make_entry(1, "thief", "s1", "S", "false"),
    ]
    entries[1]["move"] = "N"  # tampered after commit
    log_path = _write_log(tmp_path, entries)

    assert ReplayViewer(log_path).verify_all() is False


def test_step_through_prints_verified_ok(tmp_path, capsys):
    entries = [_make_entry(0, "police", "s0", "N", "true")]
    log_path = _write_log(tmp_path, entries)

    ReplayViewer(log_path).step_through()

    out = capsys.readouterr().out
    assert "Verified OK" in out
    assert "TAMPERED" not in out


def test_step_through_prints_tampered_for_forged_entry(tmp_path, capsys):
    entries = [_make_entry(0, "police", "s0", "N", "true")]
    entries[0]["h_commit"] = "0" * 64  # forged
    log_path = _write_log(tmp_path, entries)

    ReplayViewer(log_path).step_through()

    out = capsys.readouterr().out
    assert "TAMPERED" in out
