"""Commit-Reveal: commit()/verify() round-trip and tamper detection (Sec. 5.3)."""

from police_thief.domain.crypto import audit_log, commit, verify


def test_verify_accepts_matching_reveal():
    commitment = commit(state="s1", move="N", intent="true")

    assert verify("s1", "N", "true", commitment.nonce, commitment.h_commit) is True


def test_verify_rejects_tampered_move():
    commitment = commit(state="s1", move="N", intent="true")

    # The revealed move doesn't match what was originally committed to.
    assert verify("s1", "S", "true", commitment.nonce, commitment.h_commit) is False


def test_verify_rejects_tampered_state():
    commitment = commit(state="s1", move="N", intent="true")
    assert verify("s2", "N", "true", commitment.nonce, commitment.h_commit) is False


def test_verify_rejects_tampered_intent():
    commitment = commit(state="s1", move="N", intent="true")
    assert verify("s1", "N", "false", commitment.nonce, commitment.h_commit) is False


def test_verify_rejects_wrong_nonce():
    commitment = commit(state="s1", move="N", intent="true")
    assert verify("s1", "N", "true", "wrong-nonce", commitment.h_commit) is False


def test_commit_nonce_is_unique_per_call():
    # Sec. 5.3: the Nonce must differ every time even for the identical
    # action, or the small move space becomes crackable by a dictionary
    # attack.
    first = commit(state="s1", move="N", intent="true")
    second = commit(state="s1", move="N", intent="true")
    assert first.nonce != second.nonce
    assert first.h_commit != second.h_commit


def test_audit_log_flags_valid_and_tampered_entries():
    good = commit(state="s1", move="N", intent="true")
    bad = commit(state="s2", move="S", intent="false")

    entries = [
        {"step": 0, "state": "s1", "move": "N", "intent": "true",
         "nonce": good.nonce, "h_commit": good.h_commit},
        {"step": 1, "state": "s2", "move": "N", "intent": "false",  # tampered: move changed after commit
         "nonce": bad.nonce, "h_commit": bad.h_commit},
    ]

    results = audit_log(entries)

    assert results == [(0, True), (1, False)]
